# Instruções de Desenvolvimento - Tenesso One Backend

## 📋 Visão Geral

Este projeto utiliza **FastAPI** com **Python** para extração de metadados de imagens térmicas FLIR. Siga rigorosamente estas diretrizes para manter consistência e qualidade do código.

## 🛠️ Stack Tecnológica
- **Operational System**: Docker for production, linux in wsl for development
- **Backend**: FastAPI 4.x
- **Linguagem**: Python 3.12+
- **Database**: PostgreSQL/SQLite3
- **Thermal Image Processing**: flyr + OpenCV
- **Image Analysis**: FLIR Thermal Images

## 🏗️ Estrutura de Diretórios

### 📁 Organização Obrigatória (FastAPI Project)

```
ai-regression-api/
├── requirements.txt         # Python dependencies
├── main.py                 # Application entry point
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
│
├── config/                 # Project configuration files
│   └── settings.py         # Application settings
│
├── models/                 # Pydantic models
│   └── image_metadata.py   # Image metadata models
│
├── routers/                # API endpoints
│   └── upload.py           # Upload endpoints
│
├── services/               # Business logic
│   ├── data_extractor_service.py  # Thermal data extraction
│   └── webhook_service.py         # Webhook notifications
│
├── utils/                  # Shared utilities
│   ├── LoggerConfig.py     # Centralized logger handler
│   ├── logger_config.py    # Logger utilities
│   ├── object_handler.py   # Object manipulation utilities
│   └── azure/              # Azure integration
│
├── logs/                   # Application logs storage
├── temp/                   # Temporary file storage
├── files/                  # File storage and management
└── tests/                  # Test suite and test files
```

## 🔧 Key Components Description

### 📸 Services Module (`services/`)
Core business logic for thermal image processing:
- Thermal data extraction from FLIR images
- Metadata parsing and structuring
- Optical image extraction
- Temperature matrix processing

### 🛠️ Utilities (`utils/`)
Core utility functions and configurations:
- Centralized logging system
- Object manipulation helpers
- Azure blob storage integration
- Common utility functions

## 📝 Padrões de Código

### 🎯 Nomenclatura (APENAS EM INGLÊS)

