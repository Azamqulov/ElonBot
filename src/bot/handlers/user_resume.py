import os
import re
import time
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.states.job_states import ResumeApplicationFSM
from src.bot.keyboards.inline_keyboards import (
    get_categories_keyboard,
    get_salary_keyboard,
    get_skip_keyboard,
    get_resume_preview_keyboard,
    get_admin_moderation_keyboard,
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

router = Router()


def get_contact_prompt_text() -> str:
    return (
        "9-qadam: <b>Bog'lanish uchun aloqa ma'lumotlarini</b> kiriting:\n\n"
        "<i>💡 Pastdagi tugmani bosib telefon raqamingiz va Telegram profilingizni tezda yuborishingiz "
        "yoki boshqa raqam va @username ni qo'lda yozishingiz mumkin.</i>"
    )


# 1. Kategoriya tanlanganda
@router.callback_query(ResumeApplicationFSM.category, F.data.startswith("cat_"))
async def step_resume_category_selected(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    category_id = int(call.data.replace("cat_", ""))
    cat = await cat_repo.get_by_id(category_id)
    if not cat:
        await call.answer("Kategoriya topilmadi!", show_alert=True)
        return

    await state.update_data(category_id=cat.id, category_name=cat.name)
    await state.set_state(ResumeApplicationFSM.specialty)

    await call.message.edit_text(
        f"Tanlangan soha: <b>{cat.name}</b>\n\n"
        "1-qadam: <b>Mutaxassislik / Yo'nalishingizni</b> kiriting:\n"
        "<i>(Masalan: Grafik Dizayner & AI Specialist, Full-stack Python Dasturchi, SMM menejer)</i>",
        parse_mode="HTML",
    )


# 2. Mutaxassislik kiritilganda
@router.message(ResumeApplicationFSM.specialty, F.text)
async def step_specialty_entered(message: Message, state: FSMContext):
    spec = message.text.strip()
    if len(spec) < 3:
        await message.answer("Mutaxassislik nomi juda qisqa. Iltimos to'liqroq yozing:")
        return

    await state.update_data(specialty=spec)
    await state.set_state(ResumeApplicationFSM.bio)
    await message.answer(
        "2-qadam: <b>O'zingiz haqingizda qisqa ta'rif yoki shioringizni</b> kiriting:\n"
        "<i>(Masalan: Brendingiz uchun sifatli, zamonaviy va sotuvchi vizual yechimlar yarataman)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("bio"),
    )


# 3. Bio skip
@router.callback_query(ResumeApplicationFSM.bio, F.data == "skip_bio")
async def step_bio_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(bio=None)
    await state.set_state(ResumeApplicationFSM.full_name)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(
        "3-qadam: <b>Ismingizni</b> kiriting:\n"
        "<i>(Masalan: Said Amir yoki Azizbek)</i>",
        parse_mode="HTML",
    )
    await call.answer()


# 3. Bio kiritilganda
@router.message(ResumeApplicationFSM.bio, F.text)
async def step_bio_entered(message: Message, state: FSMContext):
    await state.update_data(bio=message.text.strip())
    await state.set_state(ResumeApplicationFSM.full_name)
    await message.answer(
        "3-qadam: <b>Ismingizni</b> kiriting:\n"
        "<i>(Masalan: Said Amir yoki Azizbek)</i>",
        parse_mode="HTML",
    )


# 4. Ism kiritilganda -> Tajribani so'rash
@router.message(ResumeApplicationFSM.full_name, F.text)
async def step_full_name_entered(message: Message, state: FSMContext):
    name = PostGenerator.format_title_case(message.text.strip())
    if len(name) < 2:
        await message.answer("Ism juda qisqa. Iltimos to'liqroq yozing:")
        return

    await state.update_data(name=name)
    await state.set_state(ResumeApplicationFSM.experience)
    await message.answer(
        "4-qadam: <b>Ish tajribangizni</b> kiriting:\n"
        "<i>(Masalan: 2 yil, 3+ yil yoki Boshlang'ich)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("exp"),
    )


# 4. Tajriba skip
@router.callback_query(ResumeApplicationFSM.experience, F.data == "skip_exp")
async def step_experience_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(experience=None)
    await state.set_state(ResumeApplicationFSM.services)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(
        "5-qadam: <b>Ko'rsatadigan xizmatlaringiz ro'yxatini</b> kiriting:\n\n"
        "<i>Masalan:\n"
        "SMM: Postlar, Stories va Reels cover\n"
        "Brending: Logotip va firma stili\n"
        "Poligrafiya: Flayer, vizitka va bannerlar</i>",
        parse_mode="HTML",
    )
    await call.answer()


# 4. Tajriba kiritilganda
@router.message(ResumeApplicationFSM.experience, F.text)
async def step_experience_entered(message: Message, state: FSMContext):
    exp = message.text.strip()
    await state.update_data(experience=exp)
    await state.set_state(ResumeApplicationFSM.services)
    await message.answer(
        "5-qadam: <b>Ko'rsatadigan xizmatlaringiz ro'yxatini</b> kiriting:\n\n"
        "<i>Masalan:\n"
        "SMM: Postlar, Stories va Reels cover\n"
        "Brending: Logotip va firma stili\n"
        "Poligrafiya: Flayer, vizitka va bannerlar</i>",
        parse_mode="HTML",
    )


# 5. Xizmatlar kiritilganda
@router.message(ResumeApplicationFSM.services, F.text)
async def step_services_entered(message: Message, state: FSMContext):
    srv = message.text.strip()
    if len(srv) < 5:
        await message.answer("Xizmatlar tavsifi juda qisqa. Iltimos to'liqroq yozing:")
        return

    await state.update_data(services=srv)
    await state.set_state(ResumeApplicationFSM.tools)
    await message.answer(
        "6-qadam: <b>Qaysi dasturlar va texnologiyalardan foydalanasiz?</b>\n"
        "<i>(Masalan: Photoshop, Illustrator va AI (Claude, ChatGPT, Midjourney))</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("tools"),
    )


# 6. Dasturlar skip
@router.callback_query(ResumeApplicationFSM.tools, F.data == "skip_tools")
async def step_tools_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(tools=None)
    await state.set_state(ResumeApplicationFSM.price)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(
        "7-qadam: <b>Xizmat narxi yoki kutilayotgan maoshingizni</b> kiriting.\n\n"
        "💡 Valyutani (<b>UZS</b> yoki <b>USD</b>) tanlashingiz yoki to'g'ridan-to'g'ri yozishingiz mumkin:\n"
        "<i>(Masalan: 10 000 000 UZS yoki 800 - 1200 USD)</i>",
        parse_mode="HTML",
        reply_markup=get_salary_keyboard(),
    )
    await call.answer()


# 7. Dasturlar kiritilganda
@router.message(ResumeApplicationFSM.tools, F.text)
async def step_tools_entered(message: Message, state: FSMContext):
    await state.update_data(tools=message.text.strip())
    await state.set_state(ResumeApplicationFSM.price)
    await message.answer(
        "7-qadam: <b>Xizmat narxi yoki kutilayotgan maoshingizni</b> kiriting.\n\n"
        "💡 Valyutani (<b>UZS</b> yoki <b>USD</b>) tanlashingiz yoki to'g'ridan-to'g'ri yozishingiz mumkin:\n"
        "<i>(Masalan: 10 000 000 UZS yoki 800 - 1200 USD)</i>",
        parse_mode="HTML",
        reply_markup=get_salary_keyboard(),
    )


# Valyuta UZS tanlanganda
@router.callback_query(ResumeApplicationFSM.price, F.data == "salary_curr_uzs")
async def cb_resume_salary_uzs(call: CallbackQuery, state: FSMContext):
    await state.update_data(salary_currency="UZS")
    text = (
        "Valyuta: 🇺🇿 <b>UZS (So'm)</b> tanlandi.\n\n"
        "Endi xizmat narxini kiriting:\n"
        "<i>(Masalan: 5 000 000 yoki 1 000 000 - 3 000 000)</i>"
    )
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_currency_selected_keyboard("UZS"))
    except Exception:
        pass
    await call.answer("UZS tanlandi")


# Valyuta USD tanlanganda
@router.callback_query(ResumeApplicationFSM.price, F.data == "salary_curr_usd")
async def cb_resume_salary_usd(call: CallbackQuery, state: FSMContext):
    await state.update_data(salary_currency="USD")
    text = (
        "Valyuta: 🇺🇸 <b>USD (Dollar)</b> tanlandi.\n\n"
        "Endi xizmat narxini kiriting:\n"
        "<i>(Masalan: 500 yoki 800 - 1200)</i>"
    )
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_currency_selected_keyboard("USD"))
    except Exception:
        pass
    await call.answer("USD tanlandi")


