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

    position: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    salary: Mapped[str] = mapped_column(String(100), nullable=False)  # Masalan "Kelishiladi" yoki "10 000 000 UZS"
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    work_schedule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_user: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    post_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_channel_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    channel_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    channel_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    added_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