- **Classes**: PascalCase (ex: `CameraManager`, `UserProfile`, `ThermalImageProcessor`)
- **Funções/Métodos**: snake_case (ex: `get_camera_data`, `process_thermal_image`)
- **Variáveis**: snake_case (ex: `camera_instance`, `thermal_data`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_TEMPERATURE`, `DEFAULT_CAMERA_SETTINGS`)
- **Arquivos**: snake_case (ex: `camera_services.py`, `thermal_processor.py`)
- **FastAPI Apps**: snake_case (ex: `camera`, `user_management`)
- **Database Tables**: snake_case (ex: `camera_settings`, `thermal_readings`)

### 📚 Documentação Obrigatória

- **TODOS** os arquivos `.py` devem ter docstring no topo
- **TODAS** as funções/métodos devem ter docstring no formato Google Style
- **SEMPRE** atualizar docstrings quando modificar código
- **OUTPUTS** para usuários em português, **CÓDIGO** em inglês
- **IMPORTS** organizados conforme PEP 8 (stdlib, third-party, local). 
    - IMPORTANTE: *NUNCA IMPORTE DENTRO DE FUNÇÂO/METODO*

### ⚡ Simplicidade e Concisão (CodeGuru Style)

- Mantenha código **SIMPLES** e **DIRETO**
- Evite over-engineering
- Prefira **legibilidade** sobre cleverness
- **Single Responsibility Principle** - cada classe/função tem UMA responsabilidade
- **DRY** - Don't Repeat Yourself
- **KISS** - Keep It Simple, Stupid
- **SOLID Principles** aplicados consistentemente

## 📋 Regras de Qualidade

### � Regras Críticas _AI_INSTRUCTIONS.TXT

1. **Completeness**: Gerar apenas blocos de código necessários à questão
2. **Comments**: Incluir comentários inline claros e docstrings descrevendo cada etapa
3. **Error Checking**: Implementar verificação de erros e validação de tipos
4. **Strings**: Aderir aos padrões de strings:
   - Usar aspas duplas (`"`) para strings
   - Usar f-strings para formatação
5. **Functions**: Incluir type hints para parâmetros e retorno
6. **Pattern**: Sempre aderir às regras PEP e design patterns. Manter código pythônico conforme TODAS as regras PEP
7. **Imports**: Manter padrão de imports (stdlib, third-party, local)
    - *Nunca importe dentro de função/Método*
8. **Sign**: No início do arquivo, sempre manter docstring assinada

### �📚 Documentação Obrigatória FastAPI

- **TODOS** os arquivos `.py` devem ter docstring no cabeçalho
- **TODAS** as funções/métodos devem ter docstring no formato Google Style
- **SEMPRE** atualizar docstrings quando modificar código
- **OUTPUTS** para usuários em português, **CÓDIGO** em inglês
- **NÃO** criar arquivos `.md` individuais para cada arquivo
- **APENAS** criar `.md` de resumo para módulos/apps complexos

### 🧹 Gestão de Arquivos FastAPI

- **EVITE** criar documentação excessiva que torna projeto difícil de manter
- **UM** arquivo de documentação por app FastAPI complexo (opcional)
- **ZERO** arquivos de documentação para funções/views individuais
- **FOQUE** na qualidade do código e docstrings internas

### ✅ Padrões FastAPI & PEP

- **NUNCA** commitar código com erros de flake8/pylint
- Execute `python manage.py check` antes de cada commit
- Configure seu editor para auto-format com black
- Siga PEP 8, PEP 257 e FastAPI Coding Style rigorosamente

## ⚠️ Regras Críticas - NUNCA QUEBRAR

1. **PEP 8 Compliance**: Sempre seguir PEP 8 rigorosamente
2. **Type Hints**: Usar type hints em todas as funções e métodos
3. **FastAPI Best Practices**: Seguir convenções FastAPI (fat models, thin views)
4. **Error Handling**: Sempre tratar erros adequadamente com try/except
5. **Código em Inglês**: Variáveis, funções, comentários em inglês
6. **Outputs em Português**: Mensagens para usuário em português
7. **Docstring Obrigatório**: Todas as funções devem ter documentação
8. **File Docstring Obrigatório**: Todos os arquivos devem ter cabeçalho
9. **Single Responsibility**: Uma responsabilidade por classe/função
10. **KISS Principle**: Mantenha código simples e direto
11. **FastAPI Security**: Sempre validar inputs e usar CSRF protection
12. **Database Optimization**: Evitar N+1 queries, usar select_related
13. **Logging**: Implementar logging adequado para debugging
14. **Code Quality**: Código deve passar em flake8 sem warnings
15. **Testing**: Escrever testes para funcionalidades críticas
16. **No Over-Documentation**: NÃO criar .md para cada arquivo
17. **String Formatting**: Usar f-strings e aspas duplas
18. **Import Organization**: Seguir ordem PEP 8 (stdlib, third-party, local)

## 🏆 Checklist Pré-Commit FastAPI

- [ ] Código passa no `flake8` sem erros/warnings
- [ ] `black` formatou o código automaticamente
- [ ] `python manage.py check` executa sem erros
- [ ] Type hints implementados em todas as funções
- [ ] **TODOS** os textos para usuário em português
- [ ] **TODO** código/variáveis/funções em inglês
- [ ] **Docstring** completo em todas as funções/classes
- [ ] **File docstring** presente no cabeçalho do arquivo
- [ ] Tratamento de erro implementado com try/except
- [ ] Logging implementado para operações críticas
- [ ] Consultas de banco otimizadas (sem N+1)
- [ ] Testes passando (quando existirem)
- [ ] Validação de inputs implementada
- [ ] **Single responsibility** respeitado
- [ ] Código **simples** e **direto**
- [ ] **NÃO** criou arquivos .md desnecessários
- [ ] Imports organizados conforme PEP 8
- [ ] F-strings usadas para formatação de strings

## 🎯 Contexto Específico - Thermal Image Processing

### 📡 Integração flyr

```python
"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting thermal and visual data from FLIR thermal images.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
import cv2
from typing import Dict
import flyr
import json

def extract_data_from_image(image_name: str = "FLIR1970.jpg") -> dict:
    """
    Extract thermal data and metadata from FLIR image.
    
    Args:
        image_name: Name of the FLIR image file
        
    Returns:
        Dictionary containing extracted metadata and thermal data
    """
    image_path = os.path.join("temp", image_name)
    
    # Unpack FLIR image
    thermogram = flyr.unpack(image_path)
    
    # Extract thermal data
    thermogram_data = {
        "image_filename": image_name,
        "image_path": image_path,
        "celsius": thermogram.celsius.tolist(),
        "metadata": thermogram.metadata,
        "camera_metadata": thermogram.camera_metadata,
    }
    
    # Save optical image
    thermogram.optical_pil.save(os.path.join("temp", f"{image_name}_optical.jpg"))
    
    return thermogram_data
```

### 🌡️ Documentação

- **flyr Library**: https://pypi.org/project/flyr/
- **OpenCV**: https://opencv.org/
- **Environment**: Docker, Linux, Windows

---

**Lembre-se**:

- **Qualidade** não é negociável
- **Simplicidade** é fundamental  
- **Documentação** interna (docstring) é obrigatória
- **Documentação** externa (.md) é **mínima**
- **Código** em inglês, **output** em português
- **FastAPI** best practices sempre
- **PEP compliance** rigoroso
- **Thermal Processing** usando flyr + OpenCV
- Siga estas diretrizes **rigorosamente** para manter a excelência do projeto Tenesso
