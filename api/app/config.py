import os
from dotenv import load_dotenv
from pathlib import Path

# Determine the path to the .env file in the project's root directory
# (one level up from this file's 'app' directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")