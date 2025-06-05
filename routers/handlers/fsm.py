from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.filters import CurrencyCodeFilter

router = Router()

class SetCurrencyStates(StatesGroup):
    waiting_for_currency = State()
    waiting_for_confirmation = State()

@router.message(Command("setcurrency"))
async def set_currency_cmd(message: types.Message, state: FSMContext):
    await message.reply("Введите код валюты для установки по умолчанию (например, USD):")
    await state.set_state(SetCurrencyStates.waiting_for_currency)

@router.message(SetCurrencyStates.waiting_for_currency, CurrencyCodeFilter())
async def process_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()
    await state.update_data(currency=currency)
    await message.reply(f"Установить {currency} как валюту по умолчанию (из которой конвертируем)? (да/нет)")
    await state.set_state(SetCurrencyStates.waiting_for_confirmation)

@router.message(SetCurrencyStates.waiting_for_currency)
async def invalid_currency(message: types.Message):
    await message.reply("Неверный код валюты. Введите код из 3 букв.")

@router.message(SetCurrencyStates.waiting_for_confirmation)
async def confirm_currency(message: types.Message, state: FSMContext):
    confirmation = message.text.lower()
    if confirmation not in ["да", "нет"]:
        await message.reply("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    data = await state.get_data()
    currency = data["currency"]
    if confirmation == "да":
        await state.update_data(currency=currency)  # Сохраняем валюту в состоянии
        await message.reply(f"Валюта по умолчанию установлена на {currency}.")
    else:
        await message.reply("Отменено.")
    await state.set_state(None)  # Завершаем FSM