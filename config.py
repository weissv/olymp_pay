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
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")  # Payme provider token

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
OLYMPIAD_CURRENCY = os.getenv("OLYMPIAD_CURRENCY", "UZS")

# Logging Configuration
LOG_FILE = BASE_DIR / "bot.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Validation Constants
MIN_GRADE = 1
MAX_GRADE = 11
