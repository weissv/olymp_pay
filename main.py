"""
Main entry point for the Olympiad Registration Bot.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, LOG_DATE_FORMAT, LOG_FILE, LOG_FORMAT
from db import init_db
from handlers import router
from middleware import LoggingMiddleware, ThrottlingMiddleware


def setup_logging() -> None:
    """Configure logging to file and console."""
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Reduce noise from aiogram and other libraries
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


async def on_startup(bot: Bot) -> None:
    """Actions to perform on bot startup."""
    logger = logging.getLogger(__name__)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username} (ID: {bot_info.id})")


async def on_shutdown(bot: Bot) -> None:
    """Actions to perform on bot shutdown."""
    logger = logging.getLogger(__name__)
    logger.info("Bot is shutting down...")
    
    # Close bot session
    await bot.session.close()
    logger.info("Bot session closed")


async def main() -> None:
    """Main function to run the bot."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Validate configuration
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Please set it in .env file.")
        sys.exit(1)
    
    # Initialize bot with default properties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Initialize dispatcher with memory storage for FSM
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    
    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Include routers
    dp.include_router(router)
    
    logger.info("Starting bot polling...")
    
    try:
        # Start polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
