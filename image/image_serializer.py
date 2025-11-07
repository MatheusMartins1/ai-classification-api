import inspect
import json
import os

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System.Drawing")
# clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

# import Flir.Atlas.Gigevision as Gigevision  # type: ignore

clr.AddReference("System")
from Flir.Atlas.Image import VisualImage  # type: ignore
from System import DateTime, Guid  # type: ignore
from System.Collections.Generic import List  # type: ignore


class VisualImageSerializer:
    def __init__(self, visual_image):
        self.visual_image = visual_image
        self.attributes = {}
        self.method_results = {}

    def _convert_net_value(self, value):
        """Converte valores .NET para tipos compatíveis com JSON."""
        if value is None:
            return None
        # Tipos primitivos (int, float, string, bool)
        if isinstance(value, (int, float, str, bool)):
            return value
        # DateTime do .NET
        elif isinstance(value, DateTime):
            return value.ToString()  # Formato ISO: "yyyy-MM-ddTHH:mm:ss"
        # GUID do .NET
        elif isinstance(value, Guid):
            return str(value)
        # Listas/arrays do .NET
        elif hasattr(value, "__iter__"):
            return [self._convert_net_value(item) for item in value]
        # Objetos complexos (extrai o nome do tipo)
        else:
            return f"Object of type: {value.GetType().Name}"

    def serialize_to_json(self, filename):
        """Captura todos os atributos públicos e os salva em JSON."""
        # Lista de atributos públicos (excluindo métodos)
        attributes = []
        for attr_name in dir(self.visual_image):
            if not attr_name.startswith("__") and not inspect.ismethod(
                getattr(self.visual_image, attr_name)
            ):
                try:
                    value = getattr(self.visual_image, attr_name)
                    self.attributes[attr_name] = self._convert_net_value(value)
                except Exception as e:
                    self.attributes[attr_name] = f"Error accessing attribute: {str(e)}"

        # Salva em JSON
        with open(filename, "w") as f:
            json.dump(self.attributes, f, indent=4)

    def execute_methods(self):
        """Executa todos os métodos públicos (sem parâmetros) e registra os resultados."""
        for method_name in dir(self.visual_image):
            if method_name.startswith("get_") or method_name.startswith("set_"):
                continue  # Ignora getters/setters

            method = getattr(self.visual_image, method_name)
            if inspect.ismethod(method):
                # Verifica se o método não tem parâmetros obrigatórios
                params = inspect.signature(method).parameters
                if len(params) == 0:
                    try:
                        result = method()
                        self.method_results[method_name] = self._convert_net_value(
                            result
                        )
                    except Exception as e:
                        self.method_results[method_name] = (
                            f"Error executing method: {str(e)}"
                        )