# 8. Narx / Maosh - Kelishiladi
@router.callback_query(ResumeApplicationFSM.price, F.data == "salary_negotiable")
async def step_price_negotiable(call: CallbackQuery, state: FSMContext):
    await state.update_data(price="Loyiha hajmiga qarab kelishiladi")
    await state.set_state(ResumeApplicationFSM.portfolio)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(
        "8-qadam: <b>Portfolio havolasini</b> yuboring:\n"
        "<i>(Masalan: Behance, GitHub, Telegram kanal yoki sayt havolasi)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("portfolio"),
    )
    await call.answer()


# 8. Narx kiritilganda
@router.message(ResumeApplicationFSM.price, F.text)
async def step_price_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    curr = data.get("salary_currency")
    price = PostGenerator.format_salary_amount(message.text, curr)
    await state.update_data(price=price)
    await state.set_state(ResumeApplicationFSM.portfolio)
    await message.answer(
        f"Narx: <b>{price}</b> qilib belgilandi.\n\n"
        "8-qadam: <b>Portfolio havolasini</b> yuboring:\n"
        "<i>(Masalan: Behance, GitHub, Telegram kanal yoki sayt havolasi)</i>",
        parse_mode="HTML",
        reply_markup=get_skip_keyboard("portfolio"),
    )


