import aiohttp
import asyncio
from datetime import datetime, timedelta
from config.settings import EXCHANGE_RATE_API_KEY
from utils.logger import logger

class ExchangeRateAPI:
    def __init__(self):
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.api_key = EXCHANGE_RATE_API_KEY
        self.cache = {}
        self.cache_expiry = {}

    async def fetch_rates(self, base_currency: str = "USD") -> dict:
        if base_currency in self.cache and self.cache_expiry.get(base_currency, datetime.min) > datetime.now():
            logger.info(f"Использование кэшированных данных для {base_currency}")
            return self.cache[base_currency]

        url = f"{self.base_url}/{self.api_key}/latest/{base_currency}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка API: {response.status}")
                        raise Exception(f"Ошибка API: {response.status}")
                    data = await response.json()
                    if data["result"] != "success":
                        logger.error(f"API вернул ошибку: {data.get('error-type', 'Неизвестная ошибка')}")
                        raise Exception(f"API вернул ошибку: {data.get('error-type', 'Неизвестная ошибка')}")
                    rates = data["conversion_rates"]
                    self.cache[base_currency] = rates
                    self.cache_expiry[base_currency] = datetime.now() + timedelta(hours=1)
                    logger.info(f"Получены курсы для {base_currency}")
                    return rates
            except asyncio.TimeoutError:
                logger.error("Таймаут запроса к API")
                raise Exception("Таймаут запроса к API")
            except Exception as e:
                logger.error(f"Ошибка запроса к API: {str(e)}")
                raise Exception(f"Ошибка запроса к API: {str(e)}")
        raise Exception("Не удалось получить курсы валют")  # Явное исключение, если ничего не возвращено

    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        rates = await self.fetch_rates(from_currency)
        if to_currency not in rates:
            logger.error(f"Неподдерживаемая валюта: {to_currency}")
            raise ValueError(f"Валюта {to_currency} не поддерживается")
        if not isinstance(rates[to_currency], (int, float)):
            logger.error(f"Некорректное значение для {to_currency}: {rates[to_currency]}")
            raise ValueError(f"Значение для {to_currency} не является числом")
        result = amount * rates[to_currency]
        logger.info(f"Конвертировано {amount} {from_currency} в {result:.2f} {to_currency}")
        return result
