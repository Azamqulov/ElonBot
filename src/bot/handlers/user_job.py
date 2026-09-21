import os
import re
import time
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.states.job_states import JobApplicationFSM, ResumeApplicationFSM
from src.bot.keyboards.inline_keyboards import (
    get_categories_keyboard,
    get_salary_keyboard,
    get_skip_keyboard,
    get_preview_keyboard,
    get_admin_moderation_keyboard,
    get_announcement_type_keyboard,
    get_cancel_receipt_keyboard,
    get_currency_selected_keyboard,
)
from src.bot.keyboards.reply_keyboards import (
    get_main_menu_keyboard,
    get_contact_keyboard,
)
from src.database.models import User, JobStatus
from src.database.repositories import CategoryRepository, JobRequestRepository, UserRepository, SettingsRepository
from src.services.post_generator import PostGenerator
from src.services.image_generator import image_generator
from src.bot.config import settings, BASE_DIR

def format_phone_number(raw_phone: str) -> str:
    """Telefon raqamini chiroyli O'zbekiston formatiga keltiradi."""
    digits = re.sub(r"[^\d]", "", raw_phone)
    if digits.startswith("998") and len(digits) == 12:
        return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
    elif len(digits) == 9:
        return f"+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"
    elif raw_phone.startswith("+"):
        return raw_phone
    return f"+{digits}" if digits else raw_phone


def get_contact_prompt_text() -> str:
    return (
        "8-qadam: <b>Bog'lanish uchun aloqa ma'lumotlarini</b> kiriting:\n\n"
        "<i>💡 Pastdagi tugmani bosib telefon raqamingiz va Telegram profilingizni tezda yuborishingiz "
        "yoki boshqa raqam va @username ni qo'lda yozishingiz mumkin.</i>"
    )


router = Router()


@router.message(Command("new", "elon", "post", "new_job", "yangi"))
@router.message(F.text.in_({"🆕 Yangi e'lon berish", "🆕 Yangi vakansiya berish"}))
async def start_announcement_choice(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Qanday turdagi e'lon bermoqchisiz?\n\n"
        "💼 <b>Ishchi kerak (Vakansiya)</b> — Kompaniya va ish beruvchilar uchun xodim qidirish.\n"
        "👨‍💼 <b>Ish kerak (Rezyume / Frilans)</b> — Mutaxassislar va frilanserlar uchun o'z xizmatlarini taklif qilish.",
        parse_mode="HTML",
        reply_markup=get_announcement_type_keyboard(),
    )


