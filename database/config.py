import os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}

def validate_config():
    missing = [key for key, value in DB_CONFIG.items() if value is None]
    if missing:
        raise ValueError(f"Missing DB configuration in .env: {', '.join(missing)}")