# 8. Portfolio skip
@router.callback_query(ResumeApplicationFSM.portfolio, F.data == "skip_portfolio")
async def step_portfolio_skip(call: CallbackQuery, state: FSMContext, db_user: User):
    await state.update_data(portfolio=None)
    await state.set_state(ResumeApplicationFSM.contact)
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


# 8. Portfolio kiritilganda
@router.message(ResumeApplicationFSM.portfolio, F.text)
async def step_portfolio_entered(message: Message, state: FSMContext, db_user: User):
    await state.update_data(portfolio=message.text.strip())
    await state.set_state(ResumeApplicationFSM.contact)
    kb = get_contact_keyboard(phone=db_user.phone, username=message.from_user.username)
    await message.answer(
        get_contact_prompt_text(),
        parse_mode="HTML",
        reply_markup=kb,
    )


# 9. Aloqa ma'lumotlari - Contact tugmasi
@router.message(ResumeApplicationFSM.contact, F.contact)
async def step_resume_contact_shared(message: Message, state: FSMContext, user_repo: UserRepository):
    contact = message.contact
    phone_clean = contact.phone_number
    if not phone_clean.startswith("+"):
        phone_clean = f"+{phone_clean}"

    user = await user_repo.get_by_tg_id(message.from_user.id)
    if user:
        user.phone = phone_clean

    tg_username = message.from_user.username
    await render_resume_preview_and_proceed(message, state, phone_clean, tg_username)


# 9. Aloqa ma'lumotlari - Matn orqali
@router.message(ResumeApplicationFSM.contact, F.text)
async def step_resume_contact_text(message: Message, state: FSMContext, db_user: User):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ E'lon bekor qilindi.", reply_markup=get_main_menu_keyboard(db_user.is_admin()))
        return

    # "📱 +998... | @username" tugmasi bosilgan bo'lsa
    if text.startswith("📱"):
        clean_btn = text.replace("📱", "").strip()
        parts = clean_btn.split("|")
        phone_part = parts[0].strip()
        user_part = parts[1].replace("@", "").strip() if len(parts) > 1 else message.from_user.username
        await render_resume_preview_and_proceed(message, state, phone_part, user_part)
        return

    # Oddiy matn kiritilganda
    phone_match = re.search(r"(\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\b\d{9,12}\b)", text)
    user_match = re.search(r"@([A-Za-z0-9_]+)", text)

    phone_val = phone_match.group(0) if phone_match else text
    user_val = user_match.group(1) if user_match else message.from_user.username

    await render_resume_preview_and_proceed(message, state, phone_val, user_val)


