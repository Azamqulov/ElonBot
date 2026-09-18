import os
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from src.bot.states.job_states import AdminRejectFSM
from src.bot.keyboards.inline_keyboards import get_admin_moderation_keyboard
from src.database.models import User, JobStatus
from src.database.repositories import JobRequestRepository, ChannelRepository
from src.bot.config import settings

router = Router()


def is_admin_check(user: User) -> bool:
    return user.is_admin()


@router.message(F.text == "🛡️ Admin paneli")
@router.message(Command("admin"))
async def cmd_admin_panel(message: Message, db_user: User, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        await message.answer("Kechirasiz, sizda admin huquqlari mavjud emas.")
        return

    stats = await job_repo.get_statistics()
    text = (
        "🛡️ <b>Admin Boshqaruv Paneli</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• Jami e'lonlar: <b>{stats['total_jobs']}</b>\n"
        f"• Kutilmoqda: <b>{stats['pending_jobs']}</b>\n"
        f"• Tasdiqlangan/Chiqarilgan: <b>{stats['approved_jobs']}</b>\n"
        f"• Rad etilgan: <b>{stats['rejected_jobs']}</b>\n"
        f"• Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n\n"
        "⚡ <b>Buyruqlar:</b>\n"
        "/pending — Kutayotgan so'rovlarni ko'rish\n"
        "/stats — Kengaytirilgan statistika\n"
    )
    if db_user.is_superadmin():
        text += (
            "\n👑 <b>Superadmin buyruqlari:</b>\n"
            "/add_admin &lt;tg_id&gt; — Yangi admin tayinlash\n"
            "/remove_admin &lt;tg_id&gt; — Adminlikdan olish\n"
            "/add_channel &lt;@kanal&gt; — Kanal ulash\n"
            "/channels — Kanallar ro'yxati\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("pending"))
async def cmd_pending_jobs(message: Message, db_user: User, bot: Bot, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        return

    pending_jobs = await job_repo.get_pending_jobs(limit=10)
    if not pending_jobs:
        await message.answer("Hozirda ko'rib chiqish uchun yangi so'rovlar yo'q.")
        return

    await message.answer(f"⏳ <b>Kutayotgan so'rovlar soni: {len(pending_jobs)} ta</b>", parse_mode="HTML")

    for job in pending_jobs:
        text = (
            f"📋 <b>Vakansiya #{job.id}</b>\n"
            f"Lavozim: <b>{job.position}</b>\n"
            f"Kompaniya: <b>{job.company}</b>\n"
            f"Maosh: <b>{job.salary}</b>\n\n"
            f"{job.post_text}"
        )
        if job.image_path and os.path.exists(job.image_path):
            if len(text) <= 1024:
                await message.answer_photo(
                    photo=FSInputFile(job.image_path),
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=get_admin_moderation_keyboard(job.id),
                )
            else:
                await message.answer_photo(photo=FSInputFile(job.image_path))
                await message.answer(text, parse_mode="HTML", reply_markup=get_admin_moderation_keyboard(job.id))
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=get_admin_moderation_keyboard(job.id))


@router.callback_query(F.data.startswith("admin_approve_"))
async def cb_admin_approve(
    call: CallbackQuery,
    bot: Bot,
    db_user: User,
    job_repo: JobRequestRepository,
    chan_repo: ChannelRepository,
):
    if not is_admin_check(db_user):
        await call.answer("Sizda ruxsat yo'q!", show_alert=True)
        return

    job_id = int(call.data.replace("admin_approve_", ""))
    job = await job_repo.get_by_id(job_id)
    if not job:
        await call.answer("E'lon topilmadi!", show_alert=True)
        return

    if job.status in (JobStatus.APPROVED.value, JobStatus.POSTED.value):
        await call.answer("Ushbu e'lon allaqachon tasdiqlangan!", show_alert=True)
        return

    # Statusni tasdiqlash
    await job_repo.update_status(job_id=job.id, status=JobStatus.APPROVED.value, reviewer_id=db_user.id)

    # Barcha faol kanallarga post qilish
    channels = await chan_repo.get_all_active()

    # Agar DB da kanal yo'q bo'lsa — .env dagi DEFAULT_CHANNEL_ID ga yuborish
    if not channels:
        target_channels = [settings.DEFAULT_CHANNEL_ID]
    else:
        target_channels = [ch.tg_channel_id for ch in channels]

    posted_successfully = False
    post_errors = []

    for target_channel in target_channels:
        try:
            if job.image_path and os.path.exists(job.image_path):
                if len(job.post_text) <= 1024:
                    await bot.send_photo(
                        chat_id=target_channel,
                        photo=FSInputFile(job.image_path),
                        caption=job.post_text,
                        parse_mode="HTML",
                    )
                else:
                    await bot.send_photo(chat_id=target_channel, photo=FSInputFile(job.image_path))
                    await bot.send_message(chat_id=target_channel, text=job.post_text, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=target_channel, text=job.post_text, parse_mode="HTML")

            posted_successfully = True
        except Exception as e:
            post_errors.append(f"❌ <b>{target_channel}</b>: {str(e)}")

    if post_errors:
        err_text = "\n".join(post_errors)
        await call.message.answer(
            f"⚠️ <b>Quyidagi kanallarga post qilishda xatolik:</b>\n{err_text}\n\n"
            "📌 <b>Tekshiring:</b>\n"
            "1. Bot kanalda <b>Admin</b> bo'lishi kerak\n"
            "2. Botga <b>'Post xabarlar'</b> ruxsati berilishi kerak\n"
            f"3. Kanal to'g'ri: <code>{', '.join(target_channels)}</code>",
            parse_mode="HTML",
        )

    if posted_successfully:
        await job_repo.update_status(job_id=job.id, status=JobStatus.POSTED.value, reviewer_id=db_user.id)

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        user_msg = (
            f"🎉 <b>Ajoyib yangilik!</b>\n\n"
            f"Sizning <b>#{job.id} - {job.position}</b> bo'yicha vakansiya e'loningiz admin tomonidan "
            f"tasdiqlandi{' va kanalga joylandi' if posted_successfully else ''}!"
        )
        await bot.send_message(chat_id=job.user.tg_id, text=user_msg, parse_mode="HTML")
    except Exception:
        pass

    # Admin xabarini yangilash
    await call.answer("E'lon tasdiqlandi!")
    status_note = "✅ <b>TASDIQLANDI VA KANALGA JOYLANDI</b>" if posted_successfully else "✅ <b>TASDIQLANDI (Kanalga qo'lda joylang)</b>"
    try:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.reply(status_note, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_reject_"))
async def cb_admin_reject(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_admin_check(db_user):
        await call.answer("Sizda ruxsat yo'q!", show_alert=True)
        return

    job_id = int(call.data.replace("admin_reject_", ""))
    await state.update_data(reject_job_id=job_id)
    await state.set_state(AdminRejectFSM.waiting_for_reason)

    await call.message.reply(
        f"❌ <b>#{job_id} raqamli e'lonni rad etish sababini yozing:</b>\n"
        "<i>(Ushbu sabab foydalanuvchiga yuboriladi)</i>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminRejectFSM.waiting_for_reason, F.text)
async def step_reject_reason_entered(
    message: Message,
    state: FSMContext,
    bot: Bot,
    db_user: User,
    job_repo: JobRequestRepository,
):
    reason = message.text.strip()
    data = await state.get_data()
    job_id = data.get("reject_job_id")

    if not job_id:
        await message.answer("Xatolik: e'lon identifikatori topilmadi.")
        await state.clear()
        return

    job = await job_repo.update_status(
        job_id=job_id,
        status=JobStatus.REJECTED.value,
        reviewer_id=db_user.id,
        rejection_reason=reason,
    )

    await state.clear()
    await message.answer(f"❌ <b>#{job_id} raqamli e'lon rad etildi.</b>", parse_mode="HTML")

    if job and job.user:
        try:
            reject_notice = (
                f"❌ <b>Vakansiya e'loningiz rad etildi. (ID: #{job.id})</b>\n\n"
                f"Lavozim: <b>{job.position}</b>\n"
                f"Kompaniya: <b>{job.company}</b>\n\n"
                f"⚠️ <b>Sabab:</b> {reason}\n\n"
                "Iltimos, e'lonni ko'rsatilgan kamchiliklarni to'g'rilab qaytadan yuboring."
            )
            await bot.send_message(chat_id=job.user.tg_id, text=reject_notice, parse_mode="HTML")
        except Exception:
            pass
