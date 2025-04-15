#Our project uses Python 3.12.0
FROM python:3.12.0-slim-bookworm

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set environment variable to avoid warning
ENV FLASK_APP=flask_backend.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]