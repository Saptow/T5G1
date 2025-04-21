# T5G1
Group project for DSE3101 on question: Geopolitical distance and Global Trade

## Table of Contents
- [T5G1](#t5g1)
  - [Setting up the Environment to try on your local machine using Docker Compose (Recommended)](#setting-up-the-environment-to-try-on-your-local-machine-using-docker-compose-recommended)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Setting up the Environment Manually (if Docker Compose does not work)](#setting-up-the-environment-manually-if-docker-compose-does-not-work)
    - [Prerequisites](#prerequisites-1)
    - [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
  - [Where to Find Everything](#where-to-find-everything)
  - [Brief Description of Models](#brief-description-of-models)
  - [Pre-Processing Steps](#pre-processing-steps)
  - [Training Pipeline](#training-pipelines)


## Setting up the Environment to try on your local machine using Docker Compose (Recommended)
#### Prerequisites

Ensure you have Docker and Docker Compose installed. If not, you can install them by following the instructions [here](https://docs.docker.com/get-docker/) for Docker and [here](https://docs.docker.com/compose/install/) for Docker Compose. </br>

Note that Docker Compose has to be used here due to the size of the requirements of this application (particularly PyTorch). </br>
Note that your first time you press "Go" on the frontend, it will take a while to load the model. This is because it has to download the NLP model from HuggingFace. After that, it will be cached and will be much faster. We could not Git LFS the NLP model weights as we had hit the free quota by accident, so we are going to import it from HuggingFace instead. Apologies for that...

#### Steps
1. **Clone the repository:**
    ```sh
    git clone https://github.com/Saptow/T5G1.git
    cd T5G1
    ```

2. **Build the Docker image:**
    ```sh
    docker-compose build
    ```

3. **Run the Docker Compose Container:**
    ```sh
    docker-compose up
    ```
    This will start the application and expose it on port 8050(frontend) and 5000(backend).
    You can access the frontend by navigating to `http://127.0.0.1:8050` in your web browser. Enjoy!



## Setting up the Environment Manually (if Docker Compose does not work)
### Prerequisites
Ensure you have `pyenv` installed. If not, you can install it by following the instructions [here](https://github.com/pyenv/pyenv#installation).

### Setting up the Virtual Environment

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Saptow/T5G1.git
    cd T5G1

2. **Install Python 3.12.0 using pyenv:** (Our code is compatible with Python 3.12.0)
    ```sh
    pyenv install 3.12.0
    pyenv local 3.12.0
    ```

3. **Create a virtual environment:** (This step is heavily recommended to avoid package conflicts, especially if you have any other projects using different versions of Python or packages.)
    ```sh
    python -m venv venv
    ```

4. **Activate the virtual environment: (DO THIS EVERYTIME YOU START THE PROJECT)**
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

5. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

6. **Run the application:**

    - For the backend:
    ```sh
    flask --app flask_backend run
    ```

    - For the frontend:
    ```sh
    python webpage.py
    ```

    This will start the application and expose it on port 8050(frontend) and 5000(backend).

## Where to Find Everything
### Frontend

- **Folder**: `apps/`
- **Main Pages**:
  - `webpage.py` – main Dash app interface

- **Styling**: `assets/`
  - `style.css` – contains CSS styling and layout configuration

---

### Backend

- **Folder**: `model/`
- **Core Modules**:
  - `helpers_backend.py` – utility functions used in backend processing
  - `agcrn_model.py` – entry point for AGCRN model
  - `AGCRN/` – source code and layers for the Adaptive Graph Convolutional Recurrent Network (AGCRN)

---

### Model Training and Benchmarking

- `model/fixedeffect.ipynb` – benchmarking notebook using fixed effects regression for geopolitical distance index
- `NLP_training.ipynb` – fine-tuning and training pipeline for the sentiment score model
- `AGCRN_training.ipynb` – time series model training for sectoral trade forecasts

---

### API Service

- `flask_backend.py` – Flask API backend handling prediction requests and routing
Datasets used for our application can be found under **data/final** folder, while the cleaning code and scraper can be found in the cleaning code and scraper folders respectively. 
## Brief Description of Models
Our backend consists of 2 sub-models, namely our NLP model and ACGRN model. Together, they function to forecast sectoral bilateral trade volumes between country pairs from a piece of trade news article. 
It starts with the trade news article being scraped by Trafilatura, which then gets parsed into the NLP model to output sentimental scores between country pairs, as well as year. These are pipelined into the ACGRN model, in the form of our unique composite Geopolitical Distance Index, to output 2026 sectoral bilateral trade volumes between country pairs. More details can be found in our technical documentation.

## Pre-Processing Steps
Datasets used include:
1. **UN Comtrade** for trade volume data, which was pulled through API calls in Harmonised System (HS) codes and then converted into Broad Economic Categories (BEC) rev 5 codes
2. **GDELT Dataset** for sentiment scores for events based on country pairs, used to train our model.
3. **Formal Bilateral Influence Capacity (FBIC)** dataset to derive our tradeagreementindex, consumed by our unique Geopolitical Distance Index. 
4. **UN Voting Records** dataset to benchmark our new composite Geopolitical Distance Index against.

Typical normalisation algorithms like MinMax Normalisation were used to pre-process before training and deployment. Data completeness checks were done as well to ensure some degree of data quality. Likewise, more details can be found in our technical documentation. 

## Training Pipeline
For the NLP model, 4000 data points randomly sampled from 2019-2023 events from GDELT dataset were used to train, based on the AvgTone column. Since we adopted a pre-trained model, we utilised a fine-tuning algorithm, which will involve a much slower learning rate so as to avoid overfitting of data. Train/Validation/Test split was 80-10-10. Hyperparameter tuning was done through Optuna.

For the ACGRN model, 2006 to 2020 trade volume data was used to effect into 2007-2020 percentage changes in export volumes before pipelined into the model for training. Since we required a window of 6 years to train our model, we utilised PyTorch's dataloader shuffle to randomly expose the model to different sequences of said windows during training, preventing learning of spurious patterns. Hyperparameter tuning was also done through Optuna. 

As usual, more details can be found in our technical documentation.
