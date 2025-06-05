from aiogram.filters import BaseFilter
from aiogram.types import Message

class CurrencyCodeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        code = message.text.upper()
        return len(code) == 3 and code.isalpha()

class ConfirmationFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.lower() in ["да", "нет"]