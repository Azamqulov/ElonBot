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
            [InlineKeyboardButton(text="🤝 Kelishiladi", callback_data="salary_negotiable")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")],
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


def get_admin_moderation_keyboard(job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash va Post qilish", callback_data=f"admin_approve_{job_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject_{job_id}"),
            ]
        ]
    )
