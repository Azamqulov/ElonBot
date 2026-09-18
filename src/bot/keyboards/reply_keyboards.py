from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🆕 Yangi vakansiya berish")],
        [KeyboardButton(text="📋 Mening e'lonlarim"), KeyboardButton(text="ℹ️ Bot haqida")],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡️ Admin paneli")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_contact_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamimni ulashish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
