FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for visualization
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY weather_client/ ./weather_client/
COPY main.py .

# Create necessary directories
RUN mkdir -p /app/cache /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["python", "main.py"]