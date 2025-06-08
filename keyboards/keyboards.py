from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data="/start")]
    ])
    return keyboard

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Конвертация валют", callback_data="/convert")],
            [InlineKeyboardButton(text="Справка", callback_data="/help")],
            [InlineKeyboardButton(text="История запросов", callback_data="/history")],
            [InlineKeyboardButton(text="Курсы валют", callback_data="/rates")]
        ]
    )
    return keyboard