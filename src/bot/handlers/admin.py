import os
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from src.bot.states.job_states import AdminRejectFSM, AdminPaymentFSM
from src.bot.keyboards.inline_keyboards import (
    get_admin_moderation_keyboard,
    get_admin_panel_keyboard,
    get_admin_back_keyboard,
    get_payment_settings_keyboard,
)
from src.database.models import User, JobStatus
from src.database.repositories import JobRequestRepository, ChannelRepository, SettingsRepository
from src.bot.config import settings

router = Router()


def is_admin_check(user: User) -> bool:
    return user.is_admin()


async def render_admin_panel_text(job_repo: JobRequestRepository) -> tuple[str, int]:
    stats = await job_repo.get_statistics()
    text = (
        "🛡️ <b>Admin Boshqaruv Paneli</b>\n\n"
        f"📊 <b>Tizim statistikasi:</b>\n"
        f"• Jami e'lonlar: <b>{stats['total_jobs']}</b> ta\n"
        f"• Kutilmoqda (moderatsiyada): <b>{stats['pending_jobs']}</b> ta\n"
        f"• Tasdiqlangan/Chiqarilgan: <b>{stats['approved_jobs']}</b> ta\n"
        f"• Rad etilgan: <b>{stats['rejected_jobs']}</b> ta\n"
        f"• Jami foydalanuvchilar: <b>{stats['total_users']}</b> ta\n\n"
        "Boshqaruv uchun quyidagi tugmalardan foydalaning 👇"
    )
    return text, stats["pending_jobs"]


@router.message(F.text == "🛡️ Admin paneli")
@router.message(Command("admin"))
async def cmd_admin_panel(message: Message, db_user: User, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        await message.answer("Kechirasiz, sizda admin huquqlari mavjud emas.")
        return

    text, pending_count = await render_admin_panel_text(job_repo)
    kb = get_admin_panel_keyboard(is_superadmin=db_user.is_superadmin(), pending_count=pending_count)
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data == "admin_btn_back")
async def cb_admin_back(call: CallbackQuery, db_user: User, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    text, pending_count = await render_admin_panel_text(job_repo)
    kb = get_admin_panel_keyboard(is_superadmin=db_user.is_superadmin(), pending_count=pending_count)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "admin_btn_close")
async def cb_admin_close(call: CallbackQuery):
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.answer("Yopildi.")


