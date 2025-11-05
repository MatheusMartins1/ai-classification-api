# =================== IMPORTS ===================
import json
import psutil
import datetime
import logging
import sys
import os
from pytz import timezone
import warnings
from colorama import init as colorama_init, Fore, Style
from typing import Optional, Dict, Set

# ============== GLOBALS & INIT ================
warnings.simplefilter(action="ignore", category=FutureWarning)
colorama_init(autoreset=True)
today = datetime.datetime.now(tz=timezone("America/Sao_Paulo"))
system_process = psutil.Process(pid=os.getpid())
_LOGGER_REGISTRY: Dict[str, logging.Logger] = {}
_LOGFILE_REGISTRY: Set[str] = set()


# ============== UTILS =========================
def format_error(error):
    return str(error).replace("\n", "").replace("\r\n", "")


def format_bytes(byte):
    if byte <= 1024:
        return f"{round(byte, 2)}.00 B"
    elif byte <= 1024**2:
        return f"{round(byte / 1024, 2)} KB"
    elif byte <= 1024**3:
        return f"{round(byte / (1024 * 1024), 2)} MB"
    else:
        return f"{round(byte / (1024 * 1024 * 1024), 2)} GB"

def get_usage():
    global system_process
    cpu = system_process.cpu_percent() / psutil.cpu_count()
    memory = format_bytes(system_process.memory_info().rss)
    return [cpu, memory]

def get_detailed_usage():
    """
    Get CPU and memory usage for current process and its threads.
    Focuses only on the main process and associated threads.
    """
    global system_process
    
    try:
        # Refresh process info
        system_process = psutil.Process(pid=os.getpid())
        
        # CPU usage (normalized by CPU count)
        cpu = system_process.cpu_percent() / psutil.cpu_count()
        cpu_str = f"{cpu:.2f}%"
        
        # Memory info for current process only
        memory_info = system_process.memory_info()
        memory_rss = format_bytes(memory_info.rss)  # Resident Set Size (physical memory)
        memory_vms = format_bytes(memory_info.vms)  # Virtual Memory Size
        
        # Thread count for current process
        thread_count = system_process.num_threads()
        
        # Memory usage string with process-specific info
        memory_str = f"{memory_rss}(RSS)|{memory_vms}(VMS)|{thread_count}T"
        
        return [cpu_str, memory_str]
        
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        # Fallback if process access fails
        return ["0.00%", "0B(RSS)|0B(VMS)|0T"]


def get_streaming_system_usage():
    """
    Get detailed usage information specifically for streaming system threads.
    Returns memory and thread info focused on the streaming components.
    """
    global system_process
    
    try:
        # Refresh process info
        system_process = psutil.Process(pid=os.getpid())
        
        # CPU and memory for main process
        cpu_percent = system_process.cpu_percent()
        memory_info = system_process.memory_info()
        
        # Get thread information
        threads = system_process.threads()
        total_threads = len(threads)
        
        # Filter threads related to streaming (by name patterns if available)
        streaming_threads = 0
        try:
            import threading
            active_threads = threading.enumerate()
            streaming_thread_names = [
                "ImageDataStreamThread", 
                "AsyncDataExtractor", 
                "ThreadPoolExecutor",
                "FeedBroadcaster"
            ]
            
            for thread in active_threads:
                if any(name in thread.name for name in streaming_thread_names):
                    streaming_threads += 1
                    
        except Exception:
            streaming_threads = 0
        
        return {
            "process_id": system_process.pid,
            "cpu_percent": cpu_percent,
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "memory_rss_formatted": format_bytes(memory_info.rss),
            "memory_vms_formatted": format_bytes(memory_info.vms),
            "total_threads": total_threads,
            "streaming_threads": streaming_threads,
            "memory_percent": system_process.memory_percent()
        }
        
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return {
            "process_id": 0,
            "cpu_percent": 0.0,
            "memory_rss": 0,
            "memory_vms": 0,
            "memory_rss_formatted": "0B",
            "memory_vms_formatted": "0B",
            "total_threads": 0,
            "streaming_threads": 0,
            "memory_percent": 0.0
        }


def get_logger_level(level_name: str) -> int:
    if level_name == "INFO":
        return logging.INFO
    elif level_name == "DEBUG":
        return logging.DEBUG
    elif level_name == "WARNING":
        return logging.WARNING
    elif level_name == "ERROR":
        return logging.ERROR
    elif level_name == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO  # Default fallback


