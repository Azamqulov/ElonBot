from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class JobStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job_requests: Mapped[List["JobRequest"]] = relationship(
        "JobRequest", back_populates="user", foreign_keys="JobRequest.user_id"
    )

    def is_admin(self) -> bool:
        return self.role in (UserRole.ADMIN.value, UserRole.SUPERADMIN.value)

    def is_superadmin(self) -> bool:
        return self.role == UserRole.SUPERADMIN.value


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    icon_name: Mapped[str] = mapped_column(String(50), default="briefcase", nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    jobs: Mapped[List["JobRequest"]] = relationship("JobRequest", back_populates="category")


class JobRequest(Base):
    __tablename__ = "job_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    request_type: Mapped[str] = mapped_column(String(20), default="job", nullable=False, index=True) # "job" yoki "resume"
    position: Mapped[str] = mapped_column(String(255), nullable=False) # Lavozim yoki Mutaxassislik
    company: Mapped[str] = mapped_column(String(255), nullable=False)  # Kompaniya yoki Ism/Sharif
    requirements: Mapped[str] = mapped_column(Text, nullable=False)    # Talablar yoki Xizmatlar
    salary: Mapped[str] = mapped_column(String(100), nullable=False)   # Maosh yoki Xizmat narxi
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    work_schedule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_user: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Rezyume / Frilanser uchun qo'shimcha maydonlar
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)             # Qisqa ta'rif / shior
    experience: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Ish tajribasi
    tools: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)     # Dasturlar / Texnologiyalar
    portfolio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # Portfolio havolasi

    post_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # To'lov ma'lumotlari
    receipt_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    payment_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    payment_status: Mapped[str] = mapped_column(String(30), default="unpaid", nullable=False) # unpaid, pending_verification, paid, rejected, free

    status: Mapped[str] = mapped_column(String(20), default=JobStatus.DRAFT.value, nullable=False, index=True)
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="job_requests")
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="jobs")


class BotSetting(Base):
    __tablename__ = "bot_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    price_per_post: Mapped[int] = mapped_column(Integer, default=25000, nullable=False)
    card_number: Mapped[str] = mapped_column(String(50), default="8600 0000 0000 0000", nullable=False)
    card_holder: Mapped[str] = mapped_column(String(100), default="Karta Egasi", nullable=False)
    is_payment_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_channel_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    channel_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    channel_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    added_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