async def render_resume_preview_and_proceed(message: Message, state: FSMContext, contact_info: str, tg_user: str | None = None):
    await state.update_data(contact=contact_info, telegram_user=tg_user)
    data = await state.get_data()

    # Rezyume post matnini generatsiya qilish (3-rasm formati)
    post_text = PostGenerator.generate_resume_post(
        specialty=data["specialty"],
        name=data.get("name", ""),
        bio=data.get("bio"),
        experience=data.get("experience"),
        services=data["services"],
        tools=data.get("tools"),
        price=data.get("price", "Kelishiladi"),
        portfolio=data.get("portfolio"),
        contact=data["contact"],
        telegram_user=data.get("telegram_user"),
        category_name=data.get("category_name"),
        channel_username=settings.DEFAULT_CHANNEL_ID,
    )

    # Rasm kartasini generatsiya qilish (2-rasm dizayni, badge: REZYUME)
    card_path = image_generator.generate_job_card(
        position=data["specialty"],
        company=data.get("name", "Mutaxassis"),
        salary=data.get("price", "Kelishiladi"),
        category_name=data.get("category_name", "Rezyume"),
        badge_text="REZYUME",
        price_label="Narx:",
        channel_watermark=settings.WATERMARK_TEXT,
    )

    await state.update_data(post_text=post_text, image_path=card_path)
    await state.set_state(ResumeApplicationFSM.preview)

    preview_caption = (
        "🔍 <b>REZYUME KO'RINISHI (PREVIEW):</b>\n\n"
        f"{post_text}\n\n"
        "Barcha ma'lumotlar to'g'riligini tekshiring va quyidagi amallardan birini tanlang:"
    )

    await message.answer("✅ Aloqa ma'lumotlari qabul qilindi.", reply_markup=ReplyKeyboardRemove())

    if len(preview_caption) <= 1024:
        await message.answer_photo(
            photo=FSInputFile(card_path),
            caption=preview_caption,
            parse_mode="HTML",
            reply_markup=get_resume_preview_keyboard(),
        )
    else:
        await message.answer_photo(photo=FSInputFile(card_path))
        await message.answer(
            preview_caption,
            parse_mode="HTML",
            reply_markup=get_resume_preview_keyboard(),
        )


