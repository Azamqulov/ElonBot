from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from src.database.connection import get_session
from src.database.repositories import (
    UserRepository,
    CategoryRepository,
    JobRequestRepository,
    ChannelRepository,
)


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with get_session() as session:
            user_repo = UserRepository(session)
            cat_repo = CategoryRepository(session)
            job_repo = JobRequestRepository(session)
            chan_repo = ChannelRepository(session)

            data["session"] = session
            data["user_repo"] = user_repo
            data["cat_repo"] = cat_repo
            data["job_repo"] = job_repo
            data["chan_repo"] = chan_repo

            # Foydalanuvchini bazadan olish yoki ro'yxatdan o'tkazish
            event_user: TgUser = data.get("event_from_user")
            if event_user:
                db_user, created = await user_repo.get_or_create(
                    tg_id=event_user.id,
                    full_name=event_user.full_name,
                    username=event_user.username,
                )
                from src.bot.config import settings
                if event_user.id in settings.SUPERADMIN_IDS and db_user.role != "superadmin":
                    db_user.role = "superadmin"
                    await session.flush()
                data["db_user"] = db_user

            return await handler(event, data)
