# Dockerfile for Image Metadata API
# Developer: Matheus Martins da Silva
# Creation Date: 11/2025

#TODO: Change base image. This has high vulnerabilities
FROM python:3.12-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONNET_RUNTIME=coreclr \
    DOTNET_ROOT=/usr/share/dotnet

# Install system dependencies including libicu72 for .NET
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    gnupg \
    apt-transport-https \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libssl-dev \
    libffi-dev \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    libicu72 \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

# Baixar repositório Microsoft para apt (para dotnet runtime)
RUN wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && rm /tmp/packages-microsoft-prod.deb

# Instalar dotnet runtime (ex: 7.0). Ajuste se precisar de 6.0 ou 8.x.
RUN apt-get update \
    && apt-get install -y --no-install-recommends dotnet-runtime-7.0 \
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

# Coloque as DLLs do FLIR numa pasta fixa do container (ex.: /opt/flir)
COPY ThermalCameraLibrary /opt/ThermalCameraLibrary

# Ajuste permissões (se necessário)
RUN chmod -R 755 /opt/ThermalCameraLibrary

# Variável de ambiente opcional para apontar onde estão as DLLs
ENV FLIR_DLL_PATH=/opt/ThermalCameraLibrary

# Create logs directory
RUN mkdir -p logs

# Expose port (default 8345, can be overridden by PORT env var)
EXPOSE ${PORT:-8345}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; import requests; port = os.getenv('PORT', '8345'); requests.get(f'http://localhost:{port}/health')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8345}"]

