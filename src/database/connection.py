import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import select
from src.bot.config import settings, BASE_DIR
from src.database.models import Base, Category, User, UserRole, BotSetting

# Baza papkasini yaratish (agar SQLite bo'lsa)
if "sqlite" in settings.DATABASE_URL:
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    db_full_path = (BASE_DIR / db_path).resolve()
    db_full_path.parent.mkdir(parents=True, exist_ok=True)
    engine_url = f"sqlite+aiosqlite:///{db_full_path}"
else:
    engine_url = settings.DATABASE_URL

engine = create_async_engine(
    engine_url,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DEFAULT_CATEGORIES = [
    {"name": "Sotuv va Marketing", "icon_name": "shopping-bag", "keywords": "sotuv, marketing, savdo, smm, menejer"},
    {"name": "IT va Dasturlash", "icon_name": "laptop", "keywords": "dasturchi, developer, frontend, backend, it, python"},
    {"name": "Haydovchi va Logistika", "icon_name": "car", "keywords": "haydovchi, yetkazib berish, logistika, kuriyer"},
    {"name": "Oshpaz va Restoran", "icon_name": "chef-hat", "keywords": "oshpaz, ofitsiant, idish yuvuvchi, barista"},
    {"name": "Ta'lim va Repetitorlik", "icon_name": "book", "keywords": "o'qituvchi, repetitor, ingliz tili, ustoz"},
    {"name": "Go'zallik va Salon", "icon_name": "scissors", "keywords": "sartarosh, vizajist, manikyur, massaj"},
    {"name": "Qurilish va Ta'mirlash", "icon_name": "brick", "keywords": "usta, quruvchi, payvandchi, suvoqchi"},
    {"name": "Moliya va Buxgalteriya", "icon_name": "coins", "keywords": "buxgalter, hisobchi, auditor, kassa"},
    {"name": "Ofis va Ma'muriyat", "icon_name": "folder", "keywords": "kotiba, administrator, operator, dispetcher"},
    {"name": "Boshqa sohalar", "icon_name": "briefcase", "keywords": "boshqa, turli, universal"},
]


async def init_db():
    """Jadvallarni yaratish va standart kategoriyalarni initsializatsiya qilish."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # SQLite uchun yangi ustunlarni xavfsiz qo'shish (migration)
        if "sqlite" in str(conn.engine.url):
            from sqlalchemy import text
            new_cols = [
                ("request_type", "VARCHAR(20) DEFAULT 'job'"),
                ("bio", "TEXT"),
                ("experience", "VARCHAR(100)"),
                ("tools", "VARCHAR(255)"),
                ("portfolio", "VARCHAR(255)"),
                ("receipt_image_path", "VARCHAR(500)"),
                ("payment_amount", "INTEGER"),
                ("payment_status", "VARCHAR(30) DEFAULT 'unpaid'"),
            ]
            for col_name, col_type in new_cols:
                try:
                    await conn.execute(text(f"ALTER TABLE job_requests ADD COLUMN {col_name} {col_type};"))
                except Exception:
                    pass  # Agar ustun allaqachon mavjud bo'lsa xatoni e'tiborsiz qoldirish

    async with get_session() as session:
        # Kategoriyalar borligini tekshirish
        stmt = select(Category)
        result = await session.execute(stmt)
        existing = result.scalars().all()

        if not existing:
            for cat_data in DEFAULT_CATEGORIES:
                cat = Category(
                    name=cat_data["name"],
                    icon_name=cat_data["icon_name"],
                    keywords=cat_data["keywords"],
                    is_active=True,
                )
                session.add(cat)

        # Bot sozlamalari (to'lov, karta, narx) borligini tekshirish
        setting_stmt = select(BotSetting)
        setting_res = await session.execute(setting_stmt)
        setting = setting_res.scalar_one_or_none()
        if not setting:
            default_setting = BotSetting(
                price_per_post=25000,
                card_number="8600 0000 0000 0000",
                card_holder="Karta Egasi",
                is_payment_enabled=True,
            )
            session.add(default_setting)

        # Superadminlarni ro'yxatdan o'tkazish/tekshirish
        for sa_id in settings.SUPERADMIN_IDS:
            user_stmt = select(User).where(User.tg_id == sa_id)
            res = await session.execute(user_stmt)
            user = res.scalar_one_or_none()
            if not user:
                new_sa = User(
                    tg_id=sa_id,
                    full_name="Super Admin",
                    role=UserRole.SUPERADMIN.value,
                )
                session.add(new_sa)
            elif user.role != UserRole.SUPERADMIN.value:
                user.role = UserRole.SUPERADMIN.value

        await session.commit()
