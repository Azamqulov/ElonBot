from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.database.models import User, UserRole
from src.database.repositories import UserRepository, ChannelRepository, CategoryRepository, JobRequestRepository

router = Router()


def is_superadmin_check(user: User) -> bool:
    return user.is_superadmin()


@router.message(Command("add_admin"))
async def cmd_add_admin(message: Message, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: <code>/add_admin &lt;Telegram_ID&gt;</code>", parse_mode="HTML")
        return

    target_id_str = args[1]
    if not target_id_str.isdigit():
        await message.answer("Telegram ID faqat raqamlardan iborat bo'lishi kerak.")
        return

    target_id = int(target_id_str)
    user = await user_repo.get_by_tg_id(target_id)
    if not user:
        # Yangi foydalanuvchi sifatida ochib admin qilish
        user, _ = await user_repo.get_or_create(tg_id=target_id, full_name="Admin", username=None)

    await user_repo.set_role(target_id, UserRole.ADMIN.value)
    await message.answer(f"✅ Foydalanuvchi (ID: <code>{target_id}</code>) muvaffaqiyatli <b>Admin</b> qilindi.", parse_mode="HTML")


@router.message(Command("remove_admin"))
async def cmd_remove_admin(message: Message, db_user: User, user_repo: UserRepository):
    if not is_superadmin_check(db_user):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Foydalanish: <code>/remove_admin &lt;Telegram_ID&gt;</code>", parse_mode="HTML")
        return

    target_id = int(args[1])
    await user_repo.set_role(target_id, UserRole.USER.value)
    await message.answer(f"✅ Foydalanuvchi (ID: <code>{target_id}</code>) adminlikdan olindi.", parse_mode="HTML")


@router.message(Command("add_channel"))
async def cmd_add_channel(message: Message, db_user: User, chan_repo: ChannelRepository):
    if not is_superadmin_check(db_user):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "Foydalanish: <code>/add_channel &lt;@kanal_yoki_id&gt;</code>\n"
            "<i>Eslatma: Bot ushbu kanalda administrator bo'lishi shart!</i>",
            parse_mode="HTML",
        )
        return

    channel_tag = args[1].strip()
    channel = await chan_repo.add_channel(
        tg_channel_id=channel_tag,
        channel_username=channel_tag if channel_tag.startswith("@") else None,
        added_by=db_user.id,
    )
    await message.answer(f"✅ Kanal <b>{channel.tg_channel_id}</b> muvaffaqiyatli ulandi!", parse_mode="HTML")


@router.message(Command("channels"))
async def cmd_list_channels(message: Message, db_user: User, chan_repo: ChannelRepository):
    if not is_superadmin_check(db_user):
        return

    channels = await chan_repo.get_all_active()
    if not channels:
        await message.answer("Hozircha ulangan kanallar yo'q.")
        return

    lines = ["📡 <b>Ulangan kanallar ro'yxati:</b>\n"]
    for ch in channels:
        lines.append(f"• <b>{ch.tg_channel_id}</b> (ID: {ch.id})")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("add_category"))
async def cmd_add_category(message: Message, db_user: User, cat_repo: CategoryRepository):
    if not is_superadmin_check(db_user):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: <code>/add_category &lt;Kategoriya nomi&gt;</code>", parse_mode="HTML")
        return

    cat_name = args[1].strip()
    new_cat = await cat_repo.create(name=cat_name, icon_name="briefcase")
    await message.answer(f"✅ Yangi kategoriya qo'shildi: <b>{new_cat.name}</b>", parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_full_stats(message: Message, db_user: User, job_repo: JobRequestRepository):
    if not is_superadmin_check(db_user):
        return

    stats = await job_repo.get_statistics()
    text = (
        "📈 <b>ElonBot — Kengaytirilgan Tizim Statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar soni: <b>{stats['total_users']}</b>\n"
        f"📝 Jami yuborilgan e'lonlar: <b>{stats['total_jobs']}</b>\n"
        f"⏳ Ko'rib chiqilmoqda (pending): <b>{stats['pending_jobs']}</b>\n"
        f"🚀 Tasdiqlangan/Post qilingan: <b>{stats['approved_jobs']}</b>\n"
        f"❌ Rad etilgan: <b>{stats['rejected_jobs']}</b>\n"
    )
    await message.answer(text, parse_mode="HTML")