# ============== FORMATTER =====================
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        msg = super().format(record)
        return f"{color}{msg}{Style.RESET_ALL}"


# ============== CONTEXT FILTER ================
class ContextFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.start_time = datetime.datetime.now(tz=timezone("America/Sao_Paulo"))
        self.last_time = self.start_time

    def filter(self, record):
        cpu, memory = get_usage()
        record.cpu = str(cpu)
        record.memory = memory
        now = datetime.datetime.now(tz=timezone("America/Sao_Paulo"))
        record.elapsed = now - self.start_time
        record.delta = now - self.last_time
        self.last_time = now
        return True


# ============== LOGGER CONFIG =================
class LoggerConfig:
    """
    Central logger configuration for the project. Use LoggerConfig.get_logger(name) to get a logger instance.
    Automatically applies colorama formatting for console output.
    """

    logger_name = "root"
    formatter = None
    # Global log format string for all handlers
    # LOG_FORMAT = "%(asctime)s|%(levelname)s|%(prefix)s|%(lineno)d|%(name)s|%(funcName)s|%(cpu)s|%(memory)s|%(message)s"

    @staticmethod
    def get_logger_format():
        """
        Returns the global log format string.
        """
        return f"%(asctime)s|%(levelname)s|{LoggerConfig.logger_name}|%(lineno)d|%(name)s|%(funcName)s|%(message)s"
        # return f"%(asctime)s|%(levelname)s|{LoggerConfig.logger_name}|%(lineno)d|%(name)s|%(funcName)s|%(cpu)s|%(memory)s|%(message)s"

    @staticmethod
    def get_logger(name: Optional[str] = None, level_name: str = "INFO") -> logging.Logger:
        global _LOGGER_REGISTRY
        logger_name = name if name is not None else "root"
        LoggerConfig.logger_name = logger_name
        if logger_name in _LOGGER_REGISTRY:
            return _LOGGER_REGISTRY[logger_name]
        logger = logging.getLogger(logger_name)
        logger.setLevel(get_logger_level(level_name))  # Set logger level based on level_name parameter
        # Remove duplicate handlers
        if not hasattr(logger, "_colorama_configured") or not getattr(
            logger, "_colorama_configured"
        ):
            for h in list(logger.handlers):
                logger.removeHandler(h)
            stream_handler = logging.StreamHandler(sys.stdout)
            formatter = ColorFormatter(LoggerConfig.get_logger_format())
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(get_logger_level(level_name))
            logger.addHandler(stream_handler)
            logger.addFilter(ContextFilter())
            LoggerConfig.supress_external_loggers()
            setattr(logger, "_colorama_configured", True)
        _LOGGER_REGISTRY[logger_name] = logger
        return logger

    @staticmethod
    def supress_external_loggers():
        logging.getLogger("boto3").setLevel(logging.WARNING)
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("tableauserverclient ").setLevel(logging.WARNING)

    @staticmethod
    def add_file_handler(
        logger: logging.Logger, log_filename: str, level_name: str = "INFO"
    ) -> None:
        global _LOGFILE_REGISTRY
        if log_filename in _LOGFILE_REGISTRY:
            return
        for h in list(logger.handlers):
            if isinstance(h, logging.FileHandler) and getattr(
                h, "baseFilename", None
            ) == os.path.abspath(log_filename):
                return
        level = get_logger_level(level_name)
        
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        formatter = logging.Formatter(LoggerConfig.get_logger_format())
        
        file_handler.setFormatter(formatter)
        logger.setLevel(level)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
        
        _LOGFILE_REGISTRY.add(log_filename)

    @staticmethod
    def add_file_logger(
        name=None, filename=None, dir_name=None, prefix=None, level_name="INFO"
    ):  # prefix is optional for flexibility
        """
        Cria e configura um logger com file handler, criando diretório e nome de arquivo automaticamente se necessário.
        Retorna o logger pronto para uso.
        """
        logger = LoggerConfig.get_logger(name, level_name)
        if dir_name is None:
            dir_name = os.path.dirname(sys.argv[0].strip())
        log_file_path = os.path.basename(sys.argv[0].strip().replace(" ", ""))
        exec_file = os.path.splitext(log_file_path)[0]
        filename = filename if filename else exec_file
        filename = f"{prefix if prefix else name}_{today.strftime('%Y-%m-%d')}.log"
        log_filename = os.path.join(dir_name, "logs", filename)
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        LoggerConfig.add_file_handler(logger, log_filename)
        logger.info("START")
        return logger
