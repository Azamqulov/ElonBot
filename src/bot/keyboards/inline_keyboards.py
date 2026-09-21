from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.database.models import Category


def get_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(text=cat.name, callback_data=f"cat_{cat.id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Bekor qilish
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_salary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 UZS (So'm)", callback_data="salary_curr_uzs"),
                InlineKeyboardButton(text="🇺🇸 USD (Dollar)", callback_data="salary_curr_usd"),
            ],
            [
                InlineKeyboardButton(text="🤝 Kelishiladi", callback_data="salary_negotiable"),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action"),
            ],
        ]
    )


def get_currency_selected_keyboard(curr: str) -> InlineKeyboardMarkup:
    other_curr = "USD" if curr == "UZS" else "UZS"
    other_label = "🇺🇸 USD ga o'tish" if curr == "UZS" else "🇺🇿 UZS ga o'tish"
    other_callback = "salary_curr_usd" if curr == "UZS" else "salary_curr_uzs"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=other_label, callback_data=other_callback),
                InlineKeyboardButton(text="🤝 Kelishiladi", callback_data="salary_negotiable"),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action"),
            ],
        ]
    )


def get_skip_keyboard(step_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data=f"skip_{step_name}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")],
        ]
    )


def get_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yuborish (Moderatsiyaga)", callback_data="submit_job")],
            [InlineKeyboardButton(text="✏️ Qaytadan to'ldirish", callback_data="restart_job")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")],
        ]
    )


def get_announcement_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💼 Ishchi kerak (Vakansiya)", callback_data="type_job"),
            ],
            [
                InlineKeyboardButton(text="👨‍💼 Ish kerak (Rezyume / Frilans)", callback_data="type_resume"),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action"),
            ],
        ]
    )


def get_resume_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yuborish (Moderatsiyaga)", callback_data="submit_resume")],
            [InlineKeyboardButton(text="✏️ Qaytadan to'ldirish", callback_data="restart_resume")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")],
        ]
    )


def get_admin_moderation_keyboard(job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash va Post qilish", callback_data=f"admin_approve_{job_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject_{job_id}"),
            ]
        ]
    )


def get_admin_panel_keyboard(is_superadmin: bool = False, pending_count: int = 0) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=f"⏳ Kutayotgan e'lonlar ({pending_count})", callback_data="admin_btn_pending"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_btn_stats"),
        ],
        [
            InlineKeyboardButton(text="💳 To'lov sozlamalari", callback_data="admin_btn_payment_settings"),
        ],
    ]
    if is_superadmin:
        buttons.extend([
            [
                InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="sa_btn_add_admin"),
                InlineKeyboardButton(text="➖ Adminni o'chirish", callback_data="sa_btn_remove_admin"),
            ],
            [
                InlineKeyboardButton(text="📢 Kanal ulash", callback_data="sa_btn_add_channel"),
                InlineKeyboardButton(text="📡 Ulangan kanallar", callback_data="sa_btn_channels"),
            ],
            [
                InlineKeyboardButton(text="📁 Kategoriya qo'shish", callback_data="sa_btn_add_category"),
                InlineKeyboardButton(text="👥 Adminlar ro'yxati", callback_data="sa_btn_admins_list"),
            ],
        ])
    buttons.append([InlineKeyboardButton(text="❌ Yopish", callback_data="admin_btn_close")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_settings_keyboard(is_payment_enabled: bool = True) -> InlineKeyboardMarkup:
    status_text = "🟢 To'lov: Yoqilgan (Pullik)" if is_payment_enabled else "🔴 To'lov: O'chirilgan (Bepul)"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💵 Narxni o'zgartirish", callback_data="admin_pay_set_price"),
                InlineKeyboardButton(text="💳 Karta raqami", callback_data="admin_pay_set_card"),
            ],
            [
                InlineKeyboardButton(text="👤 Karta egasi", callback_data="admin_pay_set_holder"),
                InlineKeyboardButton(text=status_text, callback_data="admin_pay_toggle_status"),
            ],
            [
                InlineKeyboardButton(text="« Admin paneliga qaytish", callback_data="admin_btn_back"),
            ],
        ]
    )


def get_cancel_receipt_keyboard(job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ To'lovni bekor qilish", callback_data=f"cancel_receipt_{job_id}")],
        ]
    )


def get_admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="« Admin paneliga qaytish", callback_data="admin_btn_back")],
        ]
    )


def get_channels_manage_keyboard(channels) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        buttons.append([
            InlineKeyboardButton(text=f"📢 {ch.tg_channel_id}", callback_data=f"ignore_{ch.id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"sa_del_chan_{ch.id}"),
        ])
    buttons.append([InlineKeyboardButton(text="« Admin paneliga qaytish", callback_data="admin_btn_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admins_manage_keyboard(admins) -> InlineKeyboardMarkup:
    buttons = []
    for a in admins:
        name = a.full_name[:15]
        buttons.append([
            InlineKeyboardButton(text=f"👤 {name} ({a.tg_id})", callback_data=f"ignore_{a.id}"),
            InlineKeyboardButton(text="❌ O'chirish", callback_data=f"sa_del_admin_{a.tg_id}"),
        ])
    buttons.append([InlineKeyboardButton(text="« Admin paneliga qaytish", callback_data="admin_btn_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Support (@Musurmon_dev)", url="https://t.me/Musurmon_dev")],
        ]
    )
