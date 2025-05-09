# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

EXPOSE 5003

# Set default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5003"]