@router.callback_query(F.data == "type_job")
async def choose_job_type(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    categories = await cat_repo.get_all_active()
    if not categories:
        await call.answer("Hozircha tizimda faol kategoriyalar mavjud emas.", show_alert=True)
        return

    await state.clear()
    await state.set_state(JobApplicationFSM.category)
    await call.message.edit_text(
        "💼 <b>Vakansiya e'loni berish</b>\n\n"
        "1-qadam: <b>Ish turi / Kategoriya</b>ni tanlang:",
        parse_mode="HTML",
        reply_markup=get_categories_keyboard(categories),
    )


@router.callback_query(F.data == "type_resume")
async def choose_resume_type(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    categories = await cat_repo.get_all_active()
    if not categories:
        await call.answer("Hozircha tizimda faol kategoriyalar mavjud emas.", show_alert=True)
        return

    await state.clear()
    await state.set_state(ResumeApplicationFSM.category)
    await call.message.edit_text(
        "👨‍💼 <b>Rezyume / Frilanser e'loni berish</b>\n\n"
        "1-qadam: <b>Sohangizni / Kategoriya</b>ni tanlang:",
        parse_mode="HTML",
        reply_markup=get_categories_keyboard(categories),
    )


@router.callback_query(JobApplicationFSM.category, F.data.startswith("cat_"))
async def step_category_selected(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    category_id = int(call.data.replace("cat_", ""))
    cat = await cat_repo.get_by_id(category_id)
    if not cat:
        await call.answer("Kategoriya topilmadi!", show_alert=True)
        return

    await state.update_data(category_id=cat.id, category_name=cat.name)
    await state.set_state(JobApplicationFSM.position)

    await call.message.edit_text(
        f"Tanlangan kategoriya: <b>{cat.name}</b>\n\n"
        "2-qadam: <b>Lavozim nomini</b> kiriting:\n"
        "<i>(Masalan: Senior Python Dasturchi, Savdo Menejeri, Bosh hisobchi)</i>",
        parse_mode="HTML",
    )


@router.message(JobApplicationFSM.position, F.text)
async def step_position_entered(message: Message, state: FSMContext):
    pos = message.text.strip()
    if len(pos) < 3:
        await message.answer("Lavozim nomi juda qisqa. Iltimos to'liqroq yozing:")
        return

    await state.update_data(position=pos)
    await state.set_state(JobApplicationFSM.company)
    await message.answer(
        "3-qadam: <b>Kompaniya yoki brend nomini</b> kiriting:\n"
        "<i>(Masalan: OOO 'Alfa Group', 'TechUz')</i>",
        parse_mode="HTML",
    )


@router.message(JobApplicationFSM.company, F.text)
async def step_company_entered(message: Message, state: FSMContext):
    comp = PostGenerator.format_title_case(message.text.strip())
    await state.update_data(company=comp)
    await state.set_state(JobApplicationFSM.requirements)
    await message.answer(
        "4-qadam: <b>Nomzodga qo'yiladigan talablarni</b> kiriting:\n"
        "<i>(Masalan: 2 yil tajriba, oliy ma'lumot, rus tilini bilish va h.k.)</i>",
        parse_mode="HTML",
    )


@router.message(JobApplicationFSM.requirements, F.text)
async def step_requirements_entered(message: Message, state: FSMContext):
    req = message.text.strip()
    await state.update_data(requirements=req)
    await state.set_state(JobApplicationFSM.salary)
    await message.answer(
        "5-qadam: <b>Maosh miqdorini</b> kiriting.\n\n"
        "💡 Valyutani (<b>UZS</b> yoki <b>USD</b>) tanlashingiz yoki to'g'ridan-to'g'ri yozishingiz mumkin:\n"
        "<i>(Masalan: 10 000 000 UZS yoki 800 - 1200 USD)</i>",
        parse_mode="HTML",
        reply_markup=get_salary_keyboard(),
    )


@router.callback_query(JobApplicationFSM.salary, F.data == "salary_curr_uzs")
async def cb_job_salary_uzs(call: CallbackQuery, state: FSMContext):
    await state.update_data(salary_currency="UZS")
    text = (
        "Valyuta: 🇺🇿 <b>UZS (So'm)</b> tanlandi.\n\n"
        "Endi maosh miqdorini kiriting:\n"
        "<i>(Masalan: 8 000 000 yoki 5 000 000 - 10 000 000)</i>"
    )
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_currency_selected_keyboard("UZS"))
    except Exception:
        pass
    await call.answer("UZS tanlandi")


@router.callback_query(JobApplicationFSM.salary, F.data == "salary_curr_usd")
async def cb_job_salary_usd(call: CallbackQuery, state: FSMContext):
    await state.update_data(salary_currency="USD")
    text = (
        "Valyuta: 🇺🇸 <b>USD (Dollar)</b> tanlandi.\n\n"
        "Endi maosh miqdorini kiriting:\n"
        "<i>(Masalan: 800 yoki 1000 - 1500)</i>"
    )
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_currency_selected_keyboard("USD"))
    except Exception:
        pass
    await call.answer("USD tanlandi")


@router.callback_query(JobApplicationFSM.salary, F.data == "salary_negotiable")
async def step_salary_negotiable(call: CallbackQuery, state: FSMContext):
    await state.update_data(salary="Kelishiladi")
    await state.set_state(JobApplicationFSM.location)
    await call.message.edit_text(
        "Maosh: <b>Kelishiladi</b> deb belgilandi.\n\n"
        "6-qadam: <b>Ish joyi manzili / lokatsiyasini</b> kiriting:\n"
        "<i>(Masalan: Toshkent sh., Mirobod t. yoki 'Masofaviy')</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("location"),
    )


@router.message(JobApplicationFSM.salary, F.text)
async def step_salary_text_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    curr = data.get("salary_currency")
    sal = PostGenerator.format_salary_amount(message.text, curr)
    await state.update_data(salary=sal)
    await state.set_state(JobApplicationFSM.location)
    await message.answer(
        f"Maosh: <b>{sal}</b> qilib belgilandi.\n\n"
        "6-qadam: <b>Ish joyi manzili / lokatsiyasini</b> kiriting:\n"
        "<i>(Masalan: Toshkent sh., Mirobod t. yoki 'Masofaviy')</i>\n"
        "Agar shart bo'lmasa, o'tkazib yuborishingiz mumkin:",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("location"),
    )


@router.callback_query(JobApplicationFSM.location, F.data == "skip_location")
async def step_location_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(location=None)
    await state.set_state(JobApplicationFSM.work_schedule)
    await call.message.edit_text(
        "7-qadam: <b>Ish tartibi va qulayliklarni</b> kiriting:\n"
        "<i>(Masalan: 5/2, 09:00 - 18:00, tushlik beriladi)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("schedule"),
    )


@router.message(JobApplicationFSM.location, F.text)
async def step_location_entered(message: Message, state: FSMContext):
    loc = message.text.strip()
    await state.update_data(location=loc)
    await state.set_state(JobApplicationFSM.work_schedule)
    await message.answer(
        "7-qadam: <b>Ish tartibi va qulayliklarni</b> kiriting:\n"
        "<i>(Masalan: 5/2, 09:00 - 18:00, tushlik beriladi)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("schedule"),
    )


async def render_preview_and_proceed(message: Message, state: FSMContext, contact_info: str, tg_user: str | None = None):
    await state.update_data(contact=contact_info, telegram_user=tg_user)
    data = await state.get_data()

    # Post matnini generatsiya qilish
    post_text = PostGenerator.generate_job_post(
        position=data["position"],
        company=data["company"],
        requirements=data["requirements"],
        salary=data["salary"],
        contact=data["contact"],
        location=data.get("location"),
        work_schedule=data.get("work_schedule"),
        telegram_user=data.get("telegram_user"),
        category_name=data.get("category_name"),
        channel_username=settings.DEFAULT_CHANNEL_ID,
    )

    # Rasm kartasini generatsiya qilish
    card_path = image_generator.generate_job_card(
        position=data["position"],
        company=data["company"],
        salary=data["salary"],
        category_name=data.get("category_name", "Vakansiya"),
        channel_watermark=settings.WATERMARK_TEXT,
    )

    await state.update_data(post_text=post_text, image_path=card_path)
    await state.set_state(JobApplicationFSM.preview)

    preview_caption = (
        "🔍 <b>E'LONINGIZ KO'RINISHI (PREVIEW):</b>\n\n"
        f"{post_text}\n\n"
        "Barcha ma'lumotlar to'g'riligini tekshiring va quyidagi amallardan birini tanlang:"
    )

    # Katta reply klaviaturani olib tashlash
    await message.answer("✅ Aloqa ma'lumotlari qabul qilindi.", reply_markup=ReplyKeyboardRemove())

    # Telegram caption chegarasi 1024 belgi
    if len(preview_caption) <= 1024:
        await message.answer_photo(
            photo=FSInputFile(card_path),
            caption=preview_caption,
            parse_mode="HTML",
            reply_markup=get_preview_keyboard(),
        )
    else:
        # Alohida rasm va alohida matn
        await message.answer_photo(photo=FSInputFile(card_path))
        await message.answer(
            preview_caption,
            parse_mode="HTML",
            reply_markup=get_preview_keyboard(),
        )


@router.callback_query(JobApplicationFSM.work_schedule, F.data == "skip_schedule")
async def step_schedule_skip(call: CallbackQuery, state: FSMContext, db_user: User):
    await state.update_data(work_schedule=None)
    await state.set_state(JobApplicationFSM.contact)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    kb = get_contact_keyboard(phone=db_user.phone, username=call.from_user.username)
    await call.message.answer(
        get_contact_prompt_text(),
        parse_mode="HTML",
        reply_markup=kb,
    )
    await call.answer()


@router.message(JobApplicationFSM.work_schedule, F.text)
async def step_schedule_entered(message: Message, state: FSMContext, db_user: User):
    sched = message.text.strip()
    await state.update_data(work_schedule=sched)
    await state.set_state(JobApplicationFSM.contact)
    kb = get_contact_keyboard(phone=db_user.phone, username=message.from_user.username)
    await message.answer(
        get_contact_prompt_text(),
        parse_mode="HTML",
        reply_markup=kb,
    )


@router.message(JobApplicationFSM.contact, F.contact)
async def step_contact_shared(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
):
    raw_phone = message.contact.phone_number
    phone_formatted = format_phone_number(raw_phone)

    # Foydalanuvchining telefon raqamini bazada saqlash
    db_user.phone = phone_formatted
    await session.commit()

    tg_user = message.from_user.username
    contact_info = phone_formatted

    await render_preview_and_proceed(message, state, contact_info, tg_user)


@router.message(JobApplicationFSM.contact, F.text)
async def step_contact_entered(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
):
    raw_text = message.text.strip()

    # Bekor qilish tekshiruvi
    if raw_text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Jarayon bekor qilindi.",
            reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
        )
        return

    # Agar "📱 +998... | @username" tugmasi bosilgan bo'lsa
    contact_info = raw_text.lstrip("📱").strip()
    tg_user = None
    if " | " in contact_info:
        parts = contact_info.split(" | ")
        contact_info = parts[0].strip()
        if len(parts) > 1 and parts[1].strip():
            tg_user = parts[1].replace("@", "").strip()

    # Telegram username aniqlash agar matnda bo'lsa
    if "@" in contact_info and not tg_user:
        match = re.search(r"@([A-Za-z0-9_]{3,})", contact_info)
        if match:
            tg_user = match.group(1)
            contact_info = re.sub(r",?\s*@[A-Za-z0-9_]{3,}", "", contact_info).strip(" ,|")

    if not tg_user and message.from_user.username:
        tg_user = message.from_user.username

    # Agar foydalanuvchida telefon raqam hali saqlanmagan bo'lsa va matnda telefon raqami topsak
    if not db_user.phone:
        match = re.search(r"(\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\b\d{9}\b)", raw_text)
        if match:
            db_user.phone = format_phone_number(match.group(1))
            await session.commit()

    await render_preview_and_proceed(message, state, contact_info, tg_user)



