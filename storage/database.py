import aiosqlite
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "storage/bot.db"):
        self.db_path = db_path
        self.conn = None
        self.db_folder = Path("storage")
        self.db_folder.mkdir(exist_ok=True, parents=True)

    async def _init_db(self):
        """Инициализация таблиц в базе данных."""
        try:
            if not self.conn or not await self._check_connection():
                self.conn = await aiosqlite.connect(self.db_path)
                self.conn.row_factory = aiosqlite.Row  # Для возврата строк как словарей
            await self.conn.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    from_currency TEXT NOT NULL,
                    to_currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    result REAL NOT NULL,
                    timestamp TEXT NOT NULL  -- Изменили тип на TEXT для хранения форматированного времени
                )
            """)
            await self.conn.commit()
            logger.info("Таблица conversions успешно создана/проверена")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
            raise

    async def connect(self):
        """Явное подключение к БД."""
        try:
            if not self.conn or not await self._check_connection():
                self.conn = await aiosqlite.connect(self.db_path)
                self.conn.row_factory = aiosqlite.Row
                logger.info("Подключение к БД установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    async def _check_connection(self):
        """Проверка активности подключения."""
        try:
            async with self.conn.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            return True
        except Exception:
            return False

    async def add_conversion(self, user_id: int, amount: float, from_currency: str, to_currency: str, result: float):
        """Добавление записи о конвертации."""
        try:

            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError(f"Некорректный user_id: {user_id}")
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValueError(f"Некорректная сумма: {amount}")
            if not isinstance(from_currency, str) or not isinstance(to_currency, str):
                raise ValueError(f"Некорректные валюты: {from_currency}, {to_currency}")
            if not isinstance(result, (int, float)) or result < 0:
                raise ValueError(f"Некорректный результат: {result}")

            await self.connect()

            local_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            async with self.conn.execute("""
                INSERT INTO conversions (user_id, amount, from_currency, to_currency, result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, amount, from_currency, to_currency, result, local_timestamp)) as cursor:
                await self.conn.commit()
                logger.info(f"Добавлена конвертация: {amount} {from_currency} → {result:.2f} {to_currency} для user_id={user_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении конвертации: {e}")
            if self.conn:
                await self.conn.rollback()
            return False

    async def get_history(self, user_id: int, limit: int = 20):
        """Получение истории конвертаций."""
        try:
            await self.connect()

            async with self.conn.execute("""
                SELECT amount, from_currency, to_currency, result, timestamp
                FROM conversions 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                logger.info(f"Получена история для user_id={user_id}: {len(rows)} записей")
                return [dict(row) for row in rows]  # Преобразуем строки в словари
        except Exception as e:
            logger.error(f"Ошибка при получении истории: {e}")
            return []

    async def close(self):
        """Закрытие соединения с БД."""
        try:
            if self.conn:
                await self.conn.close()
                logger.info("Соединение с БД закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии БД: {e}")
