from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, Category, JobRequest, Channel, UserRole, JobStatus, BotSetting


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, tg_id: int, full_name: str, username: Optional[str] = None) -> Tuple[User, bool]:
        user = await self.get_by_tg_id(tg_id)
        created = False
        if not user:
            user = User(
                tg_id=tg_id,
                full_name=full_name,
                username=username,
                role=UserRole.USER.value,
            )
            self.session.add(user)
            await self.session.flush()
            created = True
        else:
            # Yangilash agar username yoki ism o'zgargan bo'lsa
            updated = False
            if user.full_name != full_name:
                user.full_name = full_name
                updated = True
            if user.username != username:
                user.username = username
                updated = True
            if updated:
                await self.session.flush()
        return user, created

    async def set_role(self, tg_id: int, role: str) -> Optional[User]:
        user = await self.get_by_tg_id(tg_id)
        if user:
            user.role = role
            await self.session.flush()
        return user

    async def get_all_admins(self) -> List[User]:
        stmt = select(User).where(User.role.in_([UserRole.ADMIN.value, UserRole.SUPERADMIN.value]))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> List[Category]:
        stmt = select(Category).where(Category.is_active == True).order_by(Category.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, name: str, icon_name: str = "briefcase", keywords: Optional[str] = None) -> Category:
        category = Category(name=name, icon_name=icon_name, keywords=keywords, is_active=True)
        self.session.add(category)
        await self.session.flush()
        return category


class JobRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        category_id: Optional[int],
        position: str,
        company: str,
        requirements: str,
        salary: str,
        contact: str,
        location: Optional[str] = None,
        work_schedule: Optional[str] = None,
        telegram_user: Optional[str] = None,
        post_text: Optional[str] = None,
        image_path: Optional[str] = None,
        status: str = JobStatus.DRAFT.value,
        request_type: str = "job",
        bio: Optional[str] = None,
        experience: Optional[str] = None,
        tools: Optional[str] = None,
        portfolio: Optional[str] = None,
        receipt_image_path: Optional[str] = None,
        payment_amount: Optional[int] = None,
        payment_status: str = "unpaid",
    ) -> JobRequest:
        job = JobRequest(
            user_id=user_id,
            category_id=category_id,
            request_type=request_type,
            position=position,
            company=company,
            requirements=requirements,
            salary=salary,
            location=location,
            work_schedule=work_schedule,
            contact=contact,
            telegram_user=telegram_user,
            bio=bio,
            experience=experience,
            tools=tools,
            portfolio=portfolio,
            post_text=post_text,
            image_path=image_path,
            receipt_image_path=receipt_image_path,
            payment_amount=payment_amount,
            payment_status=payment_status,
            status=status,
            created_at=datetime.utcnow(),
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def update_payment(
        self,
        job_id: int,
        receipt_image_path: Optional[str] = None,
        payment_status: Optional[str] = None,
        payment_amount: Optional[int] = None,
    ) -> Optional[JobRequest]:
        job = await self.get_by_id(job_id)
        if not job:
            return None
        if receipt_image_path is not None:
            job.receipt_image_path = receipt_image_path
        if payment_status is not None:
            job.payment_status = payment_status
        if payment_amount is not None:
            job.payment_amount = payment_amount
        await self.session.flush()
        return job

    async def get_by_id(self, job_id: int) -> Optional[JobRequest]:
        stmt = select(JobRequest).where(JobRequest.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_jobs(self, user_id: int, limit: int = 10) -> List[JobRequest]:
        stmt = (
            select(JobRequest)
            .where(JobRequest.user_id == user_id)
            .order_by(desc(JobRequest.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_jobs(self, limit: int = 20) -> List[JobRequest]:
        stmt = (
            select(JobRequest)
            .where(JobRequest.status == JobStatus.PENDING.value)
            .order_by(JobRequest.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        job_id: int,
        status: str,
        reviewer_id: Optional[int] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[JobRequest]:
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.status = status
        now = datetime.utcnow()
        if reviewer_id:
            job.reviewed_by = reviewer_id
            job.reviewed_at = now

        if rejection_reason is not None:
            job.rejection_reason = rejection_reason

        if status == JobStatus.POSTED.value:
            job.posted_at = now

        await self.session.flush()
        return job

    async def update_post_data(
        self,
        job_id: int,
        post_text: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> Optional[JobRequest]:
        job = await self.get_by_id(job_id)
        if not job:
            return None
        if post_text is not None:
            job.post_text = post_text
        if image_path is not None:
            job.image_path = image_path
        await self.session.flush()
        return job

    async def get_statistics(self) -> dict:
        total = await self.session.scalar(select(func.count(JobRequest.id)))
        pending = await self.session.scalar(
            select(func.count(JobRequest.id)).where(JobRequest.status == JobStatus.PENDING.value)
        )
        approved = await self.session.scalar(
            select(func.count(JobRequest.id)).where(JobRequest.status.in_([JobStatus.APPROVED.value, JobStatus.POSTED.value]))
        )
        rejected = await self.session.scalar(
            select(func.count(JobRequest.id)).where(JobRequest.status == JobStatus.REJECTED.value)
        )
        users_count = await self.session.scalar(select(func.count(User.id)))

        return {
            "total_jobs": total or 0,
            "pending_jobs": pending or 0,
            "approved_jobs": approved or 0,
            "rejected_jobs": rejected or 0,
            "total_users": users_count or 0,
        }


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_channel(
        self, tg_channel_id: str, channel_title: Optional[str] = None, channel_username: Optional[str] = None, added_by: Optional[int] = None
    ) -> Channel:
        stmt = select(Channel).where(Channel.tg_channel_id == tg_channel_id)
        res = await self.session.execute(stmt)
        channel = res.scalar_one_or_none()
        if not channel:
            channel = Channel(
                tg_channel_id=tg_channel_id,
                channel_title=channel_title,
                channel_username=channel_username,
                added_by=added_by,
                is_active=True,
            )
            self.session.add(channel)
        else:
            channel.is_active = True
            if channel_title:
                channel.channel_title = channel_title
            if channel_username:
                channel.channel_username = channel_username
        await self.session.flush()
        return channel

    async def remove_channel(self, channel_id: int) -> bool:
        stmt = select(Channel).where(Channel.id == channel_id)
        res = await self.session.execute(stmt)
        channel = res.scalar_one_or_none()
        if channel:
            channel.is_active = False
            await self.session.flush()
            return True
        return False

    async def get_all_active(self) -> List[Channel]:
        stmt = select(Channel).where(Channel.is_active == True).order_by(desc(Channel.id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> BotSetting:
        stmt = select(BotSetting).limit(1)
        res = await self.session.execute(stmt)
        setting = res.scalar_one_or_none()
        if not setting:
            setting = BotSetting(
                price_per_post=25000,
                card_number="8600 0000 0000 0000",
                card_holder="Karta Egasi",
                is_payment_enabled=True,
            )
            self.session.add(setting)
            await self.session.flush()
        return setting

    async def update_price(self, price: int) -> BotSetting:
        setting = await self.get_settings()
        setting.price_per_post = price
        setting.updated_at = datetime.utcnow()
        await self.session.flush()
        return setting

    async def update_card_number(self, card_number: str) -> BotSetting:
        setting = await self.get_settings()
        setting.card_number = card_number
        setting.updated_at = datetime.utcnow()
        await self.session.flush()
        return setting

    async def update_card_holder(self, card_holder: str) -> BotSetting:
        setting = await self.get_settings()
        setting.card_holder = card_holder
        setting.updated_at = datetime.utcnow()
        await self.session.flush()
        return setting

    async def toggle_payment_enabled(self) -> BotSetting:
        setting = await self.get_settings()
        setting.is_payment_enabled = not setting.is_payment_enabled
        setting.updated_at = datetime.utcnow()
        await self.session.flush()
        return setting
