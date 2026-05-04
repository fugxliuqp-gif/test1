from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.response import success
from app.schemas.banner import BannerCreate
from app.schemas.skill import SkillCreate
from app.schemas.policy import PolicyCreate
from app.schemas.contact import ContactCreate
from app.schemas.application import ApplyRequest, ReviewRequest
from app.services.banner import BannerService
from app.services.skill import SkillService
from app.services.policy import PolicyService
from app.services.contact import ContactService
from app.services.application import ApplicationService

router = APIRouter()


def handle_not_found(exc: ValueError):
    raise HTTPException(status_code=404, detail=str(exc))


# ═══════════════════════════════════════════
# 公开路由 (无需认证)
# ═══════════════════════════════════════════


@router.get("/cms/banners", tags=["CMS"], summary="获取启用的 Banner 列表")
async def get_banners(db: AsyncSession = Depends(get_db)):
    data = await BannerService(db).get_active()
    return success(data=data)


@router.get("/cms/skills", tags=["CMS"], summary="获取启用的 Skill 列表")
async def get_skills(db: AsyncSession = Depends(get_db)):
    data = await SkillService(db).get_active()
    return success(data=data)


@router.get("/cms/policies", tags=["CMS"], summary="获取启用的政策列表")
async def get_policies(db: AsyncSession = Depends(get_db)):
    data = await PolicyService(db).get_active()
    return success(data=data)


@router.get("/cms/contact", tags=["CMS"], summary="获取联系方式列表")
async def get_contact(db: AsyncSession = Depends(get_db)):
    data = await ContactService(db).get_all()
    return success(data=data)


# ═══════════════════════════════════════════
# 入驻申请 (公开)
# ═══════════════════════════════════════════


@router.post("/apply", tags=["Application"], summary="提交入驻申请")
async def create_application(req: ApplyRequest, db: AsyncSession = Depends(get_db)):
    app = await ApplicationService(db).create(req)
    return success(data={"tracking_code": app.tracking_code}, message="提交成功")


# ═══════════════════════════════════════════
# 管理路由 (需认证)
# ═══════════════════════════════════════════

# ── 入驻审核 ──


@router.get("/admin/applications", tags=["Application"], summary="获取入驻申请列表（需认证）")
async def get_applications(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await ApplicationService(db).get_all(status=status)
    return success(data=data)


@router.put("/admin/applications/{app_id}", tags=["Application"], summary="审核入驻申请（需认证）")
async def review_application(
    app_id: int,
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        app = await ApplicationService(db).review(app_id, req)
        return success(data=app, message="更新成功")
    except ValueError as e:
        handle_not_found(e)


# ── Banner CRUD ──


@router.get("/admin/banners", tags=["Banner"], summary="获取所有 Banner（需认证）")
async def admin_get_banners(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await BannerService(db).get_all()
    return success(data=data)


@router.post("/admin/banners", tags=["Banner"], summary="创建 Banner（需认证）")
async def admin_create_banner(
    req: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    banner = await BannerService(db).create(req)
    return success(data=banner, message="创建成功")


@router.put("/admin/banners/{banner_id}", tags=["Banner"], summary="更新 Banner（需认证）")
async def admin_update_banner(
    banner_id: int,
    req: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        banner = await BannerService(db).update(banner_id, req)
        return success(data=banner, message="更新成功")
    except ValueError as e:
        handle_not_found(e)


@router.delete("/admin/banners/{banner_id}", tags=["Banner"], summary="删除 Banner（需认证）")
async def admin_delete_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        await BannerService(db).delete(banner_id)
        return success(message="删除成功")
    except ValueError as e:
        handle_not_found(e)


# ── Skill CRUD ──


@router.get("/admin/skills", tags=["Skill"], summary="获取所有 Skill（需认证）")
async def admin_get_skills(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await SkillService(db).get_all()
    return success(data=data)


@router.post("/admin/skills", tags=["Skill"], summary="创建 Skill（需认证）")
async def admin_create_skill(
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    skill = await SkillService(db).create(req)
    return success(data=skill, message="创建成功")


@router.put("/admin/skills/{skill_id}", tags=["Skill"], summary="更新 Skill（需认证）")
async def admin_update_skill(
    skill_id: int,
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        skill = await SkillService(db).update(skill_id, req)
        return success(data=skill, message="更新成功")
    except ValueError as e:
        handle_not_found(e)


@router.delete("/admin/skills/{skill_id}", tags=["Skill"], summary="删除 Skill（需认证）")
async def admin_delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        await SkillService(db).delete(skill_id)
        return success(message="删除成功")
    except ValueError as e:
        handle_not_found(e)


# ── Policy CRUD ──


@router.get("/admin/policies", tags=["Policy"], summary="获取所有政策（需认证）")
async def admin_get_policies(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await PolicyService(db).get_all()
    return success(data=data)


@router.post("/admin/policies", tags=["Policy"], summary="创建政策（需认证）")
async def admin_create_policy(
    req: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    policy = await PolicyService(db).create(req)
    return success(data=policy, message="创建成功")


@router.put("/admin/policies/{policy_id}", tags=["Policy"], summary="更新政策（需认证）")
async def admin_update_policy(
    policy_id: int,
    req: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        policy = await PolicyService(db).update(policy_id, req)
        return success(data=policy, message="更新成功")
    except ValueError as e:
        handle_not_found(e)


@router.delete("/admin/policies/{policy_id}", tags=["Policy"], summary="删除政策（需认证）")
async def admin_delete_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        await PolicyService(db).delete(policy_id)
        return success(message="删除成功")
    except ValueError as e:
        handle_not_found(e)


# ── Contact CRUD ──


@router.get("/admin/contacts", tags=["Contact"], summary="获取所有联系方式（需认证）")
async def admin_get_contacts(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await ContactService(db).get_all()
    return success(data=data)


@router.post("/admin/contacts", tags=["Contact"], summary="创建联系方式（需认证）")
async def admin_create_contact(
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    contact = await ContactService(db).create(req)
    return success(data=contact, message="创建成功")


@router.put("/admin/contacts/{contact_id}", tags=["Contact"], summary="更新联系方式（需认证）")
async def admin_update_contact(
    contact_id: int,
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        contact = await ContactService(db).update(contact_id, req)
        return success(data=contact, message="更新成功")
    except ValueError as e:
        handle_not_found(e)


@router.delete("/admin/contacts/{contact_id}", tags=["Contact"], summary="删除联系方式（需认证）")
async def admin_delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    try:
        await ContactService(db).delete(contact_id)
        return success(message="删除成功")
    except ValueError as e:
        handle_not_found(e)
