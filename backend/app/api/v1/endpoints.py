import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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
# Pydantic 模型
# ═══════════════════════════════════════════


class ApplyRequest(BaseModel):
    company_name: str
    credit_code: str
    industry: str
    scale: str
    contact_name: str
    contact_phone: str
    contact_email: str
    interested_skills: Optional[str] = ""
    requirements: Optional[str] = ""
    current_systems: Optional[str] = ""


class ReviewRequest(BaseModel):
    status: str
    reject_reason: Optional[str] = ""


class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    image_url: str = ""
    button_text: str = "了解更多"
    button_link: str = "#trial"
    sort_order: int = 0
    is_active: bool = True


class SkillCreate(BaseModel):
    key: str
    name: str
    icon: Optional[str] = ""
    summary: str
    description: Optional[str] = ""
    scenarios: Optional[str] = ""
    capabilities: Optional[str] = ""
    platforms: Optional[str] = ""
    sort_order: int = 0
    is_active: bool = True


class PolicyCreate(BaseModel):
    dept: str
    doc_number: Optional[str] = ""
    title: str
    description: Optional[str] = ""
    sort_order: int = 0
    is_active: bool = True


class ContactCreate(BaseModel):
    type: str
    label: str
    value: str
    display_order: int = 0


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
    stmt = select(Skill).where(Skill.is_active == True).order_by(Skill.sort_order.desc())
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


@router.post("/apply")
async def create_application(
    req: ApplyRequest,
    db: AsyncSession = Depends(get_db),
):
    app = EnterpriseApplication(
        company_name=req.company_name,
        credit_code=req.credit_code,
        industry=req.industry,
        scale=req.scale,
        contact_name=req.contact_name,
        contact_phone=req.contact_phone,
        contact_email=req.contact_email,
        interested_skills=req.interested_skills,
        requirements=req.requirements,
        current_systems=req.current_systems,
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

# ── 入驻审核 ──


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
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(EnterpriseApplication).where(EnterpriseApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="申请不存在")
    app.status = req.status
    app.reject_reason = req.reject_reason
    await db.commit()
    await db.refresh(app)
    return app


# ── Banner CRUD ──


@router.get("/admin/banners")
async def admin_get_banners(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    stmt = select(Banner).order_by(Banner.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/admin/banners")
async def admin_create_banner(
    req: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    banner = Banner(**req.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


@router.put("/admin/banners/{banner_id}")
async def admin_update_banner(
    banner_id: int,
    req: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner 不存在")
    for k, v in req.model_dump().items():
        setattr(banner, k, v)
    await db.commit()
    await db.refresh(banner)
    return banner


@router.delete("/admin/banners/{banner_id}")
async def admin_delete_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner 不存在")
    await db.delete(banner)
    await db.commit()
    return {"ok": True}


# ── Skill CRUD ──


@router.get("/admin/skills")
async def admin_get_skills(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    stmt = select(Skill).order_by(Skill.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/admin/skills")
async def admin_create_skill(
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    skill = Skill(**req.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.put("/admin/skills/{skill_id}")
async def admin_update_skill(
    skill_id: int,
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")
    for k, v in req.model_dump().items():
        setattr(skill, k, v)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/admin/skills/{skill_id}")
async def admin_delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")
    await db.delete(skill)
    await db.commit()
    return {"ok": True}


# ── Policy CRUD ──


@router.get("/admin/policies")
async def admin_get_policies(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    stmt = select(Policy).order_by(Policy.sort_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/admin/policies")
async def admin_create_policy(
    req: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    policy = Policy(**req.model_dump())
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return policy


@router.put("/admin/policies/{policy_id}")
async def admin_update_policy(
    policy_id: int,
    req: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="政策不存在")
    for k, v in req.model_dump().items():
        setattr(policy, k, v)
    await db.commit()
    await db.refresh(policy)
    return policy


@router.delete("/admin/policies/{policy_id}")
async def admin_delete_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="政策不存在")
    await db.delete(policy)
    await db.commit()
    return {"ok": True}


# ── Contact CRUD ──


@router.get("/admin/contacts")
async def admin_get_contacts(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    stmt = select(ContactInfo).order_by(ContactInfo.display_order)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/admin/contacts")
async def admin_create_contact(
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    contact = ContactInfo(**req.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.put("/admin/contacts/{contact_id}")
async def admin_update_contact(
    contact_id: int,
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(ContactInfo).where(ContactInfo.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="联系方式不存在")
    for k, v in req.model_dump().items():
        setattr(contact, k, v)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/admin/contacts/{contact_id}")
async def admin_delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    result = await db.execute(select(ContactInfo).where(ContactInfo.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="联系方式不存在")
    await db.delete(contact)
    await db.commit()
    return {"ok": True}
