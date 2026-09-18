from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.database.models import User, JobStatus
from src.database.repositories import JobRequestRepository
from src.bot.keyboards.reply_keyboards import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db_user: User):
    await state.clear()
    is_admin = db_user.is_admin()
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "<b>Vakansiya E'lon Tayyorlash Botiga</b> xush kelibsiz.\n"
        "Ushbu bot orqali siz kanallarimiz uchun chiroyli dizayndagi rasmli karta va "
        "standart formatlangan vakansiya e'lonini tayyorlashingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇"
    )
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin),
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext, db_user: User):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer(
            "Jarayon bekor qilindi.",
            reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
        )
    else:
        await message.answer(
            "Hozirda faol jarayon mavjud emas.",
            reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
        )


@router.callback_query(F.data == "cancel_action")
async def cb_cancel(call: CallbackQuery, state: FSMContext, db_user: User):
    await state.clear()
    await call.answer("Jarayon bekor qilindi.")
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(
        "Bosh sahifaga qaytdingiz.",
        reply_markup=get_main_menu_keyboard(is_admin=db_user.is_admin()),
    )


@router.message(F.text == "ℹ️ Bot haqida")
@router.message(Command("help"))
async def cmd_about(message: Message):
    text = (
        "ℹ️ <b>ElonBot haqida ma'lumot:</b>\n\n"
        "1. <b>E'lon berish:</b> '🆕 Yangi vakansiya berish' tugmasini bosing va savollarga javob bering.\n"
        "2. <b>Dizayn:</b> Bot siz kiritgan ma'lumotlar asosida avtomatik professional rasm va matn tayyorlaydi.\n"
        "3. <b>Moderatsiya:</b> E'loningiz adminlar tomonidan ko'rib chiqiladi va tasdiqlangach to'g'ridan-to'g'ri kanalga chiqariladi.\n"
        "4. <b>Holatni kuzatish:</b> '📋 Mening e'lonlarim' bo'limida barcha e'lonlaringiz holatini ko'rishingiz mumkin."
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📋 Mening e'lonlarim")
@router.message(Command("my_requests"))
async def cmd_my_requests(message: Message, db_user: User, job_repo: JobRequestRepository):
    jobs = await job_repo.get_user_jobs(user_id=db_user.id, limit=5)
    if not jobs:
        await message.answer("Sizda hali vakansiya e'lonlari mavjud emas.")
        return

    status_labels = {
        JobStatus.DRAFT.value: "📝 Qoralama",
        JobStatus.PENDING.value: "⏳ Kutilmoqda (moderatsiyada)",
        JobStatus.APPROVED.value: "✅ Tasdiqlangan",
        JobStatus.REJECTED.value: "❌ Rad etilgan",
        JobStatus.POSTED.value: "🚀 Kanalga chiqarilgan",
    }

    text_parts = ["📋 <b>Sizning oxirgi vakansiya e'lonlaringiz:</b>\n"]
    for j in jobs:
        stat = status_labels.get(j.status, j.status)
        created = j.created_at.strftime("%d.%m.%Y %H:%M")
        text_parts.append(
            f"🔹 <b>#{j.id} - {j.position}</b> ({j.company})\n"
            f"   Holat: <b>{stat}</b>\n"
            f"   Sana: {created}"
        )
        if j.status == JobStatus.REJECTED.value and j.rejection_reason:
            text_parts.append(f"   ⚠️ <i>Rad etish sababi: {j.rejection_reason}</i>")
        text_parts.append("")

    await message.answer("\n".join(text_parts), parse_mode="HTML")
