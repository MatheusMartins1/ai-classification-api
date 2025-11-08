# Thermal Image Metadata API

API FastAPI para extrair metadados e dados térmicos de imagens FLIR usando flyr e OpenCV.

## 🏗️ Estrutura

```
ai-regression-api/
├── main.py                 # Entry point
├── Dockerfile              # Docker configuration
├── config/                 # Configurações
│   └── settings.py         # Settings com Pydantic
├── models/                 # Modelos Pydantic
│   └── image_metadata.py   # Modelos de metadata
├── services/               # Lógica de negócio
│   ├── data_extractor_service.py  # Extração de dados térmicos
│   └── webhook_service.py         # Envio para webhook
├── routers/                # Endpoints FastAPI
│   └── upload.py           # Router de upload
├── utils/                  # Utilitários
│   ├── logger_config.py    # Logger centralizado
│   └── azure/              # Azure integration
└── requirements.txt        # Dependências
```

## ⚙️ Setup

### Desenvolvimento Local
```bash
pip install -r requirements.txt
```

### Docker
```bash
docker build -t thermal-api .
docker run -p 8345:8345 thermal-api
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

### Upload de Inspeção Térmica

```bash
POST /api/v1/upload-inspection
Content-Type: multipart/form-data

curl -X POST "http://localhost:8345/api/v1/upload-inspection" \
  -F "user_id=user123" \
  -F "ir_image_0=@FLIR1970.jpg"
```

**Resposta:**

```json
{
  "status": "success",
  "message": "Imagens IR recebidas com sucesso",
  "user_info": {
    "user_id": "user123",
    "company_id": null,
    "email": null
  },
  "files_processed": 1,
  "ir_images": [
    {
      "field_name": "ir_image_0",
      "filename": "FLIR1970.jpg",
      "content_type": "image/jpeg",
      "size": 245678,
      "metadata": {
        "celsius": [[...]],
        "camera_metadata": {...}
      }
    }
  ]
}
```

## 🎯 Princípios Aplicados

- **SOLID**: Single Responsibility, separação de camadas
- **Type Hints**: Tipos em todas as funções
- **Docstrings**: Documentação Google Style
- **PEP 8**: Código formatado e limpo
- **Logging**: Sistema centralizado de logs
