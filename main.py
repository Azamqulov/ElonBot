import asyncio
import logging
import sys

# Windows konsolida UTF-8 kodlashini faollashtirish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.config import settings
from src.database.connection import init_db
from src.bot.middlewares.db_middleware import DatabaseMiddleware
from src.bot.handlers import common, user_job, user_resume, admin, superadmin

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ElonBot")


async def main():
    logger.info("ElonBot ishga tushirilmoqda...")

    # 1. Ma'lumotlar bazasini initsializatsiya qilish
    logger.info("Ma'lumotlar bazasi tekshirilmoqda...")
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning(
            "DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan! "
            "Iltimos .env fayliga haqiqiy Telegram Bot Tokenini kiriting."
        )

    # 2. Bot va Dispatcher yaratish
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Middleware ulash
    dp.update.middleware(DatabaseMiddleware())

    # 4. Routerlarni ro'yxatdan o'tkazish
    dp.include_router(common.router)
    dp.include_router(user_job.router)
    dp.include_router(user_resume.router)
    dp.include_router(admin.router)
    dp.include_router(superadmin.router)

    logger.info("Barcha routerlar va middleware'lar muvaffaqiyatli ulandi.")

    # 5. Telegram Menu buyruqlarini ro'yxatdan o'tkazish
    bot_commands = [
        BotCommand(command="new", description="🆕 Yangi e'lon berish (Vakansiya / Rezyume)"),
        BotCommand(command="my_requests", description="📋 Mening e'lonlarim"),
        BotCommand(command="admin", description="🛡️ Admin paneli"),
        BotCommand(command="help", description="ℹ️ Bot haqida va Support"),
        BotCommand(command="cancel", description="❌ Jarayonni bekor qilish"),
    ]
    try:
        await bot.set_my_commands(bot_commands)
        logger.info("Bot komandalar menyusi muvaffaqiyatli sozlandi.")
    except Exception as e:
        logger.warning(f"Komandalar menyusini o'rnatishda xatolik: {e}")

    # 6. Pollingni boshlash
    try:
        # Eski kutilmagan update'larni tozalash
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot polling rejimida tinglashni boshladi. To'xtatish uchun Ctrl+C bosing.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot sessiyasi yopildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
