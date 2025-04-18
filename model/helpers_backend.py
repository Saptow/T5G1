import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset
import pandas as pd
import numpy as np
from model.AGCRN.lib.dataloader import normalize_dataset
from sklearn.preprocessing import MinMaxScaler
from model.agcrn_model import AGCRNFinal

#imports from NLP side
import pycountry
import trafilatura
import json
import dateparser
import re
import requests
from langdetect import detect
from transformers import AutoTokenizer, AutoConfig
from itertools import combinations
from datetime import datetime
from trafilatura.settings import DEFAULT_CONFIG
from copy import deepcopy
import torch.nn.functional as F
from transformers import (
    AutoModelForSequenceClassification,
    PreTrainedModel
)
from transformers.modeling_outputs import SequenceClassifierOutput


## defining variables
num_countries=17
num_country_pairs=num_countries*(num_countries-1) 
num_sectors=8 # 8 sectors

class Args:
    def __init__(self):
        # Model structure
        self.num_nodes = num_country_pairs  
        self.input_dim = num_sectors+1    # e.g. sectorial export volume + composite
        self.rnn_units = 120
        self.output_dim = num_sectors   # e.g., predict only the sectorial export volume
        self.horizon = 3      # forecast 3 steps ahead
        self.num_layers = 2
        self.cheb_k = 2
        self.embed_dim = 14
        self.default_graph = True  
        self.log_dir = './logs/'
        self.debug = False
        self.model='AGCRN'
        self.normaliser = 'max11'
        self.device='cpu'
        self.batch_size=4 
        self.mode='train'
        # Training
        self.seed=10
        self.loss_func= 'mse'
        self.epochs = 50
        self.lr_init = 0.005718209917007313
        self.lr_decay = True
        self.lr_decay_step = '5,20,40,70'
        self.lr_decay_rate = 0.27126698303010943
        self.early_stop = True
        self.early_stop_patience = 5
        self.teacher_forcing = True
        self.tf_decay_steps = 20
        self.real_value = False
        self.grad_norm = True
        self.max_grad_norm = 5
        self.weight_decay=1.0830728769764218e-06

        # Testing
        self.mae_thresh=None
        self.mape_thresh=0.

        #Logging
        self.log_step = 20
        self.plot=True

    def set_args(self, **kwargs):
        """
        Update attributes of Args dynamically based on the kwargs.
        If a key doesn't match an existing attribute, a warning is printed.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: '{key}' is not a recognized attribute of the Args class.")

########################################################
####################### NLP MODEL ######################
########################################################
class DebertaForRegression(PreTrainedModel):
    """
    Outputs a scalar tone score in [-1, 1] by taking the expected value of
    the 3‑class sentiment probabilities:  (-1, 0, +1) · softmax(logits).
    """
    def __init__(self, config):
        super().__init__(config)
        self.classifier = AutoModelForSequenceClassification.from_config(
            config
        )
        self.register_buffer("value_map", torch.tensor([-1.0, 0.0, 1.0]))

        self.loss_fn = nn.MSELoss()

    def forward(self, input_ids, attention_mask=None, labels=None, num_items_in_batch: int | None = None,  **kwargs ):
        out = self.classifier(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **kwargs
        )
        logits = out.logits                      # (B, 3)
        probs  = F.softmax(logits, dim=-1)       # (B, 3)

        # Expected value: (B, 3) · (3,)  → (B,)
        tone   = (probs * self.value_map).sum(dim=-1)

        loss = None
        if labels is not None:
            loss = self.loss_fn(tone, labels.float())

        return SequenceClassifierOutput(
            loss   = loss,          # scalar or None
            logits = tone,          # (B,) continuous in [-1, 1]
            hidden_states = out.hidden_states,
            attentions    = out.attentions,
        )

def process_article_for_sentiment_analysis(url, debug=False):
    """
    Unified function that:
    1. Extracts article content and publish date from a URL
    2. Cleans and preprocesses the text
    3. Identifies country pairs in the text
    4. Predicts sentiment scores for each country pair
    5. Returns both the sentiment scores and publication year

    Args:
        url (str): URL of the article to analyze
        model_path (str): Path to the model on Hugging Face
        debug (bool): Whether to print debug information

    Returns:
            - sentiment_scores (dict): Dictionary of country pairs and their sentiment scores
            - publication_year (int): Year of publication of the article
    """
    # Step 1: Define unwanted keywords for text cleaning
    unwanted_keywords = [
        "disclaimer", "terms and conditions", "for more information",
        "privacy policy", "cookies", "contact us", "cookie policy",
        "FAQ", "unsubscribe", "user agreement", "site policy",
        "sign up", "stay updated"
    ]

    # Step 2: Set up country normalization
    countries_to_keep = {
        'CHN', 'MYS', 'USA', 'HKG', 'IDN', 'KOR', 'JPN', 'THA', 'AUS', 'VNM',
        'IND', 'PHL', 'DEU', 'FRA', 'CHE', 'NLD', 'SGP'
    }

    # Build name-to-ISO3 mapping
    name_to_iso3 = {}
    for country in pycountry.countries:
        iso3 = country.alpha_3
        if iso3 not in countries_to_keep:
            continue
        for key in ["name", "official_name", "common_name"]:
            val = getattr(country, key, None)
            if val:
                name_to_iso3[val.lower()] = iso3
                #convert to lower case to ensure case insensitive

    # Manual aliases for informal country names (from Kaggle dataset "Country Aliases - List of Alternative Country Names").
    # Dropped outdated entries and added a few new ones.
    manual_aliases = {'mainland china': 'CHN',
                      'federation of malaysia': 'MYS',
                      'united states': 'USA',
                      'america': 'USA',
                      'the states': 'USA',
                      'u.s.': 'USA'}


    name_to_iso3.update({k.lower(): v for k, v in manual_aliases.items()})

    # Trading bloc aliases (top 10 global trade blocs in 2022-23)
    trading_bloc_aliases = {
        "apec": ["CHN", "MYS", "USA", "HKG", "IDN", "KOR", "JPN", "THA", "AUS", "VNM", "PHL", "SGP"],
        "eu": ["DEU", "FRA", "NLD"],
        "brics": ["CHN", "IND"],
        "nafta": ["USA"],
        "usmca": ["USA"],
        "asean": ["MYS", "IDN", "SGP", "THA", "VNM", "PHL"],
        "saarc": ["IND"],
    }

    # UN M49 region mapping
    un_region_mapping = {
        "eastern asia": ["CHN", "HKG", "JPN", "KOR"],
        "south-eastern asia": ["MYS", "IDN", "THA", "VNM", "PHL", "SGP"],
        "southern asia": ["IND"],
        "western europe": ["DEU", "FRA", "CHE", "NLD"],
        "oceania": ["AUS"],
        "northern america": ["USA"]
    }

    # Step 3: Initialize model


    # Define the model and tokenizer paths
    model_path = "ML2105/deberta-geopolitical-sentiment"


    # Load the tokenizer using the specific DebertaV2Tokenizer class that worked
    from transformers import DebertaV2Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Load the model config from the model path
    config = AutoConfig.from_pretrained(model_path)
    config.architectures = ["DebertaForRegression"]

    # Load the model from the checkpoint
    model = DebertaForRegression.from_pretrained(model_path, trust_remote_code=True, use_safetensors=True, config=config) 

    # Step 4: Define helper functions

    # Function to load EasyList (ad-blocking) rules
    def load_easylist_rules():
        """
        Loads EasyList rules from the provided URL and parses the rules into a list.
        """
        url = "https://easylist.to/easylist/easylist.txt"
        response = requests.get(url)

        if response.status_code == 200:
            return response.text.splitlines()  # Split the response into a list of lines
        else:
            print("Error: Could not retrieve EasyList.")
            return []

    # Function to remove ad-related content based on EasyList rules
    def remove_ad_content(content, easylist_rules):
        """
        Removes ad-related content from the extracted content using EasyList rules.
        """
        for rule in easylist_rules:
            if rule.startswith('||'):  # Domain-based ad blocking rule
                ad_domain = rule[2:]
                content = re.sub(r'https?://(?:[a-zA-Z0-9-]+\.)?' + re.escape(ad_domain), '', content)

        return content

    def remove_unwanted_content(content, unwanted_keywords):
        """
        Removes the sentence containing the first occurrence of any unwanted keywords,
        removes everything after the ellipsis ("..."), and everything after the unwanted keyword.
        Also removes everything after "Related:".
        """
        # Remove unwanted backslashes
        content = content.replace("\\", "")

        # This matches the sentence that contains the unwanted keyword and everything after it
        pattern = r"([^.]*\b(?:{})\b[^.]*\.).*".format("|".join(re.escape(keyword) for keyword in unwanted_keywords))

        # Substitute the sentence containing the unwanted keyword and everything after it with an empty string
        content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        # Remove everything after "Related:" or "related content:" (case-insensitive)
        content = re.sub(r"([^.]*\b(?:Related:|related content:)\b[^.]*\.).*|(\b(?:Related:|related content:)\b.*)", "", content, flags=re.IGNORECASE)

        return content.strip()

    def extract_articles(url, unwanted_keywords):
        """
        Extracts article content and publication date from a given URL using Trafilatura.
        Cleans content by removing newline characters, ensures no redirects, no external URLs, and language is English.
        Removes content after any unwanted keywords.
        """
        try:
            # Modify the config settings directly before use
            my_config = deepcopy(DEFAULT_CONFIG)

            # Disable external URLs and no redirects
            my_config['DEFAULT']['EXTERNAL_URLS'] = 'off'  # Disable external URL extraction
            my_config['DEFAULT']['MAX_REDIRECTS'] = '0'    # Disable URL redirection

            # Set download timeout and sleep time
            my_config['DEFAULT']['DOWNLOAD_TIMEOUT'] = '120'  # Set timeout to 120 seconds
            my_config['DEFAULT']['SLEEP_TIME'] = '5'         # Set sleep time between requests to 5 seconds

            # Fetch the content from the original URL using the modified config
            downloaded_html = trafilatura.fetch_url(url, config=my_config)

            if not downloaded_html:
                raise ValueError("Failed to download content")

            # Extract content using Trafilatura with the custom config
            extracted = trafilatura.extract(downloaded_html, output_format="json", with_metadata=True, config=my_config)
            if not extracted:
                raise ValueError("Trafilatura extraction failed")

            data = json.loads(extracted)

            # Clean and format the content
            content = data.get("text", "").replace("\n", " ").strip()

            # Remove content after the unwanted keywords
            content = remove_unwanted_content(content, unwanted_keywords)

            # Remove ad-related content based on EasyList rules
            easylist_rules = load_easylist_rules()  # Load EasyList rules
            content = remove_ad_content(content, easylist_rules)


            if not content or len(content) < 1500:  # 1500 characters roughly 300 words
                raise ValueError("Content too short")

            # Manually detect language (ensure it's English)
            try:
                detected_language = detect(content)  # Returns 'en' for English
                if detected_language != 'en':  # If not English, return empty content
                    print(f"Warning: Non-English content detected. Skipping URL.")
                    return {"content": "", "publish_date": None}
            except Exception as e:
                print(f"Error detecting language: {e}")
                return {"content": "", "publish_date": None}

            # Continue to extract publication date
            publish_date_str = data.get("date", None)
            publish_date = dateparser.parse(publish_date_str) if publish_date_str else None

            formatted_date = publish_date.strftime("%d-%m-%Y") if publish_date else None

            return {"content": content, "publish_date": formatted_date}

        except Exception as e:
            print(f"Error: {e}")
            return {"content": "", "publish_date": None}

    # Normalize country name to ISO3
    def normalize_country(name):
        return name_to_iso3.get(name.strip().lower(), None)

    # Function to extract relevant countries from the article text
    def extract_countries_from_text(text):
        found = set()
        lowered = text.lower()

        # Direct country match
        for name in name_to_iso3:
            if name in lowered:
                iso = normalize_country(name)
                if iso:
                    found.add(iso)

        # Match trading blocs
        for bloc, members in trading_bloc_aliases.items():
            if bloc in lowered:
                found.update(members)

        # Match regions
        for region, members in un_region_mapping.items():
            if region in lowered:
                found.update(members)

        return sorted(found)

    # Generate all unique 2-country combinations
    def generate_country_pairs(countries):
        return ['-'.join(sorted(pair)) for pair in combinations(countries, 2)]

    # Predict sentiment for all detected country pairs
    def predict_all_pairs(text, debug=False):
        """
        Predict sentiment scores for each country pair detected in the given text.
        This function processes article texts and detects country pairs.
        """
        detected = extract_countries_from_text(text)
        pairs = generate_country_pairs(detected)

        if debug:
            print(f"\n Detected countries: {detected}")
            print(f" Generated country pairs: {pairs}")

        results = {}

        # Loop through country pairs and run inference on each pair
        for pair in pairs:
            # Tokenize the text with overflow handling
            inputs = tokenizer(
                text,                # Article text
                pair,                # Country pair
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=512,
                stride=128,          # Overlap for chunks
                return_overflowing_tokens=True
            )

            # Remove overflow_to_sample_mapping from the inputs
            if "overflow_to_sample_mapping" in inputs:
                del inputs["overflow_to_sample_mapping"]

            # Initialize variable to accumulate sentiment scores for the chunks
            total_score = 0
            num_chunks = 0

            # Iterate through each chunk in overflowed tokens
            for i in range(len(inputs['input_ids'])):
                # Get the chunk for this index
                chunk = {key: value[i:i+1] for key, value in inputs.items()}

                chunk = {k: v.to(model.device) for k, v in chunk.items()}

                with torch.inference_mode():
                    outputs = model(**chunk)
                    score = outputs["logits"].item()
                    # Accumulate the score for the chunk
                    total_score += score
                    num_chunks += 1

            # Compute the average score across all chunks for this country pair
            avg_score = total_score / num_chunks if num_chunks > 0 else 0  # Avoid division by zero

            results[pair] = avg_score  # Store the averaged score for the current pair

        if debug:
            print(f" Predicted sentiment scores: {results}")

        return results

    # Step 5: Main execution
    article_data = extract_articles(url, unwanted_keywords)

    if not article_data["content"]:
        print("No content extracted from URL.")
        return {}, None

    # Get the publication year
    publish_year = None
    if article_data["publish_date"]:
        publish_date = datetime.strptime(article_data["publish_date"], "%d-%m-%Y")
        publish_year = publish_date.year

    # Get sentiment predictions for country pairs in the article
    sentiment_scores = predict_all_pairs(article_data["content"], debug=debug)
    return sentiment_scores, publish_year

# TGNN side
def csv_to_tensor_run(csv_file,sentiment_dict,year_nlp=2023):
    """
    Reads a CSV file with columns:
      country1, country2, sector1, sector2, ..., sector8, sentiment, year
    and returns a tensor of shape (T, N, D), where:
      T = number of years,
      N = number of unique country pairs,
      D = num of sectors + features.
    Also returns the sorted list of years and country pair nodes.
    """
    def change_sentiment_index(df1,dict,year):
        """
        Change the sentiment index of the dataframe based on NLP model. (For now, it replaces based on year)
        """
        for country_pair, sentiment in dict.items():
            # Extract the country pair from the tuple
            country_a, country_b = country_pair.split('-')
            # Update the sentiment index for the specific year and country pair
            df1.loc[(df1['year'] == year) & (df1['country_a'] == country_a) & (df1['country_b'] == country_b), 'sentiment_index'] = sentiment
            df1.loc[(df1['year'] == year) & (df1['country_a'] == country_b) & (df1['country_b'] == country_a), 'sentiment_index'] = sentiment
        return df1
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    df=change_sentiment_index(df,sentiment_dict,year_nlp)

    # Transform tradeagreementindex and sentiment_index into D
    df['D']=1+(-1)*0.5*df['tradeagreementindex']+(-1)*0.5*df['sentiment_index']
    df=df.drop(columns=['sentiment_index','tradeagreementindex'],axis=1)   

    T = 3 # Number of years to get from
    # Get all unique country pairs
    pairs_df = df[['country_a', 'country_b']].drop_duplicates()
    # Create a sorted list of tuples (country1, country2) for consistent node ordering
    country_pairs = sorted([tuple(x) for x in pairs_df.values])
    N = len(country_pairs)
    
    # Number of features (8 sectors + 1 sentiment)
    D = 9
    years=df['year'].unique()
    # Initialize an empty numpy array for the tensor data
    tensor_data = np.empty((T, N, D), dtype=float)
    
    # Loop over each year and each country pair to fill in the tensor
    for t, year in enumerate(years):
        # Get data for the current year
        df_year = df[df['year'] == year]
        for n, (c1, c2) in enumerate(country_pairs):
            # Filter rows for the current country pair
            row = df_year[(df_year['country_a'] == c1) & (df_year['country_b'] == c2)]
            if not row.empty:
                # Extract the 8 sector columns and the sentiment column.
                # Assumes these columns are named exactly as shown.
                features = row.iloc[0][['bec_1', 'bec_2', 'bec_3', 'bec_4', 
                                         'bec_5', 'bec_6', 'bec_7', 'bec_8', 'D']].values
                tensor_data[t, n, :] = features.astype(float)
            else:
                # If a record is missing for a given year/country pair, fill with zeros (or choose another strategy)
                tensor_data[t, n, :] = np.zeros(D)
                
    return tensor_data, years, country_pairs

def group_into_windows(tensor_data, window_size):
    """
    Given a tensor of shape (T, N, D), group the data into overlapping windows.
    Each window is of length window_size
    Returns a numpy array of shape (num_samples, window_size, N, D).
    """
    T, N, D = tensor_data.shape
    num_samples = T - window_size + 1  # sliding window with stride 1
    windows = []
    for i in range(num_samples):
        window = tensor_data[i: i + window_size]  # shape: (window_size, N, D)
        windows.append(window)
    windows = np.stack(windows)  # shape: (num_samples, window_size, N, D)
    return windows

def split_input_target_direct(windows, input_len, horizon=3):
    """
    Splits each window into input and a single target that is horizon steps forward.
    
    windows: numpy array of shape (num_samples, window_size, N, D)
              where window_size = input_len + horizon.
    input_len: number of time steps used as input.
    horizon: steps forward to pick the target (here, horizon=3).
    
    Returns:
      x: inputs of shape (num_samples, input_len, N, D)
      y: targets of shape (num_samples, N, 8), which are the first 8 features of the target time step.
    """
    # x: first input_len time steps (e.g., years 2006-2009 if input_len=4)
    x = windows[:, :input_len]  
    # y_full: the time step exactly horizon steps forward (i.e., index input_len + horizon - 1)
    # y_full = windows[:, input_len + horizon-1]  
    y_full = windows[:, input_len:input_len + horizon]
    # y: only the first 8 features from the predicted time step (ignoring sentiment_index and tradeagreementindex)
    y = y_full[..., :8]
    return x, y

def train_val_split(x, y, val_ratio=0.2):
    """
    Splits the data into train and validation sets by ratio.
    """
    num_samples = x.shape[0]
    split_index = int(num_samples * (1 - val_ratio))
    x_train, y_train = x[:split_index], y[:split_index]
    x_val, y_val = x[split_index:], y[split_index:]
    return x_train, y_train, x_val, y_val


##### DataTransformer
def pair_data(df):
    import pandas as pd

    # Drop pre-computed totals to avoid incorrect duplication
    df = df.drop(columns=[
        "total_export_of_A_to_B",
        "total_import_of_A_from_B",
        "trade_volume"
    ], errors="ignore")

    # Define BEC column names
    bec_export_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)]
    bec_import_cols = [f"bec_{i}_import_A_from_B" for i in range(1, 9)]

    # Create mirrored DataFrame (B to A)
    df_mirrored = df.copy()
    df_mirrored[["country_a", "country_b"]] = df_mirrored[["country_b", "country_a"]]

    for i in range(1, 9):
        export_col = f"bec_{i}_export_A_to_B"
        import_col = f"bec_{i}_import_A_from_B"
        df_mirrored[export_col], df_mirrored[import_col] = (
            df[import_col],
            df[export_col],
        )

    # Combine original and mirrored rows
    df_combined = pd.concat([df, df_mirrored], ignore_index=True)

    # Recalculate totals
    df_combined["total_export_of_A_to_B"] = df_combined[bec_export_cols].sum(axis=1)
    df_combined["total_import_of_A_from_B"] = df_combined[bec_import_cols].sum(axis=1)
    df_combined["trade_volume"] = (
        df_combined["total_export_of_A_to_B"] + df_combined["total_import_of_A_from_B"]
    )

    # Sort for easier viewing
    df_combined = df_combined.sort_values(by=["scenario", "country_a", "country_b"]).reset_index(drop=True)

    return df_combined




##############################################################
############### FINAL FUNCTION for TGNN ######################
##############################################################
def run_tgnn(sentiment_dict, year_nlp=2023):
    """
    Run the T-GNN model with the provided data dictionary.
    Key of dictionary: country pairs
    Value of dictionary: sentiment scores
    """
    
    # Convert the dictionary to a DataFrame
    args = Args()
    args.set_args(embed_dim=10, lr_init=0.005489139587271934,lr_decay_rate=0.18605505546333992, rnn_units=64, num_layers=2, weight_decay=3.0450041080579258e-05) #based on best model by Optuna

    #convert to tensor
    test_data_tensor, years, country_pairs_model = csv_to_tensor_run('./data/final/run_model_data.csv',sentiment_dict=sentiment_dict,year_nlp=year_nlp)
    
    #do normalisation
    data_to_normalize = test_data_tensor[:, :, :8]
    normalized_data, scaler = normalize_dataset(data_to_normalize, normalizer=args.normaliser,column_wise=True)
    remaining_features = test_data_tensor[:, :, 8:]

    # Get the shape dimensions
    T, N, _ = remaining_features.shape

    # Initialize the scaler with the desired feature range (-1, 1)
    scaler2 = MinMaxScaler(feature_range=(-1, 1))

    # Reshape the first column of remaining_features to 2D (T*N, 1)
    col_data = remaining_features[:, :, 0].reshape(-1, 1)

    # Fit and transform the column data using the scaler
    col_scaled = scaler2.fit_transform(col_data)

    # Reshape back to the original shape (T, N, 1)
    col_scaled = col_scaled.reshape(T, N, 1)
    # Concatenate along the last axis
    normalized_test_data = np.concatenate((normalized_data, col_scaled), axis=-1)
    test_x_tensor=torch.tensor(normalized_test_data, dtype=torch.float32)
    test_x_tensor = test_x_tensor.unsqueeze(0)  

    #load model and previously saved states
    model=AGCRNFinal(args)
    model=model.to(args.device)
    model.load_state_dict(torch.load('./model/logs/best_model_69.pth',map_location=torch.device('cpu')))
    model.eval()
    with torch.no_grad():
        test_x_tensor = test_x_tensor.to(args.device)
        predictions = model(test_x_tensor,None,0)
        predictions = predictions.cpu().numpy()

    #convert back to original scale
    predictions = scaler.inverse_transform(predictions[0, :, :, :8])

    # CONVERT % CHANGES TO ABSOLUTE VALUES
    initial_nums=pd.read_csv('./data/final/without_ARE_2021_2023.csv',header=0)

    # we only need 2023 data to compute forecasted 2024, 2025 and 2026 values
    initial_nums=initial_nums[initial_nums['year']==2023]
    initial_nums.reset_index(drop=True,inplace=True)

    # Group the dataframe indices by country pairs
    for country_pair in country_pairs_model:
        country_a, country_b = country_pair
        
        # Extract the subset of dataframe where country_a and country_b match
        subset = initial_nums[(initial_nums['country_a'] == country_a) & (initial_nums['country_b'] == country_b)]
        
        #check for any country pair/year missing 
        if subset.empty:
            print(f'country_pair: ({country_a}, {country_b}) is missing')

    # Apply Percentage change
    bec_cols=[f'bec_{i}' for i in range(1, 9)]
    future_years = [2024, 2025, 2026]
    predicted=[]

    for pair_idx, row in initial_nums.iterrows():
        # convert base values to numpy array and float
        base_values = row[bec_cols].values.astype(float)
        
        # copy just for saving the initial values
        current_values = base_values.copy()
        
        # Apply the percentage changes for each future year
        for year_offset, future_year in enumerate(future_years):
            # extract the 8 % changes for country pair in forecast_year
            pct_change = predictions[year_offset, pair_idx, :]
            # convert to factor change
            factor = 1 + pct_change / 100.0
            
            # update current values
            current_values = current_values * factor
            
            # build dictionary to build final dataframe
            row_dict = {
                'country_a': row['country_a'],
                'country_b': row['country_b'],
                'year': future_year
            }
            # add each bec column
            for col_idx, col in enumerate(bec_cols):
                row_dict[col] = current_values[col_idx]
            
            # Add the row to our list
            predicted.append(row_dict)

    # Create a new df containing the predicted absolute trade volumes for 2024, 2025, 2026
    predictions_df = pd.DataFrame(predicted)

    #Put exports and imports in the same row and transform column names
    temp=pd.merge(predictions_df,predictions_df,how='outer',left_on=['country_a','country_b','year'],right_on=['country_b','country_a','year'],suffixes=('_export_A_to_B', '_import_A_from_B'))
    temp.drop(columns=['country_a_import_A_from_B','country_b_import_A_from_B'],inplace=True)
    temp.rename(columns={'country_a_export_A_to_B':'country_a','country_b_export_A_to_B':'country_b'},inplace=True)
    temp['country_pair'] = temp.apply(
        lambda x: '_'.join(sorted([x['country_a'], x['country_b']])), 
        axis=1
    )
    temp.rename(columns=lambda col: col[:-1] + 'B' if col.endswith('_to_b') else col, inplace=True)
    temp = temp.drop_duplicates(subset=['country_pair', 'year'], keep='first')
    temp = temp.drop('country_pair', axis=1)

    #add additional columns for frontend
    bec_export_cols=[f'bec_{i}_export_A_to_B' for i in range(1, 9)]
    bec_import_cols=[f'bec_{i}_import_A_from_B' for i in range(1, 9)]
    temp['total_export_of_A_to_B']=temp[bec_export_cols].sum(axis=1)
    temp['total_import_of_A_from_B']=temp[bec_import_cols].sum(axis=1)
    temp['trade_volume']=temp['total_export_of_A_to_B']+temp['total_import_of_A_from_B']
    temp['scenario']='postshock'

    #reorder columns for frontend
    temp=temp[['country_a','country_b','year','total_export_of_A_to_B','total_import_of_A_from_B','trade_volume']+bec_export_cols+bec_import_cols+['scenario']]

    # #filter only 2026 data and add scenario column for frontend
    temp=temp[temp['year']==2026] #comment out if need 2024 to 2026 data as well

    baseline=pd.read_csv('./data/final/2026_baseline_forecast.csv',header=0)
    baseline.rename(columns=lambda col: col[:-1] + 'B' if col.endswith('_to_b') else col, inplace=True)
    final=pd.concat([baseline,temp],axis=0,ignore_index=True)
    final.reset_index(drop=True,inplace=True)

    final = pair_data(final)
    #final.to_csv("/Users/jeremytoh/Desktop/dse3101/lalala_post.csv") # change this to visualise and check if needed 
    return final

