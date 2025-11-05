# Instruções de Desenvolvimento - Tenesso One Backend

## 📋 Visão Geral

Este projeto utiliza **FastAPI** com **Python**, **PostgreSQL** e **Pythonnet** para integração com Flir Atlas SDK. Siga rigorosamente estas diretrizes para manter consistência e qualidade do código.

## 🛠️ Stack Tecnológica
- **Operational System**: Docker for production, linux in wsl for development
- **Backend**: FastAPI 4.x
- **Linguagem**: Python 3.12+
- **Database**: PostgreSQL/SQLite3
- **SDK Integration**: Pythonnet + Flir Atlas SDK 7.5
- **Camera Management**: Flir Thermal Cameras
- **Documentation**: Flir Atlas Live Namespace

## 🏗️ Estrutura de Diretórios

### 📁 Organização Obrigatória (FastAPI Project)

```
ai-regression-api/
├── requirements.txt         # Python dependencies
│
├── camera/                 # Main Flir abstraction classes to use throughout the project
│   ├── camera.py           # Core camera implementation and management
│   ├── camera_connection.py # Camera connection and communication handling
│   ├── camera_events.py    # Event handling system for camera operations
│   ├── camera_mock.py      # Mock camera implementation for testing
│   ├── camera_streaming.py # Camera streaming functionality
│   ├── camera_ui.py        # User interface related camera functions
│   ├── enumerations.py     # SDK enumerations and constants
│   ├── events.py           # Event system definitions
│   ├── image/              # Image handling and processing
│   │   └── image.py        # Core image processing functionality
│   ├── controls/           # Camera control implementations
│   ├── services/           # Camera-related services
│   ├── sensors/            # Camera sensor management
│   ├── interfaces/         # SDK interface implementations
│   ├── palettes/           # Thermal palette management
│   ├── image_processing/   # Advanced image processing utilities
│   ├── image_imports/      # Image import functionality
│   ├── helpers/            # Utility functions for camera operations
│   ├── fusion/             # Image fusion capabilities
│   └── playback/           # Video playback functionality
│
├── logs/                  # Application logs storage
│
├── utils/                 # Shared utilities
│   ├── LoggerConfig.py    # Centralized logger handler
│   ├── Other utilities    # Additional utility functions
│
├── ThermalCameraLibrary/  # Flir SDK integration
│
├── nginx/                 # Nginx server configuration
├── services/              # Additional service implementations
├── files/                 # File storage and management
├── config/                # Project configuration files
├── test/                  # Test suite and test files
├── serve.py              # Server startup script
├── start.bat             # Windows startup script
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose configuration
```

## 🔧 Key Components Description

### 📸 Camera Module (`camera/`)
The core module handling all Flir camera operations:
- Complete camera lifecycle management
- Real-time thermal image processing
- Event-driven architecture for camera operations
- Multiple imaging modes (thermal,visual,dual, fusion)
- Extensive palette management for thermal visualization
- Sensor data handling and processing
- Mock camera support for testing

### 🛠️ Utilities (`utils/`)
Core utility functions and configurations:
- Centralized logging system
- Resource pooling management
- Common utility functions
- Legacy video streaming support (deprecated)

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

## 🎯 Contexto Específico - Flir SDK Integration

### 📡 Integração Pythonnet

```python
"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: This module manages the thermal camera, including initialization, device discovery, and thermal image handling.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""


import json
import clr
import os

from ir_drone_stream import settings
import threading
import time
import numpy as np
from PIL import Image as PILImage
import io
import datetime

from utils import object_handler

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))
clr.AddReference("System")

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore
import Flir.Atlas.Image as Image  # type: ignore
import Flir.Atlas.Gigevision as Gigevision  # type: ignore

import System.Drawing  # type: ignore
from System import EventHandler  # type: ignore

import camera.camera_connection as camera_connection_manager
import camera.camera_logs as camera_log_manager
import camera.camera_ui as camera_ui_manager
import camera.controls.control as camera_control
import camera.camera_streaming as camera_streaming
import image.bitmap_handler as bitmap_handler

import camera.image.image as image_handler
from camera.services.data_extractor import DataExtractorService

# import camera.image.thermal_image as thermal_image_handler
import camera.image.alarms.alarm as alarm_handler
import camera.image.measurements.measurements as measurements_handler

class CameraManager:
    """
    The CameraManager class manages the thermal camera, including initialization, device discovery, and thermal image handling.
    """

    # TODO: Implementar um singleton para a classe CameraManager
    _instance = None
    _lock = threading.Lock()

```

### 🌡️ Documentação SDK

- **SDK Reference**: https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/index.html
- **Live Namespace**: https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live.html
- **Environment**: Windows 10 64-bit, Ubuntu Server, Docker, Chrome, Flir Cameras

---

**Lembre-se**:

- **Qualidade** não é negociável
- **Simplicidade** é fundamental  
- **Documentação** interna (docstring) é obrigatória
- **Documentação** externa (.md) é **mínima**
- **Código** em inglês, **output** em português
- **FastAPI** best practices sempre
- **PEP compliance** rigoroso
- **Flir SDK** integration seguindo padrões pythonnet
- Siga estas diretrizes **rigorosamente** para manter a excelência do projeto Tenesso
