#Our project uses Python 3.12.0
FROM python:3.12.0-slim-bookworm

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt
RUN pip install --no-cache-dir transformers==4.51.3
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install torch-geometric -f https://data.pyg.org/whl/torch-2.6.0+cpu.html


# copy app code (to immediately deploy backend)
COPY . .

# Set environment variable to avoid warning
ENV FLASK_APP=flask_backend.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]