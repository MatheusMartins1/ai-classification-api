# Thermal Data Extractor Service

## Objetivo

Este serviço organiza a extração de dados térmicos da câmera FLIR para uso nas views principais do projeto, mantendo o código da view limpo e organizado.

## Uso na View

### Importação

```python
from camera.services.thermal_data_service import get_thermal_data_for_view, validate_thermal_data_request
```

### Extração Completa

```python
# Extrair todos os dados térmicos
result = get_thermal_data_for_view(thermal_image, "complete")
# ou simplesmente
result = get_thermal_data_for_view(thermal_image)  # "complete" é o padrão
```

### Extração Específica

```python
# Extrair apenas dados GPS
gps_data = get_thermal_data_for_view(thermal_image, "gps")

# Extrair apenas informações da câmera
camera_data = get_thermal_data_for_view(thermal_image, "camera")

# Extrair apenas parâmetros térmicos
thermal_params = get_thermal_data_for_view(thermal_image, "thermal_params")
```

### Tipos de Dados Disponíveis

- **`"complete"`** - Todos os dados disponíveis (padrão)
- **`"gps"`** - Informações GPS (coordenadas, altitude, timestamp)
- **`"camera"`** - Informações da câmera (modelo, número de série, especificações)
- **`"thermal_params"`** - Parâmetros térmicos (emissividade, distância, temperatura)
- **`"gas"`** - Dados de detecção e quantificação de gases
- **`"compass"`** - Informações de orientação (graus, roll, pitch)
- **`"zoom"`** - Informações de zoom
- **`"statistics"`** - Dados estatísticos (min, max, média, desvio padrão)
- **`"metadata"`** - Metadados básicos da imagem

### Validação

```python
# Validar tipo de dados antes da extração
is_valid, message = validate_thermal_data_request(data_to_extract)
if not is_valid:
    return JsonResponse({"error": message}, status=400)
```

### Exemplo de Uso na View

```python
@route("camera/data/thermal/", "get_thermal_data")
def get_thermal_data(request_or_message):
    from camera.services.thermal_data_service import get_thermal_data_for_view, validate_thermal_data_request
    
    # Obter parâmetros
    if hasattr(request_or_message, "GET"):
        thermal_image = camera.get_thermal_image()
        data_to_extract = request_or_message.GET.get("data_to_extract", "complete")
    else:
        payload = request_or_message.get("payload", {})
        thermal_image = camera.get_thermal_image()
        data_to_extract = payload.get("data_to_extract", "complete")
    
    # Validações
    if thermal_image is None:
        return JsonResponse({"error": "No thermal image available"}, status=404)
    
    is_valid, validation_message = validate_thermal_data_request(data_to_extract)
    if not is_valid:
        return JsonResponse({"error": validation_message}, status=400)
    
    # Extrair dados
    result = get_thermal_data_for_view(thermal_image, data_to_extract)
    
    # Retornar resposta
    status_code = 200 if result["status"] == "success" else 500
    return JsonResponse(result, status=status_code)
```

## Formato de Resposta

### Sucesso

```json
{
    "status": "success",
    "message": "Thermal data extracted successfully (gps)",
    "data": {
        "data_type": "gps",
        "data": {
            "IsValid": true,
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "Altitude": 10.5,
            ...
        }
    },
    "requested_type": "gps",
    "data_keys": ["data_type", "data"]
}
```

### Erro

```json
{
    "status": "error",
    "message": "Invalid data type 'invalid_type'. Available types: ['complete', 'gps', 'camera', ...]",
    "data": null,
    "requested_type": "invalid_type"
}
```

## Exemplos de Uso da API

### GET Request - Dados Completos

```
GET /camera/data/thermal/
GET /camera/data/thermal/?data_to_extract=complete
```

### GET Request - Dados Específicos

```
GET /camera/data/thermal/?data_to_extract=gps
GET /camera/data/thermal/?data_to_extract=camera
GET /camera/data/thermal/?data_to_extract=thermal_params
```

### Redis Message - Dados Completos

```json
{
    "payload": {
        "data_to_extract": "complete",
        "format": "Dual"
    }
}
```

### Redis Message - Dados Específicos

```json
{
    "payload": {
        "data_to_extract": "gps",
        "format": "Dual"
    }
}
```

## Benefícios

1. **View Limpa**: A view fica focada apenas na lógica de requisição/resposta
2. **Reutilização**: O serviço pode ser usado em outras views
3. **Manutenção**: Mudanças na extração de dados ficam centralizadas
4. **Validação**: Validação automática dos tipos de dados
5. **Formato Consistente**: Respostas padronizadas para sucesso/erro
6. **Fallback**: Se o serviço principal falhar, usa métodos de fallback
7. **Logging**: Logs automáticos para debugging

## Estrutura do Projeto

```
camera/
├── services/
│   ├── thermal_data_service.py          # Serviço principal
│   └── examples_thermal_service.py      # Exemplos de uso
└── image/
    └── resources/                        # Classes de recursos
        ├── gps_info.py
        ├── camera_info.py
        ├── thermal_parameters.py
        └── ...
```
