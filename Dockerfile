FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required (none needed for basic run, but good to have)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the Flask port
EXPOSE 5001

# Run the Flask app
CMD ["python", "app.py"]
