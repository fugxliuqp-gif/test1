from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), default="")
    image_url: Mapped[str] = mapped_column(String(500))
    button_text: Mapped[str] = mapped_column(String(50), default="了解更多")
    button_link: Mapped[str] = mapped_column(String(200), default="#trial")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    icon: Mapped[Optional[str]] = mapped_column(String(50), default="")
    summary: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    scenarios: Mapped[Optional[str]] = mapped_column(Text, default="")  # JSON array
    capabilities: Mapped[Optional[str]] = mapped_column(Text, default="")  # JSON array
    platforms: Mapped[Optional[str]] = mapped_column(Text, default="")  # JSON array
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    dept: Mapped[str] = mapped_column(String(200))
    doc_number: Mapped[Optional[str]] = mapped_column(String(200), default="")
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # manager|email|address|wechat_qr|phone
    label: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(String(500))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class EnterpriseApplication(Base):
    __tablename__ = "enterprise_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200))
    credit_code: Mapped[str] = mapped_column(String(50))
    industry: Mapped[str] = mapped_column(String(50))
    scale: Mapped[str] = mapped_column(String(50))
    contact_name: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(20))
    contact_email: Mapped[str] = mapped_column(String(200))
    interested_skills: Mapped[Optional[str]] = mapped_column(Text, default="")
    requirements: Mapped[Optional[str]] = mapped_column(Text, default="")
    current_systems: Mapped[Optional[str]] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|approved|rejected
    reject_reason: Mapped[Optional[str]] = mapped_column(String(500), default="")
    tracking_code: Mapped[str] = mapped_column(String(32), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