@router.callback_query(F.data == "admin_btn_stats")
@router.message(Command("stats"))
async def cmd_stats_button(event: Message | CallbackQuery, db_user: User, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        if isinstance(event, CallbackQuery):
            await event.answer("Ruxsat yo'q!", show_alert=True)
        return

    stats = await job_repo.get_statistics()
    text = (
        "📊 <b>Kengaytirilgan Tizim Statistikasi</b>\n\n"
        f"📋 <b>E'lonlar:</b>\n"
        f"• Jami qabul qilingan: <b>{stats['total_jobs']}</b> ta\n"
        f"• Hozir kutayotgan (Pending): <b>{stats['pending_jobs']}</b> ta\n"
        f"• Muvaffaqiyatli kanalga chiqqan: <b>{stats['approved_jobs']}</b> ta\n"
        f"• Rad etilgan: <b>{stats['rejected_jobs']}</b> ta\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"• Bot foydalanuvchilari soni: <b>{stats['total_users']}</b> ta"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())


@router.callback_query(F.data == "admin_btn_pending")
@router.message(Command("pending"))
async def cmd_pending_jobs(event: Message | CallbackQuery, db_user: User, bot: Bot, job_repo: JobRequestRepository):
    if not is_admin_check(db_user):
        if isinstance(event, CallbackQuery):
            await event.answer("Ruxsat yo'q!", show_alert=True)
        return

    pending_jobs = await job_repo.get_pending_jobs(limit=10)
    target_msg = event.message if isinstance(event, CallbackQuery) else event

    if not pending_jobs:
        ans_text = "✅ <b>Ayni damda ko'rib chiqish uchun yangi so'rovlar yo'q!</b>\nBarcha e'lonlar ko'rib chiqilgan."
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(ans_text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
            await event.answer()
        else:
            await event.answer(ans_text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
        return

    if isinstance(event, CallbackQuery):
        await event.answer(f"{len(pending_jobs)} ta kutayotgan e'lon mavjud.")

    await target_msg.answer(f"⏳ <b>Kutayotgan so'rovlar ({len(pending_jobs)} ta):</b>", parse_mode="HTML")

    for job in pending_jobs:
        type_badge = "Rezyume" if getattr(job, "request_type", "job") == "resume" else "Vakansiya"
        text = (
            f"📋 <b>{type_badge} #{job.id}</b>\n"
            f"Sohasi/Lavozim: <b>{job.position}</b>\n"
            f"Kompaniya/Ism: <b>{job.company}</b>\n"
            f"Maosh/Narx: <b>{job.salary}</b>\n\n"
            f"{job.post_text}"
        )

        has_receipt = bool(job.receipt_image_path and os.path.exists(job.receipt_image_path))
        ad_kb = None if has_receipt else get_admin_moderation_keyboard(job.id)

        if job.image_path and os.path.exists(job.image_path):
            if len(text) <= 1024:
                await target_msg.answer_photo(
                    photo=FSInputFile(job.image_path),
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=ad_kb,
                )
            else:
                await target_msg.answer_photo(photo=FSInputFile(job.image_path))
                await target_msg.answer(text, parse_mode="HTML", reply_markup=ad_kb)
        else:
            await target_msg.answer(text, parse_mode="HTML", reply_markup=ad_kb)

        # Agar to'lov cheki yuborilgan bo'lsa, uni alohida ko'rsatish
        if has_receipt:
            amt_text = f"{job.payment_amount:,}".replace(",", " ") + " UZS" if job.payment_amount else "Noma'lum"
            receipt_caption = (
                f"🧾 <b>To'lov cheki (E'lon #{job.id})</b>\n"
                f"💵 Belgilangan summa: <b>{amt_text}</b>\n"
                f"💳 To'lov holati: <b>{job.payment_status}</b>\n\n"
                "Iltimos, to'lovni tasdiqlang yoki rad eting:"
            )
            await target_msg.answer_photo(
                photo=FSInputFile(job.receipt_image_path),
                caption=receipt_caption,
                parse_mode="HTML",
                reply_markup=get_admin_moderation_keyboard(job.id),
            )


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

    # Statusni tasdiqlash va to'lovni paid qilish
    await job_repo.update_status(job_id=job.id, status=JobStatus.APPROVED.value, reviewer_id=db_user.id)
    await job_repo.update_payment(job_id=job.id, payment_status="paid")

    # Kanalga post qilish
    channels = await chan_repo.get_all_active()
    target_channel = settings.DEFAULT_CHANNEL_ID
    if channels:
        target_channel = channels[0].tg_channel_id

    posted_successfully = False
    try:
        if job.image_path and os.path.exists(job.image_path):
            if len(job.post_text) <= 1024:
                await bot.send_photo(
                    chat_id=target_channel,
                    photo=FSInputFile(job.image_path),
                    caption=job.post_text,
                )
            else:
                await bot.send_photo(chat_id=target_channel, photo=FSInputFile(job.image_path))
                await bot.send_message(chat_id=target_channel, text=job.post_text)
        else:
            await bot.send_message(chat_id=target_channel, text=job.post_text)

        posted_successfully = True
        await job_repo.update_status(job_id=job.id, status=JobStatus.POSTED.value, reviewer_id=db_user.id)
    except Exception as e:
        # Kanalga yuborishda xatolik (masalan bot kanalda admin emas)
        await call.message.answer(
            f"⚠️ <b>Kanalga post qilishda xatolik bo'ldi:</b> {str(e)}\n"
            f"Bot {target_channel} kanalida admin ekanligini va post chiqarish huquqi borligini tekshiring."
        )

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        type_title = "rezyume" if getattr(job, "request_type", "job") == "resume" else "vakansiya"
        user_msg = (
            f"🎉 <b>Ajoyib yangilik! To'lovingiz va e'loningiz tasdiqlandi!</b>\n\n"
            f"Sizning <b>#{job.id} - {job.position}</b> bo'yicha {type_title} e'loningiz "
            f"administrator tomonidan tekshirilib tasdiqlandi{' va kanalga joylandi' if posted_successfully else ''}!"
        )
        await bot.send_message(chat_id=job.user.tg_id, text=user_msg, parse_mode="HTML")
    except Exception:
        pass

    # Admin xabarini yangilash
    await call.answer("E'lon va to'lov tasdiqlandi!")
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
        "<i>(Ushbu sabab foydalanuvchiga yuboriladi, masalan: 'To'lov cheki soxta' yoki 'E'lon talablari noto'liq')</i>",
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
    await job_repo.update_payment(job_id=job_id, payment_status="rejected")

    await state.clear()
    await message.answer(f"❌ <b>#{job_id} raqamli e'lon rad etildi.</b>", parse_mode="HTML")

    if job and job.user:
        try:
            type_title = "Rezyume" if getattr(job, "request_type", "job") == "resume" else "Vakansiya"
            reject_notice = (
                f"❌ <b>{type_title} e'loningiz rad etildi. (ID: #{job.id})</b>\n\n"
                f"Yo'nalish/Lavozim: <b>{job.position}</b>\n"
                f"Kompaniya/Ism: <b>{job.company}</b>\n\n"
                f"⚠️ <b>Rad etish sababi:</b> {reason}\n\n"
                "Iltimos, ko'rsatilgan kamchiliklarni to'g'rilab yoki to'lov ma'lumotlarini tekshirib qaytadan yuboring."
            )
            await bot.send_message(chat_id=job.user.tg_id, text=reject_notice, parse_mode="HTML")
        except Exception:
            pass


# =========================================================
# --- TO'LOV TIZIMI SOZLAMALARI (PAYMENT SETTINGS FLOW) ---
# =========================================================

@router.callback_query(F.data == "admin_btn_payment_settings")
async def cb_admin_payment_settings(call: CallbackQuery, db_user: User, settings_repo: SettingsRepository):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    setting = await settings_repo.get_settings()
    formatted_price = f"{setting.price_per_post:,}".replace(",", " ") + " UZS"
    status_text = "🟢 Yoqilgan (Har bir e'lon pullik)" if setting.is_payment_enabled else "🔴 O'chirilgan (E'lonlar bepul)"
    text = (
        "💳 <b>E'lonlar uchun To'lov Tizimi Sozlamalari</b>\n\n"
        f"💵 <b>E'lon narxi:</b> <b>{formatted_price}</b>\n"
        f"👤 <b>Karta egasi:</b> <b>{setting.card_holder}</b>\n"
        f"💳 <b>Karta raqami:</b> <code>{setting.card_number}</code>\n"
        f"🔘 <b>To'lov holati:</b> {status_text}\n\n"
        "Kerakli sozlamani o'zgartirish uchun quyidagi tugmalardan foydalaning 👇"
    )
    kb = get_payment_settings_keyboard(is_payment_enabled=setting.is_payment_enabled)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "admin_pay_toggle_status")
async def cb_admin_pay_toggle_status(call: CallbackQuery, db_user: User, settings_repo: SettingsRepository):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    setting = await settings_repo.toggle_payment_enabled()
    formatted_price = f"{setting.price_per_post:,}".replace(",", " ") + " UZS"
    status_text = "🟢 Yoqilgan (Har bir e'lon pullik)" if setting.is_payment_enabled else "🔴 O'chirilgan (E'lonlar bepul)"
    text = (
        "💳 <b>E'lonlar uchun To'lov Tizimi Sozlamalari</b>\n\n"
        f"💵 <b>E'lon narxi:</b> <b>{formatted_price}</b>\n"
        f"👤 <b>Karta egasi:</b> <b>{setting.card_holder}</b>\n"
        f"💳 <b>Karta raqami:</b> <code>{setting.card_number}</code>\n"
        f"🔘 <b>To'lov holati:</b> {status_text}\n\n"
        "Kerakli sozlamani o'zgartirish uchun quyidagi tugmalardan foydalaning 👇"
    )
    kb = get_payment_settings_keyboard(is_payment_enabled=setting.is_payment_enabled)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer("To'lov holati o'zgartirildi!")


@router.callback_query(F.data == "admin_pay_set_price")
async def cb_admin_pay_set_price(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminPaymentFSM.waiting_for_price)
    text = (
        "💵 <b>E'lon narxini belgilash</b>\n\n"
        "Har bitta post uchun yangi narxni <b>so'mda</b> kiriting (faqat raqam):\n"
        "<i>(Masalan: 20000 yoki 35000)</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(AdminPaymentFSM.waiting_for_price, F.text)
async def step_admin_price_entered(
    message: Message, state: FSMContext, db_user: User, settings_repo: SettingsRepository
):
    if not is_admin_check(db_user):
        return

    clean_text = message.text.replace(" ", "").replace(",", "").replace(".", "").strip()
    if not clean_text.isdigit() or int(clean_text) < 0:
        await message.answer("⚠️ Iltimos, to'g'ri musbat raqam kiriting (masalan: 25000):")
        return

    new_price = int(clean_text)
    setting = await settings_repo.update_price(new_price)
    await state.clear()
    formatted_price = f"{setting.price_per_post:,}".replace(",", " ") + " UZS"
    await message.answer(
        f"✅ E'lon narxi muvaffaqiyatli <b>{formatted_price}</b> qilib belgilandi!",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )


@router.callback_query(F.data == "admin_pay_set_card")
async def cb_admin_pay_set_card(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminPaymentFSM.waiting_for_card_number)
    text = (
        "💳 <b>Karta raqamini kiritish</b>\n\n"
        "To'lovlar qabul qilinadigan yangi 16 xonali karta raqamini yuboring:\n"
        "<i>(Masalan: 8600 1234 5678 9012 yoki 9860123456789012)</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(AdminPaymentFSM.waiting_for_card_number, F.text)
async def step_admin_card_entered(
    message: Message, state: FSMContext, db_user: User, settings_repo: SettingsRepository
):
    if not is_admin_check(db_user):
        return

    raw_num = message.text.replace(" ", "").replace("-", "").strip()
    if not raw_num.isdigit() or len(raw_num) != 16:
        await message.answer("⚠️ Karta raqami 16 ta raqamdan iborat bo'lishi kerak. Iltimos qaytadan kiriting:")
        return

    formatted_card = f"{raw_num[:4]} {raw_num[4:8]} {raw_num[8:12]} {raw_num[12:16]}"
    setting = await settings_repo.update_card_number(formatted_card)
    await state.clear()
    await message.answer(
        f"✅ Karta raqami muvaffaqiyatli saqlandi: <code>{setting.card_number}</code>",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )


@router.callback_query(F.data == "admin_pay_set_holder")
async def cb_admin_pay_set_holder(call: CallbackQuery, state: FSMContext, db_user: User):
    if not is_admin_check(db_user):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminPaymentFSM.waiting_for_card_holder)
    text = (
        "👤 <b>Karta egasini kiritish</b>\n\n"
        "Karta egasining ism va familiyasini kiriting:\n"
        "<i>(Masalan: Said Amir yoki Azizbek Karimov)</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_back_keyboard())
    await call.answer()


@router.message(AdminPaymentFSM.waiting_for_card_holder, F.text)
async def step_admin_holder_entered(
    message: Message, state: FSMContext, db_user: User, settings_repo: SettingsRepository
):
    if not is_admin_check(db_user):
        return

    name = message.text.strip()
    if len(name) < 3:
        await message.answer("⚠️ Iltimos, to'liq ism-familiyani kiriting:")
        return

    setting = await settings_repo.update_card_holder(name)
    await state.clear()
    await message.answer(
        f"✅ Karta egasi muvaffaqiyatli saqlandi: <b>{setting.card_holder}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_back_keyboard(),
    )