# 10. Moderatsiyaga yuborish
@router.callback_query(ResumeApplicationFSM.preview, F.data == "submit_resume")
async def step_submit_resume(
    call: CallbackQuery,
    state: FSMContext,
    job_repo: JobRequestRepository,
    user_repo: UserRepository,
    settings_repo: SettingsRepository,
    db_user: User,
    bot: Bot,
):
    data = await state.get_data()

    setting = await settings_repo.get_settings()
    is_paid = setting.is_payment_enabled and setting.price_per_post > 0

    initial_status = JobStatus.DRAFT.value if is_paid else JobStatus.PENDING.value
    initial_payment_status = "unpaid" if is_paid else "free"
    initial_amount = setting.price_per_post if is_paid else 0

    job = await job_repo.create(
        user_id=db_user.id,
        category_id=data.get("category_id"),
        request_type="resume",
        position=data["specialty"],
        company=data.get("name", "Mutaxassis"),
        requirements=data["services"],
        salary=data.get("price", "Kelishiladi"),
        contact=data["contact"],
        telegram_user=data.get("telegram_user"),
        bio=data.get("bio"),
        experience=data.get("experience"),
        tools=data.get("tools"),
        portfolio=data.get("portfolio"),
        post_text=data.get("post_text"),
        image_path=data.get("image_path"),
        status=initial_status,
        payment_status=initial_payment_status,
        payment_amount=initial_amount,
    )

    # Yakuniy rezyume post matniga aniq E'lon ID sini biriktirish
    final_post_text = PostGenerator.generate_resume_post(
        specialty=data["specialty"],
        name=data.get("name", ""),
        bio=data.get("bio"),
        experience=data.get("experience"),
        services=data["services"],
        tools=data.get("tools"),
        price=data.get("price", "Kelishiladi"),
        portfolio=data.get("portfolio"),
        contact=data["contact"],
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
        await state.set_state(ResumeApplicationFSM.waiting_for_receipt)
        await state.update_data(payment_job_id=job.id)

        formatted_price = f"{setting.price_per_post:,}".replace(",", " ") + " UZS"
        invoice_text = (
            f"💳 <b>REZYUME UCHUN TO'LOV (E'lon #{job.id})</b>\n\n"
            f"Rezyumeingiz moderatorlarga ko'rib chiqish uchun yuborilishi va kanalga chiqarilishi uchun to'lovni amalga oshiring:\n\n"
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

    # AGAR BEPUL BO'LSA — TO'ĞRIDAN-TO'ĞRI MODERATSIYAGA YUBORISH
    await state.clear()
    await call.message.answer(
        "🎉 <b>Rezyumeingiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "Tez orada kanal administratorlari rezyumeni ko'rib chiqadi. "
        "Tasdiqlangach, avtomatik ravishda e'lon kanalga joylanadi.\n\n"
        "Holatni <b>📋 Mening e'lonlarim</b> bo'limida kuzatishingiz mumkin.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(db_user.is_admin()),
    )
    await call.answer()

    # Barcha adminlarga xabar yuborish
    admins = await user_repo.get_all_admins()
    admin_caption = (
        f"🔔 <b>YANGI REZYUME SO'ROVI #{job.id}</b>\n\n"
        f"<b>Mutaxassis:</b> {db_user.full_name} (@{db_user.username or 'yoq'})\n"
        f"<b>Yo'nalish:</b> {job.position}\n"
        f"<b>Narx/Maosh:</b> {job.salary}\n\n"
        f"{job.post_text}"
    )

    for admin in admins:
        try:
            if job.image_path and os.path.exists(job.image_path):
                if len(admin_caption) <= 1024:
                    await bot.send_photo(
                        chat_id=admin.tg_id,
                        photo=FSInputFile(job.image_path),
                        caption=admin_caption,
                        parse_mode="HTML",
                        reply_markup=get_admin_moderation_keyboard(job.id),
                    )
                else:
                    await bot.send_photo(chat_id=admin.tg_id, photo=FSInputFile(job.image_path))
                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=admin_caption,
                        parse_mode="HTML",
                        reply_markup=get_admin_moderation_keyboard(job.id),
                    )
            else:
                await bot.send_message(
                    chat_id=admin.tg_id,
                    text=admin_caption,
                    parse_mode="HTML",
                    reply_markup=get_admin_moderation_keyboard(job.id),
                )
        except Exception:
            pass


# --- REZYUME TO'LOV CHEKI QABUL QILISH ---
@router.message(ResumeApplicationFSM.waiting_for_receipt, F.photo)
@router.message(ResumeApplicationFSM.waiting_for_receipt, F.document)
async def step_resume_receipt_received(
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
        await message.answer("Xatolik: rezyume ma'lumotlari topilmadi. Qaytadan urinib ko'ring.")
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
    filename = f"receipt_resume_{job.id}_{int(time.time())}.jpg"
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
        f"🧾 <b>To'lov cheki va rezyumeingiz qabul qilindi! (ID: #{job.id})</b>\n\n"
        "Administrator to'lovni va rezyumeni ko'rib chiqqach, u avtomatik tarzda kanalga chiqariladi.\n"
        "Holatni <b>'📋 Mening e'lonlarim'</b> bo'limida kuzatishingiz mumkin.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
    )

    # Barcha adminlarga bildirishnoma yuborish (Rezyume banneri + To'lov cheki)
    admins = await user_repo.get_all_admins()
    amt_text = f"{job.payment_amount:,}".replace(",", " ") + " UZS" if job.payment_amount else ""
    admin_notice = (
        f"🔔 <b>YANGI REZYUME VA TO'LOV CHEKI! (ID: #{job.id})</b>\n\n"
        f"Mutaxassis: {db_user.full_name} (@{db_user.username or 'yoq'})\n"
        f"Yo'nalish: <b>{job.position}</b>\n"
        f"Narx/Maosh: <b>{job.salary}</b>\n"
        f"To'lov summasi: <b>{amt_text}</b>\n\n"
        f"{job.post_text}"
    )

    for admin in admins:
        try:
            # 1. Rezyume kartasini yuborish
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
                f"🧾 <b>To'lov cheki (Rezyume #{job.id})</b>\n"
                f"💵 Belgilangan summa: <b>{amt_text}</b>\n\n"
                "To'lovni va rezyumeni tasdiqlaysizmi?"
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


@router.message(ResumeApplicationFSM.waiting_for_receipt)
async def step_resume_invalid_receipt_sent(message: Message):
    if message.text == "❌ Bekor qilish":
        return
    await message.answer(
        "⚠️ <b>Iltimos, to'lov chekining fotosuratini (skrinshotini) rasm formatida yuboring!</b>\n\n"
        "To'lov ilovangizdan (Payme, Click, bank ilovasi) to'lov chekining skrinshotini oling va shu yerga rasm qilib tashlang.",
        parse_mode="HTML",
    )


# 11. Qaytadan to'ldirish
@router.callback_query(ResumeApplicationFSM.preview, F.data == "restart_resume")
async def step_restart_resume(call: CallbackQuery, state: FSMContext, cat_repo: CategoryRepository):
    categories = await cat_repo.get_all_active()
    await state.clear()
    await state.set_state(ResumeApplicationFSM.category)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Qaytadan to'ldirish boshlandi.\n\n"
        "1-qadam: <b>Sohangizni / Kategoriya</b>ni tanlang:",
        parse_mode="HTML",
        reply_markup=get_categories_keyboard(categories),
    )
    await call.answer()
