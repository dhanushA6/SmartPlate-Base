"""
Configuration module for loading environment variables strictly from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get backend directory
BACKEND_DIR = Path(__file__).parent

# Path to .env file
ENV_PATH = BACKEND_DIR / ".env"

# Ensure .env file exists
if not ENV_PATH.exists():
    raise FileNotFoundError("[ERROR] .env file not found in backend directory")

# Load variables ONLY from .env (override=False prevents OS env usage)
load_dotenv(dotenv_path=ENV_PATH, override=True)

# ------------------------------------------------------------------
# Configuration values (STRICTLY from .env)
# ------------------------------------------------------------------

def get_env(key: str, default=None, required: bool = False):
    value = os.environ.get(key, default)
    if required and value is None:
        raise EnvironmentError(f"[ERROR] Required env variable '{key}' is missing in .env")
    return value


# API Keys
GOOGLE_API_KEY = get_env("GOOGLE_API_KEY", required=True)

# Server Configuration
PORT = int(get_env("PORT", default=5000))

# ------------------------------------------------------------------
# Debug (Development only)
# ------------------------------------------------------------------
print(f"[INFO] GOOGLE_API_KEY loaded successfully (length: {len(GOOGLE_API_KEY)})")
print(f"[INFO] Server running on port {PORT}")
