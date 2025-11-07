import threading
import time
from typing import Callable, Any, Optional, Union
from enum import Enum
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="polling", filename=None, dir_name=None, prefix=None
)


class PollingResult(Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"


class PollingManager:
    def __init__(self):
        self._threads = {}
        self._stop_events = {}

    def poll_until_condition(
        self,
        condition_func: Callable[[], bool],
        interval: float = 1.0,
        max_wait: float = 30.0,
        error_handler: Optional[Callable[[Exception], bool]] = None,
    ) -> PollingResult:
        """
        Polling simples que aguarda até que uma condição seja verdadeira.

        Args:
            condition_func: Função que retorna True quando a condição for atendida
            interval: Intervalo entre verificações em segundos
            max_wait: Tempo máximo de espera em segundos
            error_handler: Função opcional para tratar erros. Retorna True para continuar, False para parar

        Returns:
            PollingResult: SUCCESS, TIMEOUT ou ERROR
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                # BUG: 
                if condition_func:
                    return PollingResult.SUCCESS
            except Exception as e:
                logger.error(f"Error in polling condition: {e}")

                if error_handler:
                    try:
                        should_continue = error_handler(e)
                        if not should_continue:
                            return PollingResult.ERROR
                    except Exception as handler_error:
                        logger.error(f"Error in error handler: {handler_error}")
                        return PollingResult.ERROR
                else:
                    return PollingResult.ERROR

            time.sleep(interval)

        return PollingResult.TIMEOUT

    def start_polling(
        self,
        callback: Callable[[], Any],
        name: str,
        interval: float = 30.0,
        max_retries: Optional[int] = None,
        stop_condition: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """
        Start polling contínuo com callback em thread separada (método original).
        """
        # Stop existing polling with same name if exists
        self.stop_polling(name)

        # Create stop event
        stop_event = threading.Event()
        self._stop_events[name] = stop_event

        # Create and start thread
        thread = threading.Thread(
            target=self._polling_loop,
            args=(callback, name, interval, max_retries, stop_condition, stop_event),
            daemon=True,
        )
        self._threads[name] = thread
        thread.start()

        logger.info(f"Started {name} polling every {interval} seconds")

    def _polling_loop(
        self,
        callback: Callable[[], Any],
        name: str,
        interval: float,
        max_retries: Optional[int],
        stop_condition: Optional[Callable[[Any], bool]],
        stop_event: threading.Event,
    ) -> None:
        """Internal polling loop que roda em thread separada"""
        retry_count = 0

        while not stop_event.is_set():
            try:
                result = callback()

                if stop_condition and stop_condition(result):
                    logger.info(f"{name} polling stopped due to stop condition")
                    break

                retry_count = 0

            except Exception as e:
                logger.error(f"Error in {name} polling: {e}")
                retry_count += 1

                if max_retries and retry_count >= max_retries:
                    logger.error(f"{name} polling stopped after {max_retries} retries")
                    break

            if not stop_event.wait(timeout=interval):
                continue
            else:
                break

        logger.info(f"{name} polling stopped")

        # Clean up
        if name in self._threads:
            del self._threads[name]
        if name in self._stop_events:
            del self._stop_events[name]

    def stop_polling(self, name: str) -> None:
        """Stop polling para uma task específica"""
        if name in self._stop_events:
            self._stop_events[name].set()

        if name in self._threads:
            thread = self._threads[name]
            if thread.is_alive():
                thread.join(timeout=5.0)

    def stop_all_polling(self) -> None:
        """Stop all polling tasks"""
        for name in list(self._stop_events.keys()):
            self.stop_polling(name)

    def is_polling(self, name: str) -> bool:
        """Check if uma polling task está rodando"""
        return name in self._threads and self._threads[name].is_alive()
