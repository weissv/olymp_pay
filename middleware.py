"""
Middleware module for logging all user interactions.
"""

import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware to log every user interaction.
    Logs commands, messages, callback queries, and state changes.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process and log event before passing to handler."""
        
        # Extract user info based on event type
        user_id = None
        username = "N/A"
        action = "Unknown"
        
        if isinstance(event, Message):
            user = event.from_user
            if user:
                user_id = user.id
                username = user.username or "N/A"
            
            # Determine action type
            if event.text:
                if event.text.startswith("/"):
                    action = f"Command: {event.text}"
                else:
                    action = f"Message: {event.text[:50]}{'...' if len(event.text) > 50 else ''}"
            elif event.contact:
                action = "Shared contact"
            elif event.photo:
                action = "Sent photo"
            elif event.document:
                action = "Sent document"
            elif event.successful_payment:
                action = f"Payment: {event.successful_payment.total_amount} {event.successful_payment.currency}"
            else:
                action = f"Content type: {event.content_type}"
                
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            if user:
                user_id = user.id
                username = user.username or "N/A"
            action = f"Callback: {event.data}"
        
        # Log the interaction
        if user_id:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] [{user_id}] [{username}] - {action}")
        
        # Continue to the handler
        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple throttling middleware to prevent spam.
    """
    
    def __init__(self, rate_limit: float = 0.5) -> None:
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum time between messages in seconds.
        """
        self.rate_limit = rate_limit
        self.user_last_action: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Check rate limit before processing."""
        import time
        
        user_id = None
        
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
        
        if user_id:
            current_time = time.time()
            last_action = self.user_last_action.get(user_id, 0)
            
            if current_time - last_action < self.rate_limit:
                # Too fast, ignore
                logger.debug(f"[{user_id}] - Rate limited")
                return None
            
            self.user_last_action[user_id] = current_time
        
        return await handler(event, data)