@router.callback_query(JobApplicationFSM.preview, F.data == "restart_job")
async def cb_restart_job(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    categories = await cat_repo.get_all_active()
    await state.clear()
    await state.set_state(JobApplicationFSM.category)
    await call.message.answer(
        "Keling, qaytadan boshlaymiz. <b>Kategoriya</b>ni tanlang:",
        parse_mode="HTML",
        reply_markup=get_categories_keyboard(categories),
    )
    await call.answer()


@router.callback_query(JobApplicationFSM.preview, F.data == "submit_job")
async def cb_submit_job(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    db_user: User,
    job_repo: JobRequestRepository,
    user_repo: UserRepository,
    settings_repo: SettingsRepository,
):
    data = await state.get_data()
    if not data or "position" not in data:
        await call.answer("Ma'lumotlar eskirgan, iltimos qaytadan boshlang.", show_alert=True)
        return

    setting = await settings_repo.get_settings()
    is_paid = setting.is_payment_enabled and setting.price_per_post > 0

    initial_status = JobStatus.DRAFT.value if is_paid else JobStatus.PENDING.value
    initial_payment_status = "unpaid" if is_paid else "free"
    initial_amount = setting.price_per_post if is_paid else 0

    # Bazada so'rov yaratish
    job = await job_repo.create(
        user_id=db_user.id,
        category_id=data.get("category_id"),
        request_type="job",
        position=data["position"],
        company=data["company"],
        requirements=data["requirements"],
        salary=data["salary"],
        contact=data["contact"],
        location=data.get("location"),
        work_schedule=data.get("work_schedule"),
        telegram_user=data.get("telegram_user"),
        post_text=data.get("post_text"),
        image_path=data.get("image_path"),
        status=initial_status,
        payment_status=initial_payment_status,
        payment_amount=initial_amount,
    )

    # Yakuniy post matniga aniq E'lon ID sini biriktirish
    final_post_text = PostGenerator.generate_job_post(
        position=data["position"],
        company=data["company"],
        requirements=data["requirements"],
        salary=data["salary"],
        contact=data["contact"],
        location=data.get("location"),
        work_schedule=data.get("work_schedule"),
        telegram_user=data.get("telegram_user"),
        category_name=data.get("category_name"),
        channel_username=settings.DEFAULT_CHANNEL_ID,
        job_id=job.id,
    )
    job.post_text = final_post_text
    await job_repo.session.flush()

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # AGAR TO'LOV YOQILGAN BO'LSA — TO'LOV VA CHEK SO'RASH OQIMI
    if is_paid:
        await state.set_state(JobApplicationFSM.waiting_for_receipt)
        await state.update_data(payment_job_id=job.id)

        formatted_price = f"{setting.price_per_post:,}".replace(",", " ") + " UZS"
        invoice_text = (
            f"💳 <b>VAKANSIYA UCHUN TO'LOV (E'lon #{job.id})</b>\n\n"
            f"E'loningiz moderatorlarga ko'rib chiqish uchun yuborilishi va kanalga chiqarilishi uchun to'lovni amalga oshiring:\n\n"
            f"💵 <b>E'lon narxi:</b> <b>{formatted_price}</b>\n"
            f"👤 <b>Karta egasi:</b> <b>{setting.card_holder}</b>\n"
            f"💳 <b>Karta raqami:</b>\n"
            f"<code>{setting.card_number}</code>\n"
            f"<i>(Nusxalash uchun karta raqami ustiga bir marta bosing)</i>\n\n"
            f"📸 <b>To'lovni amalga oshirgach, to'lov chekining fotosuratini (skrinshotini) shu yerga rasm sifatida yuboring:</b>"
        )
        await call.message.answer(invoice_text, parse_mode="HTML", reply_markup=get_cancel_receipt_keyboard(job.id))
        await call.answer()
        return

    # AGAR BEPUL BO'LSA — TO'G'RIDAN-TO'G'RI MODERATSIYAGA YUBORISH
    await state.clear()
    await call.answer("So'rovingiz qabul qilindi!", show_alert=True)
    await call.message.answer(
        f"✅ <b>Vakansiya so'rovingiz qabul qilindi! (ID: #{job.id})</b>\n\n"
        "Adminlarimiz tez orada e'loningizni ko'rib chiqadi va tasdiqlangach kanalga joylanadi.\n"
        "Holatni <b>'📋 Mening e'lonlarim'</b> bo'limida kuzatishingiz mumkin.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
    )

    # Barcha adminlarga xabar yuborish
    admins = await user_repo.get_all_admins()
    admin_notice = (
        f"🔔 <b>YANGI VAKANSIYA SO'ROVI! (ID: #{job.id})</b>\n\n"
        f"Yuboruvchi: {db_user.full_name} (@{db_user.username or 'yo_q'})\n"
        f"Lavozim: <b>{job.position}</b>\n"
        f"Kompaniya: <b>{job.company}</b>\n"
        f"Maosh: <b>{job.salary}</b>\n\n"
        f"{job.post_text}"
    )

    for admin in admins:
        try:
            if job.image_path and os.path.exists(job.image_path):
                if len(admin_notice) <= 1024:
                    await bot.send_photo(
                        chat_id=admin.tg_id,
                        photo=FSInputFile(job.image_path),
                        caption=admin_notice,
                        parse_mode="HTML",
                        reply_markup=get_admin_moderation_keyboard(job.id),
                    )
                else:
                    await bot.send_photo(chat_id=admin.tg_id, photo=FSInputFile(job.image_path))
                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=admin_notice,
                        parse_mode="HTML",
                        reply_markup=get_admin_moderation_keyboard(job.id),
                    )
            else:
                await bot.send_message(
                    chat_id=admin.tg_id,
                    text=admin_notice,
                    parse_mode="HTML",
                    reply_markup=get_admin_moderation_keyboard(job.id),
                )
        except Exception:
            continue


