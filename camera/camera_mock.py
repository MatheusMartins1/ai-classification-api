"""Mock camera for development"""

from datetime import datetime
import numpy as np


class CameraMock:
    def __init__(self):
        self.is_connected = True
        self.connection_status = "Connected"
        self.camera_control = CameraControlMock()
        self.measurements_handler = MeasurementsHandlerMock()
        self.alarms_handler = AlarmsHandlerMock()
        self.logger = MockLogger()
        self.image_obj_thermal = ThermalImageMock()
        self.image_obj_visual = VisualImageMock()

        # Inicializa com valores simulados
        self._init_time = datetime.now()
        self._frame_count = 0
        self._fps = 30

    def get_connection_status(self):
        return "Connected"

    def get_fps(self):
        return self._fps

    def get_frame_counter(self):
        return self._frame_count

    def get_lost_images(self):
        return 0

    def get_cpu_usage(self):
        return 25.5

    def get_memory_usage(self):
        return 512.3

    def get_running_time(self):
        delta = datetime.now() - self._init_time
        return str(delta).split(".")[0]

    def get_camera_info(self):
        return {
            "name": "FLIR Camera Mock",
            "model": "Mock X1000",
            "serial": "SN12345678",
            "firmware": "1.0.0",
        }

    def get_current_image(self, image_type="thermal"):
        """Simula uma imagem térmica ou visual"""
        self._frame_count += 1

        # Gera uma imagem simulada 640x480
        if image_type == "thermal":
            # Imagem térmica simulada (tons de cinza)
            img = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
            # Adiciona um ponto quente no centro
            img[220:260, 300:340] = 255
        else:
            # Imagem visual colorida simulada
            img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        return img

    def to_dict(self):
        return {
            "is_connected": self.is_connected,
            "connection_status": self.connection_status,
            "camera_info": self.get_camera_info(),
            "measurements": self.measurements_handler.to_string(),
            "alarms": self.alarms_handler.to_string(),
            "camera_control": self.camera_control.to_dict(),
            "stream_info": {
                "fps": self._fps,
                "frame_counter": self._frame_count,
                "lost_images": 0,
                "cpu_usage": self.get_cpu_usage(),
                "memory_usage": self.get_memory_usage(),
                "running_time": self.get_running_time(),
            },
        }


class CameraControlMock:
    def __init__(self):
        self.is_focus_supported = True
        self.is_nuc_supported = True
        self.is_hsm_supported = True
        self.is_recorder_supported = True
        self.camera_control_settings = CameraControlSettingsMock()
        self.camera_control_focus = CameraControlFocusMock()

    def to_dict(self):
        return {
            "is_focus_supported": self.is_focus_supported,
            "is_nuc_supported": self.is_nuc_supported,
            "is_hsm_supported": self.is_hsm_supported,
            "is_recorder_supported": self.is_recorder_supported,
            "settings": self.camera_control_settings.to_dict(),
            "focus": self.camera_control_focus.to_dict(),
        }


class CameraControlSettingsMock:
    def __init__(self):
        self.atmospheric_temperature = 20.0
        self.distance_unit = "meters"
        self.object_distance = 1.0
        self.object_emissivity = 0.95
        self.temperature_unit = "Celsius"

    def to_dict(self):
        return {
            "atmospheric_temperature": self.atmospheric_temperature,
            "distance_unit": self.distance_unit,
            "object_distance": self.object_distance,
            "object_emissivity": self.object_emissivity,
            "temperature_unit": self.temperature_unit,
        }


class CameraControlFocusMock:
    def __init__(self):
        self.is_focus_supported = True
        self.is_continuous_focus_enabled = False
        self.distance = 1.0
        self.speed = 100

    def to_dict(self):
        return {
            "is_focus_supported": self.is_focus_supported,
            "is_continuous_focus_enabled": self.is_continuous_focus_enabled,
            "distance": self.distance,
            "speed": self.speed,
        }


class ThermalImageMock:
    """Simula a interface da imagem térmica"""

    def __init__(self):
        self.Measurements = MeasurementsHandlerMock()
        self.Alarms = AlarmsHandlerMock()


class VisualImageMock:
    """Simula a interface da imagem visual"""

    def __init__(self):
        self.Width = 640
        self.Height = 480


class MeasurementsHandlerMock:
    def __init__(self):
        self._measurements = {
            "measurements": [
                {
                    "id": "rect1",
                    "name": "Rectangle Test",
                    "type": "rectangle",
                    "bounds": {"x": 100, "y": 100, "width": 200, "height": 150},
                },
                {
                    "id": "spot1",
                    "name": "Spot Test",
                    "type": "spot",
                    "bounds": {"x": 150, "y": 150},
                },
                {
                    "id": "line1",
                    "name": "Line Test",
                    "type": "line",
                    "bounds": {"x1": 100, "y1": 100, "x2": 200, "y2": 200},
                },
            ]
        }

    def get_all_measurements(self):
        return self._measurements["measurements"]

    def add_measurement(self, type, config):
        measurement = {
            "id": f"{type}{len(self._measurements['measurements'])+1}",
            "name": config.get("name", f"New {type}"),
            "type": type,
            "bounds": config,
        }
        self._measurements["measurements"].append(measurement)
        return measurement

    def update_measurement(self, id, config):
        for m in self._measurements["measurements"]:
            if m["id"] == id:
                m.update(config)
                return True
        return False

    def remove_measurement(self, id):
        self._measurements["measurements"] = [
            m for m in self._measurements["measurements"] if m["id"] != id
        ]
        return True

    def clear_all_measurements(self):
        self._measurements["measurements"] = []
        return True

    def to_string(self):
        return self._measurements


class AlarmsHandlerMock:
    def __init__(self):
        self._alarms = {
            "alarms": [
                {
                    "id": "alarm1",
                    "name": "Above Test",
                    "type": "above",
                    "threshold": 30.0,
                    "color": "Red",
                },
                {
                    "id": "alarm2",
                    "name": "Below Test",
                    "type": "below",
                    "threshold": 20.0,
                    "color": "Blue",
                },
            ]
        }

    def get_all_alarms(self):
        return self._alarms["alarms"]

    def add_alarm(self, alarm_type, config, collection_type="alarms"):
        alarm = {
            "id": f"alarm{len(self._alarms['alarms'])+1}",
            "name": config.get("name", f"New {alarm_type}"),
            "type": alarm_type,
            **config,
        }
        self._alarms["alarms"].append(alarm)
        return alarm

    def clear_all(self):
        self._alarms["alarms"] = []
        return True

    def to_string(self):
        return self._alarms


class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")

    def debug(self, msg):
        print(f"DEBUG: {msg}")
