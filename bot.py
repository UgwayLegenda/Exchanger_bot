import asyncio
from aiogram import Bot, Dispatcher
from config.settings import BOT_TOKEN
from routers.handlers import commands, fsm
from middlewares.middleware import LoggingMiddleware

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.update.middleware(LoggingMiddleware())
    dp.include_router(commands.router)
    dp.include_router(fsm.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())