from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, Category, JobRequest, Channel, UserRole, JobStatus, TariffType, PaymentStatus


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
        tariff: str = TariffType.START.value,
        payment_status: str = PaymentStatus.PAID.value,
    ) -> JobRequest:
        job = JobRequest(
            user_id=user_id,
            category_id=category_id,
            position=position,
            company=company,
            requirements=requirements,
            salary=salary,
            location=location,
            work_schedule=work_schedule,
            contact=contact,
            telegram_user=telegram_user,
            post_text=post_text,
            image_path=image_path,
            status=status,
            tariff=tariff,
            payment_status=payment_status,
            created_at=datetime.utcnow(),
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def create_pending_payment(
        self,
        user_id: int,
        tariff: str,
        payment_provider: str,
        payment_receipt: str,
        price: int,
    ) -> JobRequest:
        """To'lov cheki yuborildi, admin tasdiqlashini kutish uchun skeletal job yaratish."""
        job = JobRequest(
            user_id=user_id,
            position="—",  # Keyinroq to'ldiriladi
            company="—",
            requirements="—",
            salary="—",
            contact="—",
            status=JobStatus.DRAFT.value,
            tariff=tariff,
            payment_status=PaymentStatus.WAITING_CONFIRM.value,
            payment_provider=payment_provider,
            payment_receipt=payment_receipt,
            created_at=datetime.utcnow(),
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def confirm_payment(self, job_id: int) -> Optional[JobRequest]:
        """Admin to'lovni tasdiqladi."""
        job = await self.get_by_id(job_id)
        if job:
            job.payment_status = PaymentStatus.PAID.value
            await self.session.flush()
        return job

    async def reject_payment(self, job_id: int) -> Optional[JobRequest]:
        """Admin to'lovni rad etdi."""
        job = await self.get_by_id(job_id)
        if job:
            job.payment_status = PaymentStatus.CANCELLED.value
            job.status = JobStatus.REJECTED.value
            await self.session.flush()
        return job

    async def get_paid_unfilled_job(self, user_id: int) -> Optional[JobRequest]:
        """To'langan lekin hali ma'lumot kiritilmagan jobni topish."""
        stmt = (
            select(JobRequest)
            .where(
                JobRequest.user_id == user_id,
                JobRequest.payment_status == PaymentStatus.PAID.value,
                JobRequest.status == JobStatus.DRAFT.value,
            )
            .order_by(desc(JobRequest.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_with_vacancy_data(
        self,
        job_id: int,
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
        status: str = JobStatus.PENDING.value,
        expires_at=None,
    ) -> Optional[JobRequest]:
        """To'lov tasdiqlangach ma'lumotlarni to'ldirish."""
        job = await self.get_by_id(job_id)
        if not job:
            return None
        job.category_id = category_id
        job.position = position
        job.company = company
        job.requirements = requirements
        job.salary = salary
        job.contact = contact
        job.location = location
        job.work_schedule = work_schedule
        job.telegram_user = telegram_user
        job.post_text = post_text
        job.image_path = image_path
        job.status = status
        job.expires_at = expires_at
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

    async def get_all_active(self) -> List[Channel]:
        stmt = select(Channel).where(Channel.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

