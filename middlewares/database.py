from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        # Transfering session to middleware
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Instance 'session' allows to do requests towards database
        async with self.session_pool() as session:
            # Every router has access to THIS session now
            data['session'] = session
            return await handler(event, data)