import os
import platform
from dotenv import load_dotenv
from pathlib import Path

def load_env_file(BASE_DIR=None, use_prod=False):
    """Load environment variables from .env file."""
    if BASE_DIR is None:
        BASE_DIR = Path(__file__).resolve().parent.parent
    
    system_user = os.getlogin()
    is_dev_environment = platform.system() == "Windows" and system_user in [
        "Matheus",
        "Dev",
        "Matheus Martins",
    ]
    
    if use_prod or not is_dev_environment:
        try:
            from utils import update_redis_password
            update_redis_password.main()
        except Exception as e:
            print(f"Erro: {e}")

    load_dotenv(os.path.join(BASE_DIR, ".env.runner"))

    # Load environment variables
    if is_dev_environment and not use_prod:
        dotenv_path = os.path.join(BASE_DIR, ".env.dev")
    if use_prod or not is_dev_environment:
        dotenv_path = os.path.join(BASE_DIR, ".env.prod")
    
    load_dotenv(dotenv_path, override=True)
    print(
        f"Loading .env for {dotenv_path} for user: {system_user} and backend: {os.getenv('BACKEND_HOST')}"
    )
    
    return
