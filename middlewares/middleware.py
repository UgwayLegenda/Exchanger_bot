from aiogram import BaseMiddleware
from aiogram.types import Update
from utils.logger import logger

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        logger.info(f"Получено обновление: {event}")
        return await handler(event, data)