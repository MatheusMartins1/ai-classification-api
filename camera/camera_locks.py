# camera/camera_locks.py
from threading import Lock
from functools import wraps
import threading
from typing import Optional, Dict

class CameraLockManager:
    """
    Gerenciador centralizado de locks para a câmera.
    Implementa padrão hierárquico para evitar deadlocks.
    """
    def __init__(self):
        self._locks = {
            'memory': threading.RLock(),      # Lock de mais alto nível
            'camera': threading.RLock(),      # Lock de dispositivo
            'image': threading.RLock(),       # Lock de imagem
            'stream': threading.RLock(),      # Lock de streaming
            'control': threading.RLock(),     # Lock de controles
            'events': threading.RLock(),     # Lock de eventos
            'service': threading.RLock(),     # Lock de service
            
        }
        self._lock_order = ['memory', 'camera', 'image', 'stream', 'control', 'events', 'service']
        self._owner_threads: Dict[str, Optional[int]] = {k: None for k in self._locks}
        
    def acquire_lock(self, lock_name: str) -> bool:
        """Adquire lock respeitando hierarquia"""
        if lock_name not in self._locks:
            raise ValueError(f"Lock {lock_name} não existe")
            
        current_thread = threading.get_ident()
        current_idx = self._lock_order.index(lock_name)
        
        # Verifica se thread já possui locks de nível mais baixo
        for lower_lock in self._lock_order[current_idx+1:]:
            if self._owner_threads[lower_lock] == current_thread:
                raise RuntimeError(
                    f"Violação de hierarquia: tentando adquirir {lock_name} "
                    f"enquanto possui {lower_lock}"
                )
        
        lock = self._locks[lock_name]
        acquired = lock.acquire(blocking=True, timeout=5.0)
        if acquired:
            self._owner_threads[lock_name] = current_thread
        return acquired
        
    def release_lock(self, lock_name: str) -> None:
        """Libera lock"""
        if lock_name not in self._locks:
            raise ValueError(f"Lock {lock_name} não existe")
            
        self._locks[lock_name].release()
        self._owner_threads[lock_name] = None

    def __call__(self, lock_name: str):
        """Permite uso como context manager"""
        return CameraLockContext(self, lock_name)

class CameraLockContext:
    """Context manager para locks da câmera"""
    def __init__(self, manager: CameraLockManager, lock_name: str):
        self.manager = manager
        self.lock_name = lock_name
        
    def __enter__(self):
        if not self.manager.acquire_lock(self.lock_name):
            raise TimeoutError(f"Timeout acquiring {self.lock_name} lock")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.release_lock(self.lock_name)

# Instância global
camera_locks = CameraLockManager()

# # Decorator para proteção de memória
# def protect_memory_access(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         with camera_locks('memory'):
#             return func(*args, **kwargs)
#     return wrapper

# # Uso na classe CameraManager
# class CameraManager:
#     def __init__(self):
#         self._locks = camera_locks  # Use o gerenciador centralizado
        
#     def process_image(self):
#         with self._locks('camera'):
#             with self._locks('image'):
#                 # Processamento seguro
#                 pass

# # Uso nas views
# @protect_memory_access
# def camera_view(request):
#     with camera_locks('camera'):
#         result = camera.get_current_image()
