from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.cms import Banner, Skill, Policy, ContactInfo, EnterpriseApplication

router = APIRouter()

# ---------- 公开路由 ----------

@router.get("/cms/banners")
async def get_banners(db: AsyncSession = Depends(get_db)):
    stmt = select(Banner).where(Banner.is_active == True).order_by(Banner.sort_order)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items

@router.get("/cms/skills")
async def get_skills(db: AsyncSession = Depends(get_db)):
    stmt = select(Skill).where(Skill.is_active == True).order_by(Skill.sort_order)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items

@router.get("/cms/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    stmt = select(Policy).where(Policy.is_active == True).order_by(Policy.sort_order)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items

@router.get("/cms/contact")
async def get_contact(db: AsyncSession = Depends(get_db)):
    stmt = select(ContactInfo).order_by(ContactInfo.display_order)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items

# ---------- 入驻申请 ----------

@router.post("/apply")
async def apply_enterprise(
    company_name: str,
    credit_code: str,
    industry: str,
    scale: str,
    contact_name: str,
    contact_phone: str,
    contact_email: str,
    interested_skills: str,
    requirements: str,
    current_systems: str,
    db: AsyncSession = Depends(get_db),
):
    tracking_code = secrets.token_hex(16)  # 32 位十六进制
    application = EnterpriseApplication(
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
        tracking_code=tracking_code,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return {"tracking_code": application.tracking_code}

# ---------- 管理路由 ----------

@router.get("/admin/applications")
async def list_applications(
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    stmt = select(EnterpriseApplication)
    if status_filter:
        stmt = stmt.where(EnterpriseApplication.status == status_filter)
    stmt = stmt.order_by(desc(EnterpriseApplication.created_at))
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items

@router.put("/admin/applications/{application_id}")
async def update_application(
    application_id: int,
    status: str,
    reject_reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    stmt = select(EnterpriseApplication).where(EnterpriseApplication.id == application_id)
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Application not found")
    application.status = status
    if reject_reason is not None:
        application.reject_reason = reject_reason
    await db.commit()
    await db.refresh(application)
    return application
