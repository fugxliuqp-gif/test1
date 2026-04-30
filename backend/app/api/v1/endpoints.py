import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.cms import (
    Banner,
    Skill,
    Policy,
    ContactInfo,
    EnterpriseApplication,
)

router = APIRouter()


# ═══════════════════════════════════════════
# 公开路由 (无需认证)
# ═══════════════════════════════════════════


@router.get("/cms/banners")
async def get_banners(db: AsyncSession = Depends(get_db)):
    stmt = select(Banner).where(Banner.is_active == True).order_by(Banner.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/cms/skills")
async def get_skills(db: AsyncSession = Depends(get_db)):
    stmt = select(Skill).where(Skill.is_active == True).order_by(Skill.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/cms/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    stmt = select(Policy).where(Policy.is_active == True).order_by(Policy.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/cms/contact")
async def get_contact(db: AsyncSession = Depends(get_db)):
    stmt = select(ContactInfo).order_by(ContactInfo.display_order)
    result = await db.execute(stmt)
    return result.scalars().all()


# ═══════════════════════════════════════════
# 入驻申请 (公开)
# ═══════════════════════════════════════════


class ApplyCreate:
    pass


@router.post("/apply")
async def create_application(
    company_name: str,
    credit_code: str,
    industry: str,
    scale: str,
    contact_name: str,
    contact_phone: str,
    contact_email: str,
    interested_skills: Optional[str] = "",
    requirements: Optional[str] = "",
    current_systems: Optional[str] = "",
    db: AsyncSession = Depends(get_db),
):
    app = EnterpriseApplication(
        company_name=company_name,
        credit_code=credit_code,
        industry=industry,
        scale=scale,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        interested_skills=interested_skills,
        requirements=requirements,
        current_systems=current_systems,
        status="pending",
        tracking_code=secrets.token_hex(16),
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return {"tracking_code": app.tracking_code}


# ═══════════════════════════════════════════
# 管理路由 (需认证)
# ═══════════════════════════════════════════


@router.get("/admin/applications")
async def get_applications(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    stmt = select(EnterpriseApplication).order_by(EnterpriseApplication.created_at.desc())
    if status:
        stmt = stmt.where(EnterpriseApplication.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/admin/applications/{app_id}")
async def review_application(
    app_id: int,
    status: str,
    reject_reason: Optional[str] = "",
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(EnterpriseApplication).where(EnterpriseApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="申请不存在")
    app.status = status
    app.reject_reason = reject_reason
    await db.commit()
    await db.refresh(app)
    return app
