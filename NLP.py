import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load pre-trained sentiment analysis model (DeBERTa)
sentiment_model_name = "yangheng/deberta-v3-base-absa-v1.1"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)

# Load Zero-Shot Classification model (RoBERTa)
zero_shot_model_name = "roberta-large-mnli"
zero_shot_classifier = pipeline("zero-shot-classification", model=zero_shot_model_name)

# Example text (news article)
text = """
On January 27, President Trump proposed up to 100 percent tariffs on semiconductors made in Taiwan, while criticizing the bipartisan CHIPS Act, which has already spurred over $450 billion in investments in America’s semiconductor and electronics sectors. But if Trump raised tariffs on imported Taiwanese chips to 100 percent, it wouldn’t drive Taiwanese semiconductor and electronics firms to America. Instead, the policy would unleash a global, cross-sector tariff war that would boost costs for Americans, hurt American tech firms, and damages relations with a key U.S. ally at a vital time.
What President Trump is essentially proposing is the United States raise tariffs on all semiconductors up to 100 percent. Trump’s assumption is if he raises tariffs on Taiwanese semiconductors to 100 percent, Taiwanese semiconductor manufacturers will move to the United States to avoid them. But if the United States imposes smaller tariffs on semiconductor imports from say India, Japan, or Malaysia, the Taiwanese companies will only move their factories there, not necessarily to the United States. Or U.S. companies will buy their semiconductors from other foreign companies.
"""

# Define pairwise aspects for sentiment analysis
pairwise_aspects = ["US-Taiwan", "US-China", "US-India", "Taiwan-China"]

# Define predefined sectors for Zero-Shot Classification
sectors = ['Agriculture', 'Technology', 'Finance', 'Manufacturing', 'Energy']

# Initialize dictionaries for storing sentiment and affected sectors
sentiment_aspect = {}
affected_sectors = set()

# ---------------- SENTIMENT ANALYSIS ---------------- #
for aspect in pairwise_aspects:
    inputs = sentiment_tokenizer(text, aspect, return_tensors="pt")

    # Perform inference for sentiment analysis
    with torch.inference_mode():
        outputs = sentiment_model(**inputs)

    # Apply softmax to get probabilities from logits
    scores = F.softmax(outputs.logits[0], dim=-1)

    # Get the class with the highest probability
    label_id = torch.argmax(scores).item()

    # Get the predicted sentiment label
    sentiment_label = sentiment_model.config.id2label[label_id]

    # Modify sentiment score based on classification
    if sentiment_label == 'Neutral':
        sentiment_score = 0  # Assign neutral a score of 0
    elif sentiment_label == 'Negative':
        sentiment_score = -scores[label_id].item()  # Multiply negative by -1
    else:
        sentiment_score = scores[label_id].item()  # Keep positive score as is

    # Store the sentiment label and score
    sentiment_aspect[aspect] = (sentiment_label, sentiment_score)

# ---------------- ZERO-SHOT CLASSIFICATION FOR SECTORS ---------------- #
classification_result = zero_shot_classifier(text, sectors, multi_label=True)

# Convert results to dictionary
confidence_scores = {
    label: score for label, score in zip(classification_result["labels"], classification_result["scores"])
}
# Print the original confidence scores (just to see what comes out now)
print("\nOriginal Confidence Scores:")
print(confidence_scores)

# Confidence threshold for zero-shot classification , or can take the top few scores
confidence_threshold = 0.2  # Adjust as needed

for label, score in zip(classification_result["labels"], classification_result["scores"]):
    if score > confidence_threshold:
        affected_sectors.add(label)

# ---------------- FINAL OUTPUT ---------------- #
print("\nFinal Sentiment Analysis Results:")
print(sentiment_aspect)

print("\nSectors Affected:")
print(affected_sectors)
