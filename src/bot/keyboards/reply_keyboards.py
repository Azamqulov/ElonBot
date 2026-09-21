from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🆕 Yangi e'lon berish")],
        [KeyboardButton(text="📋 Mening e'lonlarim"), KeyboardButton(text="ℹ️ Bot haqida")],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡️ Admin paneli")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_contact_keyboard(phone: str | None = None, username: str | None = None) -> ReplyKeyboardMarkup:
    keyboard = []
    
    # 1. Agar foydalanuvchining telefon raqami bazada mavjud bo'lsa
    if phone:
        btn_text = f"📱 {phone}"
        if username:
            btn_text += f" | @{username}"
        keyboard.append([KeyboardButton(text=btn_text)])
    
    # 2. Telegram orqali bir bosishda telefon raqamini ulashish tugmasi
    keyboard.append([KeyboardButton(text="📱 Telefon raqamimni ulashish", request_contact=True)])
    
    # 3. Bekor qilish tugmasi
    keyboard.append([KeyboardButton(text="❌ Bekor qilish")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

