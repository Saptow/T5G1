# T5G1
Group project for DSE3101 on question: Geopolitical distance and Global Trade


## Setting up the Environment to try on your local machine using Docker Compose (Recommended)
#### Prerequisites
Ensure you have Docker and Docker Compose installed. If not, you can install them by following the instructions [here](https://docs.docker.com/get-docker/) and [here](https://docs.docker.com/compose/install/).

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Saptow/T5G1.git
    cd T5G1
    ```

2. **Build the Docker image:**
    ```sh
    docker-compose build
    ```

3. **Run the Docker container:**
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