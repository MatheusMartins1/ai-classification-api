# Dockerfile for Thermal Image Metadata API
# Developer: Matheus Martins da Silva
# Creation Date: 11/2025

FROM python:3.12-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs and temp directories
RUN mkdir -p logs temp

# Expose port (default 8345, can be overridden by PORT env var)
EXPOSE ${PORT:-8345}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; import requests; port = os.getenv('PORT', '8345'); requests.get(f'http://localhost:{port}/health')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8345}"]

