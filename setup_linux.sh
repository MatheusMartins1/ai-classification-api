#!/bin/bash
# Setup script for Linux/WSL - Tenesso AI Regression API
# Developer: Matheus Martins da Silva
# Creation Date: 11/2025

set -e  # Exit on error

echo "=========================================="
echo "Setup Linux/WSL - Tenesso AI Regression API"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Por favor, NÃO execute como root/sudo${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[1/6] Atualizando repositórios...${NC}"
sudo apt-get update

echo ""
echo -e "${GREEN}[2/6] Instalando dependências do sistema...${NC}"
sudo apt-get install -y \
    wget \
    curl \
    apt-transport-https \
    software-properties-common \
    build-essential \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    exiftool

echo ""
echo -e "${GREEN}[3/6] Instalando .NET 7 SDK...${NC}"

# Add Microsoft package repository
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Install .NET 7 SDK
sudo apt-get update
sudo apt-get install -y dotnet-sdk-7.0

# Verify .NET installation
if command -v dotnet &> /dev/null; then
    echo -e "${GREEN}✓ .NET instalado com sucesso!${NC}"
    dotnet --version
else
    echo -e "${RED}✗ Erro ao instalar .NET${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[4/6] Configurando Python virtual environment...${NC}"

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo -e "${YELLOW}Python 3.12 não encontrado. Instalando...${NC}"
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Criando virtual environment..."
    python3.12 -m venv .venv
else
    echo "Virtual environment já existe"
fi

# Activate virtual environment
source .venv/bin/activate

echo ""
echo -e "${GREEN}[5/6] Instalando dependências Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${GREEN}[6/6] Configurando variáveis de ambiente para pythonnet...${NC}"

# Create or update .env file with pythonnet configuration
if [ ! -f ".env.dev" ]; then
    echo -e "${YELLOW}Arquivo .env.dev não encontrado. Criando...${NC}"
    touch .env.dev
fi

# Add pythonnet configuration if not present
if ! grep -q "PYTHONNET_RUNTIME" .env.dev; then
    echo "" >> .env.dev
    echo "# Pythonnet configuration for Linux/WSL" >> .env.dev
    echo "PYTHONNET_RUNTIME=coreclr" >> .env.dev
    echo "PYTHONNET_CORECLR_RUNTIME_VERSION=7.0" >> .env.dev
    echo -e "${GREEN}✓ Configuração pythonnet adicionada ao .env.dev${NC}"
else
    echo -e "${YELLOW}Configuração pythonnet já existe no .env.dev${NC}"
fi

# Create activation script with environment variables
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Activation script with pythonnet configuration

export PYTHONNET_RUNTIME=coreclr
export PYTHONNET_CORECLR_RUNTIME_VERSION=7.0

source .venv/bin/activate

echo "Environment activated with pythonnet configuration:"
echo "  PYTHONNET_RUNTIME=$PYTHONNET_RUNTIME"
echo "  PYTHONNET_CORECLR_RUNTIME_VERSION=$PYTHONNET_CORECLR_RUNTIME_VERSION"
EOF

chmod +x activate_env.sh

echo ""
echo -e "${GREEN}=========================================="
echo "Setup concluído com sucesso!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Para ativar o ambiente, execute:${NC}"
echo -e "  ${GREEN}source activate_env.sh${NC}"
echo ""
echo -e "${YELLOW}Ou manualmente:${NC}"
echo -e "  ${GREEN}export PYTHONNET_RUNTIME=coreclr${NC}"
echo -e "  ${GREEN}export PYTHONNET_CORECLR_RUNTIME_VERSION=7.0${NC}"
echo -e "  ${GREEN}source .venv/bin/activate${NC}"
echo ""
echo -e "${YELLOW}Verificar instalação:${NC}"
echo -e "  ${GREEN}dotnet --version${NC}"
echo -e "  ${GREEN}python --version${NC}"
echo -e "  ${GREEN}exiftool -ver${NC}"
echo ""

