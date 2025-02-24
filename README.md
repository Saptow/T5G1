# T5G1
Group project for DSE3101 on question: Geopolitical distance and Global Trade



## Setup Instructions

### Prerequisites
Ensure you have `pyenv` installed. If not, you can install it by following the instructions [here](https://github.com/pyenv/pyenv#installation).

### Setting up the Virtual Environment

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/T5G1.git
    cd T5G1
    ```

2. **Install Python 3.12.0 using pyenv:**
    ```sh
    pyenv install 3.12.0
    pyenv local 3.12.0
    ```

3. **Create a virtual environment:**
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

Your virtual environment is now set up and you can start working on the project.

**IF YOU INSTALL NEW DEPENDENCIES**
pip freeze > requirements.txt (replace so that anyone after can just install using the requirements.txt to solve the problem)