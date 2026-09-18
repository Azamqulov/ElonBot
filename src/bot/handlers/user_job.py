import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from src.bot.states.job_states import JobApplicationFSM
from src.bot.keyboards.inline_keyboards import (
    get_categories_keyboard,
    get_salary_keyboard,
    get_skip_keyboard,
    get_preview_keyboard,
    get_admin_moderation_keyboard,
)
from src.bot.keyboards.reply_keyboards import get_main_menu_keyboard
from src.database.models import User, JobStatus
from src.database.repositories import CategoryRepository, JobRequestRepository, UserRepository
from src.services.post_generator import PostGenerator
from src.services.image_generator import image_generator
from src.bot.config import settings

router = Router()


@router.message(F.text == "🆕 Yangi vakansiya berish")
async def start_job_application(message: Message, state: FSMContext, cat_repo: CategoryRepository):
    categories = await cat_repo.get_all_active()
    if not categories:
        await message.answer("Hozircha tizimda faol kategoriyalar mavjud emas. Iltimos adminga murojaat qiling.")
        return

    await state.clear()
    await state.set_state(JobApplicationFSM.category)
    await message.answer(
        "1-qadam: <b>Ish turi / Kategoriya</b>ni tanlang:",
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
    comp = message.text.strip()
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
        "5-qadam: <b>Maosh miqdorini</b> kiriting (masalan: <i>10 000 000 UZS</i> yoki <i>800 - 1200 USD</i>)\n"
        "Yoki pastdagi <b>'🤝 Kelishiladi'</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=get_salary_keyboard(),
    )


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
    sal = message.text.strip()
    await state.update_data(salary=sal)
    await state.set_state(JobApplicationFSM.location)
    await message.answer(
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


@router.callback_query(JobApplicationFSM.work_schedule, F.data == "skip_schedule")
async def step_schedule_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(work_schedule=None)
    await state.set_state(JobApplicationFSM.contact)
    await call.message.edit_text(
        "8-qadam: <b>Bog'lanish uchun aloqa ma'lumotlarini</b> kiriting:\n"
        "<i>(Telefon raqami va Telegram username, masalan: +998 90 123 45 67, @hr_menejer)</i>",
        parse_mode="HTML",
    )


@router.message(JobApplicationFSM.work_schedule, F.text)
async def step_schedule_entered(message: Message, state: FSMContext):
    sched = message.text.strip()
    await state.update_data(work_schedule=sched)
    await state.set_state(JobApplicationFSM.contact)
    await message.answer(
        "8-qadam: <b>Bog'lanish uchun aloqa ma'lumotlarini</b> kiriting:\n"
        "<i>(Telefon raqami va Telegram username, masalan: +998 90 123 45 67, @hr_menejer)</i>",
        parse_mode="HTML",
    )


@router.message(JobApplicationFSM.contact, F.text)
async def step_contact_entered(message: Message, state: FSMContext, bot: Bot):
    contact_info = message.text.strip()
    await state.update_data(contact=contact_info)

    # Telegram user aniqlash
    tg_user = None
    if "@" in contact_info:
        for word in contact_info.split():
            if word.startswith("@") and len(word) > 2:
                tg_user = word.replace("@", "")
                break
    if not tg_user and message.from_user.username:
        tg_user = message.from_user.username

    await state.update_data(telegram_user=tg_user)

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

    # Preview taqdim etish
    preview_caption = (
        "🔍 <b>E'LONINGIZ KO'RINISHI (PREVIEW):</b>\n\n"
        f"{post_text}\n\n"
        "Barcha ma'lumotlar to'g'riligini tekshiring va quyidagi amallardan birini tanlang:"
    )

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
):
    data = await state.get_data()
    if not data or "position" not in data:
        await call.answer("Ma'lumotlar eskirgan, iltimos qaytadan boshlang.", show_alert=True)
        return

    # Bazada so'rov yaratish
    job = await job_repo.create(
        user_id=db_user.id,
        category_id=data.get("category_id"),
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
        status=JobStatus.PENDING.value,
    )

    await state.clear()
    await call.answer("So'rovingiz qabul qilindi!", show_alert=True)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

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
