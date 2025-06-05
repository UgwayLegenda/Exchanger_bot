import aiosqlite
import asyncio
from datetime import datetime
from utils.logger import logger

class Database:
    def __init__(self, db_path: str = "storage/bot.db"):
        self.db_path = db_path
        self._init_db()

    async def _init_db(self):
        """Инициализация базы данных и создание таблицы."""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    from_currency TEXT,
                    to_currency TEXT,
                    result REAL,
                    timestamp TEXT
                )
            """)
            await conn.commit()
            logger.info("База данных инициализирована")

    async def add_conversion(self, user_id: int, amount: float, from_currency: str, to_currency: str, result: float):
        """Добавление записи о конвертации."""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                INSERT INTO conversions (user_id, amount, from_currency, to_currency, result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, amount, from_currency, to_currency, result, datetime.now().isoformat()))
            await conn.commit()
            logger.info(f"Добавлена конвертация для пользователя {user_id}: {amount} {from_currency} -> {result} {to_currency}")

    async def get_history(self, user_id: int) -> list:
        """Получение истории конвертаций пользователя."""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT amount, from_currency, to_currency, result, timestamp FROM conversions WHERE user_id = ?", (user_id,))
            history = await cursor.fetchall()
            logger.info(f"Получена история для пользователя {user_id}: {len(history)} записей")
            return history

    def __init__(self, db_path: str = "storage/bot.db"):
        self.db_path = db_path
        asyncio.run(self._init_db())