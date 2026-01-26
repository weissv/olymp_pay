"""
Configuration module for the Olympiad Registration Bot.
Loads environment variables and defines constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Payme Configuration
PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID", "")  # Merchant ID from Payme Business
PAYME_SECRET_KEY = os.getenv("PAYME_SECRET_KEY", "")    # Secret Key from Payme Business

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/olympiad.db")

# Fix postgres:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Admin Configuration
ADMIN_IDS: list[int] = [
    int(admin_id.strip()) 
    for admin_id in os.getenv("ADMIN_IDS", "").split(",") 
    if admin_id.strip().isdigit()
]

# Payment Configuration
OLYMPIAD_PRICE = int(os.getenv("OLYMPIAD_PRICE", "50000"))  # Price in tiyin (500.00 UZS = 50000 tiyin)

# Logging Configuration
LOG_FILE = BASE_DIR / "bot.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Validation Constants
MIN_GRADE = 1
MAX_GRADE = 8  # Changed from 11 to 8
