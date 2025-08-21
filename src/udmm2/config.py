import os
from typing import Optional

def get_api_key(service: str) -> Optional[str]:
    """
    Retrieves an API key from environment variables.
    Service names should be like 'GOOGLE_API_KEY'.
    """
    return os.environ.get(service.upper() + "_API_KEY")

def set_api_key(service: str, key: str):
    """
    Sets an API key as an environment variable for the current process.
    Note: This is not persistent across server restarts. A more robust
    solution would write to a .env file or a secure vault.
    """
    os.environ[service.upper() + "_API_KEY"] = key
    return True
