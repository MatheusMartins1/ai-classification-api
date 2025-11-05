# Image Metadata API

API FastAPI para extrair metadados de imagens seguindo princípios SOLID e boas práticas.

## 🏗️ Estrutura

```
ai-regression-api/
├── main.py                 # Entry point
├── config/                 # Configurações
│   └── settings.py         # Settings com Pydantic
├── models/                 # Modelos Pydantic
│   └── image_metadata.py   # Modelos de metadata
├── services/               # Lógica de negócio
│   ├── metadata_extractor.py  # Extração de metadados
│   └── webhook_service.py      # Envio para webhook
├── routers/                # Endpoints FastAPI
│   └── metadata.py         # Router de metadados
├── utils/                  # Utilitários
│   └── logger_config.py    # Logger centralizado
└── requirements.txt        # Dependências
```

## ⚙️ Setup

### Setup Automático
```bash
# Windows
setup.bat

# Linux/WSL
chmod +x setup.sh
./setup.sh
```

### Setup Manual
```bash
pip install -r requirements.txt
```

## 🔧 Configuração

Crie arquivo `.env`:

```
WEBHOOK_URL=https://seu-webhook.com/endpoint
WEBHOOK_TIMEOUT=10.0
LOG_LEVEL=INFO
DEBUG=False
```

## 🚀 Executar

### Opção 1: VSCode Debug (Recomendado)
Pressione `F5` e selecione:
- **FastAPI: Run Server** - Servidor com hot-reload
- **FastAPI: Debug Server** - Debug completo com breakpoints

### Opção 2: Python Direto
```bash
python main.py
```

### Opção 3: Uvicorn Manual
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8345
```

**Porta:** `8345` | **Docs:** `http://localhost:8345/docs`

## 📡 Endpoints

### Health Check

```bash
GET /
GET /health
```

### Extrair Metadados

```bash
POST /api/v1/extract-metadata
Content-Type: multipart/form-data

curl -X POST "http://localhost:8345/api/v1/extract-metadata" \
  -F "file=@imagem.jpg"
```

**Resposta:**

```json
{
  "success": true,
  "metadata": {
    "format": "JPEG",
    "mode": "RGB",
    "size": {"width": 1920, "height": 1080},
    "file_size_bytes": 245678,
    "filename": "imagem.jpg",
    "content_type": "image/jpeg",
    "timestamp": "2024-11-05T12:00:00",
    "exif": {...},
    "info": {...}
  },
  "message": "Metadados extraídos com sucesso"
}
```

## 🎯 Princípios Aplicados

- **SOLID**: Single Responsibility, separação de camadas
- **Type Hints**: Tipos em todas as funções
- **Docstrings**: Documentação Google Style
- **PEP 8**: Código formatado e limpo
- **Logging**: Sistema centralizado de logs