# --- TO'LOV CHEKI QABUL QILISH ---
@router.message(JobApplicationFSM.waiting_for_receipt, F.photo)
@router.message(JobApplicationFSM.waiting_for_receipt, F.document)
async def step_job_receipt_received(
    message: Message,
    state: FSMContext,
    bot: Bot,
    db_user: User,
    job_repo: JobRequestRepository,
    user_repo: UserRepository,
):
    data = await state.get_data()
    job_id = data.get("payment_job_id")
    if not job_id:
        await message.answer("Xatolik: e'lon ma'lumotlari topilmadi. Qaytadan urinib ko'ring.")
        await state.clear()
        return

    job = await job_repo.get_by_id(job_id)
    if not job:
        await message.answer("Xatolik: e'lon topilmadi.")
        await state.clear()
        return

    # Rasmni yuklab olish va saqlash
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id
    else:
        await message.answer("⚠️ Iltimos, chekni fotosurat yoki rasm fayli sifatida yuboring.")
        return

    receipts_dir = BASE_DIR / "data" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    filename = f"receipt_job_{job.id}_{int(time.time())}.jpg"
    destination = receipts_dir / filename

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination)
    receipt_path_str = str(destination)

    # Bazadagi statusni yangilash
    await job_repo.update_status(job_id=job.id, status=JobStatus.PENDING.value)
    await job_repo.update_payment(
        job_id=job.id,
        receipt_image_path=receipt_path_str,
        payment_status="pending_verification",
    )

    await state.clear()
    await message.answer(
        f"🧾 <b>To'lov cheki va vakansiya so'rovingiz qabul qilindi! (ID: #{job.id})</b>\n\n"
        "Administrator to'lovni va e'loningizni tekshirib chiqqach, u avtomatik ravishda kanalga chiqariladi.\n"
        "Holatni <b>'📋 Mening e'lonlarim'</b> bo'limida kuzatishingiz mumkin.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
    )

    # Barcha adminlarga bildirishnoma yuborish (E'lon banneri + To'lov cheki)
    admins = await user_repo.get_all_admins()
    amt_text = f"{job.payment_amount:,}".replace(",", " ") + " UZS" if job.payment_amount else ""
    admin_notice = (
        f"🔔 <b>YANGI VAKANSIYA VA TO'LOV CHEKI! (ID: #{job.id})</b>\n\n"
        f"Yuboruvchi: {db_user.full_name} (@{db_user.username or 'yo_q'})\n"
        f"Lavozim: <b>{job.position}</b>\n"
        f"Kompaniya: <b>{job.company}</b>\n"
        f"To'lov summasi: <b>{amt_text}</b>\n\n"
        f"{job.post_text}"
    )

    for admin in admins:
        try:
            # 1. E'lon kartasini yuborish
            if job.image_path and os.path.exists(job.image_path):
                if len(admin_notice) <= 1024:
                    await bot.send_photo(
                        chat_id=admin.tg_id,
                        photo=FSInputFile(job.image_path),
                        caption=admin_notice,
                        parse_mode="HTML",
                    )
                else:
                    await bot.send_photo(chat_id=admin.tg_id, photo=FSInputFile(job.image_path))
                    await bot.send_message(chat_id=admin.tg_id, text=admin_notice, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=admin.tg_id, text=admin_notice, parse_mode="HTML")

            # 2. To'lov chekini alohida yuborish (tagida tasdiqlash/rad etish tugmalari bilan)
            receipt_caption = (
                f"🧾 <b>To'lov cheki (E'lon #{job.id})</b>\n"
                f"💵 Belgilangan summa: <b>{amt_text}</b>\n\n"
                "To'lovni va e'lonni tasdiqlaysizmi?"
            )
            await bot.send_photo(
                chat_id=admin.tg_id,
                photo=FSInputFile(receipt_path_str),
                caption=receipt_caption,
                parse_mode="HTML",
                reply_markup=get_admin_moderation_keyboard(job.id),
            )
        except Exception:
            continue


@router.message(JobApplicationFSM.waiting_for_receipt)
async def step_job_invalid_receipt_sent(message: Message):
    if message.text == "❌ Bekor qilish":
        return
    await message.answer(
        "⚠️ <b>Iltimos, to'lov chekining fotosuratini (skrinshotini) rasm formatida yuboring!</b>\n\n"
        "To'lov ilovangizdan (Payme, Click, bank ilovasi) to'lov chekining skrinshotini oling va shu yerga rasm qilib tashlang.",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("cancel_receipt_"))
async def cb_job_cancel_receipt(
    call: CallbackQuery, state: FSMContext, db_user: User, job_repo: JobRequestRepository
):
    job_id = int(call.data.replace("cancel_receipt_", ""))
    await job_repo.update_status(
        job_id=job_id, status=JobStatus.REJECTED.value, rejection_reason="To'lov foydalanuvchi tomonidan bekor qilindi"
    )
    await state.clear()
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(
        "❌ E'lon va to'lov jarayoni bekor qilindi.",
        reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
    )
    await call.answer("Bekor qilindi")
