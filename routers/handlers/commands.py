from aiogram import Router, types
from aiogram.filters import Command
from services.api_client import ExchangeRateAPI
from storage.database import Database
from aiogram.fsm.context import FSMContext

router = Router()
api = ExchangeRateAPI()
db = Database()


@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Добро пожаловать в бот-конвертер валют!")


@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(
        "Используйте /convert <сумма> <из> <в> для конвертации валют.\n"
        "Используйте /rates для просмотра текущих курсов.\n"
        "Используйте /history для просмотра истории конвертаций.\n"
        "Используйте /setcurrency для установки валюты по умолчанию (валюты, из которой конвертируем)."
    )


@router.message(Command("convert"))
async def convert_command(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 4:
        await message.reply("Использование: /convert <сумма> <из> <в>")
        return
    try:
        amount = float(parts[1])
    except ValueError:
        await message.reply("Сумма должна быть числом.")
        return
    from_curr = parts[2].upper()
    to_curr = parts[3].upper()
    if not (len(from_curr) == 3 and from_curr.isalpha()) or not (len(to_curr) == 3 and to_curr.isalpha()):
        await message.reply("Коды валют должны состоять из 3 букв.")
        return

    # Получаем валюту по умолчанию из FSM, если она установлена
    default_currency = await state.get_data()
    default_currency = default_currency.get("currency", "USD") if default_currency else "USD"
    if from_curr == "DEFAULT":
        from_curr = default_currency

    try:
        result = await api.convert_currency(amount, from_curr, to_curr)
        await db.add_conversion(message.from_user.id, amount, from_curr, to_curr, result)
        await message.reply(f"{amount} {from_curr} = {result:.2f} {to_curr}")
    except Exception as e:
        await message.reply(f"Ошибка конвертации: {str(e)}")


@router.message(Command("rates"))
async def rates_command(message: types.Message, state: FSMContext):
    try:
        # Используем валюту по умолчанию из FSM
        default_currency = await state.get_data()
        default_currency = default_currency.get("currency", "USD") if default_currency else "USD"
        rates = await api.fetch_rates(default_currency)
        rates_text = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
        await message.reply(f"Текущие курсы ({default_currency}):\n{rates_text}")
    except Exception as e:
        await message.reply(f"Ошибка: {str(e)}")


@router.message(Command("history"))
async def history_command(message: types.Message):
    history = await db.get_history(message.from_user.id)
    if not history:
        await message.reply("История конвертаций пуста.")
        return
    history_text = "\n".join(
        [f"{amount} {from_curr} -> {result} {to_curr} в {timestamp}" for amount, from_curr, to_curr, result, timestamp
         in history])
    await message.reply(f"Ваша история конвертаций:\n{history_text}")