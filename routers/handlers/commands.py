from aiogram import Router, types
from aiogram import F
from aiogram.filters import Command
from services.api_client import ExchangeRateAPI
from storage.database import Database
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import get_start_keyboard, get_main_menu_keyboard
from utils import logger

router = Router()
api = ExchangeRateAPI()
db = Database()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "/help")
async def help_command(callback: types.CallbackQuery):
    await callback.message.answer(
        "Используйте /convert <сумма> <из> <в> для конвертации валют.\n"
        "Используйте /rates для просмотра текущих курсов.\n"
        "Используйте /history для просмотра истории конвертаций.\n"
        "Используйте /setcurrency для установки валюты по умолчанию (валюты, из которой конвертируем).",
        reply_markup=get_main_menu_keyboard()

    )


@router.callback_query(F.data == "/convert")
async def handle_convert_button(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.answer(
        "Введите данные для конвертации в формате:\n"
        "<сумма> <из валюты> <в валюту>\n"
        "Например: 100 USD EUR"
    )

    await state.set_state("waiting_for_conversion_data")


@router.callback_query(F.data == "/history")
async def handle_history_button(callback: types.CallbackQuery):
    try:
        history = await db.get_history(callback.from_user.id)
        if not history:
            await callback.message.answer(
                text="История конвертаций пуста.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            history_text = "\n".join(
                f"{conv['amount']} {conv['from_currency']} -> {conv['result']:.2f} {conv['to_currency']} в {conv['timestamp']}"
                for conv in history
            )
            await callback.message.answer(
                text=f"Ваша история конвертаций:\n{history_text}",
                reply_markup=get_main_menu_keyboard()
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {str(e)}")
        await callback.message.answer(
            text=f"Ошибка: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data == "/rates")
async def handle_rates_button(callback: types.CallbackQuery, state: FSMContext):
    try:
        default_currency = (await state.get_data()).get("currency", "USD")

        rates = await api.fetch_rates(default_currency)
        rates_text = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])

        await callback.message.answer(f"Текущие курсы ({default_currency}):\n{rates_text}",
                                      reply_markup=get_main_menu_keyboard())



    except Exception as e:
        await callback.message.answer(f"Ошибка: {str(e)}",
                                      reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "/convert")
async def handle_convert_button(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите данные для конвертации в формате:\n"
        "<сумма> <из валюты> <в валюту>\n"
        "Например: 100 USD EUR"
    )
    await state.set_state("waiting_for_conversion_data")


@router.message(StateFilter("waiting_for_conversion_data"))
async def handle_conversion_input(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("Неверный формат. Пример: 100 USD EUR")
            return

        amount, from_currency, to_currency = parts
        amount = float(amount)
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if amount <= 0:
            await message.answer("Сумма должна быть больше 0")
            return

        rates = await api.fetch_rates(from_currency)
        if not isinstance(rates, dict):
            raise ValueError(f"Некорректный формат данных от API: {rates}")

        if to_currency not in rates:
            await message.answer(f"Валюта {to_currency} не найдена")
            return

        if not isinstance(rates[to_currency], (int, float)):
            raise ValueError(f"Некорректный курс для {to_currency}: {rates[to_currency]}")

        converted_amount = amount * rates[to_currency]

        success = await db.add_conversion(
            user_id=message.from_user.id,
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            result=converted_amount
        )
        if not success:
            await message.answer("Ошибка при сохранении конвертации в базу данных")
            return

        result = (
            f"Ваша операция: {amount} {from_currency} = {converted_amount:.2f} {to_currency}\n"
            f"Текущий курс валют: 1 {from_currency} = {rates[to_currency]:.4f} {to_currency}"
        )

        await message.answer(result, reply_markup=get_main_menu_keyboard())
    except ValueError as ve:
        await message.answer(f"Неверный формат суммы или данных: {str(ve)}")
    except Exception as e:
        logger.error(f"Ошибка при конвертации: {str(e)}")
        await message.answer(f"Произошла ошибка: {str(e)}")
    finally:
        await state.clear()
