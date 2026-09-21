from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.bot.states.job_states import SuperAdminFSM
from src.bot.keyboards.inline_keyboards import (
    get_admin_back_keyboard,
    get_channels_manage_keyboard,
    get_admins_manage_keyboard,
)
from src.database.models import User, UserRole
from src.database.repositories import UserRepository, ChannelRepository, CategoryRepository

router = Router()


def is_superadmin_check(user: User) -> bool:
    return user.is_superadmin()


# --- 1. ADMIN QO'SHISH (BUTTON FLOW) ---
@router.callback_query(F.data == "sa_btn_add_admin")
async def cb_sa_add_admin_start(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    await state.set_state(SuperAdminFSM.waiting_for_admin_tg_id)
    text = (
        "➕ <b>Yangi admin tayinlash</b>\n\n"
        "Admin qilmoqchi bo'lgan foydalanuvchining <b>Telegram ID raqamini</b> yuboring:\n"
        "<i>(Foydalanuvchi botga kamida bir marta /start bosgan bo'lishi lozim)</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(SuperAdminFSM.waiting_for_admin_tg_id, F.text)
async def step_admin_id_received(message: Message, state: FSMContext, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        return

    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Telegram ID faqat raqamlardan iborat bo'lishi kerak. Iltimos qaytadan kiriting:")
        return

    target_id = int(text)
    user = await user_repo.get_by_tg_id(target_id)
    if not user:
        user, _ = await user_repo.get_or_create(tg_id=target_id, full_name="Admin", username=None)

    await user_repo.set_role(target_id, UserRole.ADMIN.value)
    await state.clear()
    await message.answer(
        f"✅ Foydalanuvchi (ID: <code>{target_id}</code>) muvaffaqiyatli <b>Admin</b> qilindi!",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )


# --- 2. ADMINNI O'CHIRISH (BUTTON FLOW) ---
@router.callback_query(F.data == "sa_btn_remove_admin")
async def cb_sa_remove_admin_list(call: CallbackQuery, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    admins = await user_repo.get_all_admins()
    # O'zini ro'yxatdan chiqarib tashlash (superadmin o'zini o'chirmasligi uchun)
    filtered_admins = [a for a in admins if a.tg_id != db_user.tg_id]

    if not filtered_admins:
        await call.message.edit_text(
            "ℹ️ Tizimda sizdan boshqa faol adminlar mavjud emas.",
            parse_mode="HTML",
            reply_markup=get_admin_back_keyboard(),
        )
        await call.answer()
        return

    text = "➖ <b>Adminlikdan olish:</b>\n\nAdminlik huquqini bekor qilmoqchi bo'lgan adminni tanlang:"
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admins_manage_keyboard(filtered_admins))
    await call.answer()


@router.callback_query(F.data.startswith("sa_del_admin_"))
async def cb_sa_delete_admin(call: CallbackQuery, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    target_id = int(call.data.replace("sa_del_admin_", ""))
    await user_repo.set_role(target_id, UserRole.USER.value)
    await call.answer(f"ID {target_id} adminlikdan olindi!", show_alert=True)

    # Qayta ro'yxatni yangilash
    admins = await user_repo.get_all_admins()
    filtered_admins = [a for a in admins if a.tg_id != db_user.tg_id]
    if not filtered_admins:
        await call.message.edit_text(
            "✅ Tanlangan admin o'chirildi. Boshqa adminlar qolmadi.",
            parse_mode="HTML",
            reply_markup=get_admin_back_keyboard(),
        )
    else:
        text = "➖ <b>Adminlikdan olish:</b>\n\nAdminlik huquqini bekor qilmoqchi bo'lgan adminni tanlang:"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admins_manage_keyboard(filtered_admins))


# --- 3. KANAL ULASH (BUTTON FLOW) ---
@router.callback_query(F.data == "sa_btn_add_channel")
async def cb_sa_add_channel_start(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    await state.set_state(SuperAdminFSM.waiting_for_channel_id)
    text = (
        "📢 <b>Yangi kanal ulash</b>\n\n"
        "Ulamoqchi bo'lgan kanalingiz <b>@username</b> yoki Telegram ID raqamini yuboring:\n"
        "<i>(Masalan: @freelance_uzb yoki -100123456789)\n\n"
        "⚠️ Muhim: Bot ushbu kanalda administrator bo'lishi va xabar yuborish huquqi berilgan bo'lishi shart!</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(SuperAdminFSM.waiting_for_channel_id, F.text)
async def step_channel_id_received(message: Message, state: FSMContext, db_user: User, chan_repo: ChannelRepository):
    if not is_superadmin_check(db_user):
        return

    channel_tag = message.text.strip()
    channel = await chan_repo.add_channel(
        tg_channel_id=channel_tag,
        channel_username=channel_tag if channel_tag.startswith("@") else None,
        added_by=db_user.id,
    )
    await state.clear()
    await message.answer(
        f"✅ Kanal <b>{channel.tg_channel_id}</b> muvaffaqiyatli ulandi va faollashtirildi!",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )


# --- 4. ULANGAN KANALLAR RO'YXATI VA BOSHQARUVI ---
@router.callback_query(F.data == "sa_btn_channels")
async def cb_sa_channels_list(call: CallbackQuery, db_user: User, chan_repo: ChannelRepository):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    channels = await chan_repo.get_all_active()
    if not channels:
        await call.message.edit_text(
            "📡 <b>Hozircha ulangan kanallar yo'q.</b>\n"
            "Yangi kanal qo'shish uchun '📢 Kanal ulash' tugmasidan foydalaning.",
            parse_mode="HTML",
            reply_markup=get_admin_back_keyboard(),
        )
        await call.answer()
        return

    text = f"📡 <b>Ulangan faol kanallar ({len(channels)} ta):</b>\nO'chirish uchun '🗑 O'chirish' tugmasini bosing:"
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_channels_manage_keyboard(channels))
    await call.answer()


@router.callback_query(F.data.startswith("sa_del_chan_"))
async def cb_sa_delete_channel(call: CallbackQuery, db_user: User, chan_repo: ChannelRepository):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    channel_id = int(call.data.replace("sa_del_chan_", ""))
    await chan_repo.remove_channel(channel_id)
    await call.answer("Kanal o'chirildi!", show_alert=True)

    channels = await chan_repo.get_all_active()
    if not channels:
        await call.message.edit_text(
            "📡 Barcha kanallar o'chirildi.",
            parse_mode="HTML",
            reply_markup=get_admin_back_keyboard(),
        )
    else:
        text = f"📡 <b>Ulangan faol kanallar ({len(channels)} ta):</b>"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_channels_manage_keyboard(channels))


# --- 5. ADMINLAR RO'YXATI ---
@router.callback_query(F.data == "sa_btn_admins_list")
async def cb_sa_admins_list(call: CallbackQuery, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    admins = await user_repo.get_all_admins()
    lines = [f"👥 <b>Barcha adminlar ro'yxati ({len(admins)} ta):</b>\n"]
    for a in admins:
        role_badge = "👑 Superadmin" if a.role == UserRole.SUPERADMIN.value else "🛡️ Moderator Admin"
        lines.append(f"• <b>{a.full_name}</b> (@{a.username or 'yo_q'}) — ID: <code>{a.tg_id}</code> [{role_badge}]")

    await call.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


# --- 6. KATEGORIYA QO'SHISH ---
@router.callback_query(F.data == "sa_btn_add_category")
async def cb_sa_add_cat_start(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_superadmin_check(db_user):
        await call.answer("Faqat superadmin uchun!", show_alert=True)
        return

    await state.set_state(SuperAdminFSM.waiting_for_category_name)
    text = (
        "📁 <b>Yangi kategoriya qo'shish</b>\n\n"
        "Yangi ish turi / kategoriya nomini kiriting:\n"
        "<i>(Masalan: Grafik Dizayn, Yetkazib berish, Call-markaz operatori)</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(SuperAdminFSM.waiting_for_category_name, F.text)
async def step_cat_name_received(message: Message, state: FSMContext, db_user: User, cat_repo: CategoryRepository):
    if not is_superadmin_check(db_user):
        return

    cat_name = message.text.strip()
    cat = await cat_repo.create(name=cat_name, icon_name="briefcase")
    await state.clear()
    await message.answer(
        f"✅ <b>'{cat.name}'</b> kategoriyasi muvaffaqiyatli qo'shildi!",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )
