# Phase D: Service 层抽离实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use `- [ ]` syntax.

**Goal:** 将业务逻辑从 `endpoints.py` 抽离到 `services/`，Pydantic schema 抽离到 `schemas/`，使 API 层只做路由和入参校验

**Architecture:**
```
backend/app/
  schemas/           ← Pydantic 请求/响应模型 (从 endpoints.py 拆出)
    banner.py
    skill.py
    policy.py
    contact.py
    application.py
  services/          ← 业务逻辑层
    banner.py        ← BannerService
    skill.py         ← SkillService
    policy.py        ← PolicyService
    contact.py       ← ContactService
    application.py   ← ApplicationService
  api/v1/
    endpoints.py     ← 精简为只调用 service + 路由装饰
```

**Pattern:** 每个 Service 是一个 class，提供 `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()` 方法，接受 `db: AsyncSession` 参数。

---

### Task D1: Schema 抽离

**Files:**
- Create: `backend/app/schemas/` package
- Modify: `backend/app/api/v1/endpoints.py` (移除 Pydantic 模型，改为从 schemas 导入)

- [ ] **Step 1: 创建 `app/schemas/__init__.py`** — 空文件

- [ ] **Step 2~5: 创建每个实体的 schema 文件**

```python
# app/schemas/banner.py
from typing import Optional
from pydantic import BaseModel


class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    image_url: str = ""
    button_text: str = "了解更多"
    button_link: str = "#trial"
    sort_order: int = 0
    is_active: bool = True
```

```python
# app/schemas/skill.py
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
```

```python
# app/schemas/policy.py
class PolicyCreate(BaseModel):
    dept: str
    doc_number: Optional[str] = ""
    title: str
    description: Optional[str] = ""
    sort_order: int = 0
    is_active: bool = True
```

```python
# app/schemas/contact.py
class ContactCreate(BaseModel):
    type: str
    label: str
    value: str
    display_order: int = 0
```

```python
# app/schemas/application.py
from typing import Optional
from pydantic import BaseModel


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
```

- [ ] **验证导入:**
```bash
cd backend && python3 -c "
from app.schemas.banner import BannerCreate
from app.schemas.skill import SkillCreate
from app.schemas.policy import PolicyCreate
from app.schemas.contact import ContactCreate
from app.schemas.application import ApplyRequest, ReviewRequest
print('OK')
"
```

Expected: `OK`

- [ ] **提交:**
```bash
git add backend/app/schemas/
git commit -m "refactor: extract Pydantic schemas into app/schemas/"
```

---

### Task D2: Service 层

**Files:**
- Create: `backend/app/services/` package
- Create: 5 个 service 文件

- [ ] **Step 1: 创建 `app/services/__init__.py`** — 空文件

- [ ] **Step 2: 创建 `app/services/banner.py`**

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import Banner
from app.schemas.banner import BannerCreate


class BannerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active(self) -> list[Banner]:
        stmt = select(Banner).where(Banner.is_active == True).order_by(Banner.sort_order)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self) -> list[Banner]:
        stmt = select(Banner).order_by(Banner.sort_order)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, banner_id: int) -> Banner | None:
        result = await self.db.execute(select(Banner).where(Banner.id == banner_id))
        return result.scalar_one_or_none()

    async def create(self, req: BannerCreate) -> Banner:
        banner = Banner(**req.model_dump())
        self.db.add(banner)
        await self.db.commit()
        await self.db.refresh(banner)
        return banner

    async def update(self, banner_id: int, req: BannerCreate) -> Banner:
        banner = await self.get_by_id(banner_id)
        if not banner:
            raise ValueError("Banner 不存在")
        for k, v in req.model_dump().items():
            setattr(banner, k, v)
        await self.db.commit()
        await self.db.refresh(banner)
        return banner

    async def delete(self, banner_id: int) -> None:
        banner = await self.get_by_id(banner_id)
        if not banner:
            raise ValueError("Banner 不存在")
        await self.db.delete(banner)
        await self.db.commit()
```

- [ ] **Step 3: 创建 `app/services/skill.py`** — 同理 (SkillService, 用 SkillCreate)

- [ ] **Step 4: 创建 `app/services/policy.py`** — 同理 (PolicyService, 用 PolicyCreate)

- [ ] **Step 5: 创建 `app/services/contact.py`** — 同理 (ContactService, 用 ContactCreate)

- [ ] **Step 6: 创建 `app/services/application.py`**

```python
import secrets
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import EnterpriseApplication
from app.schemas.application import ApplyRequest, ReviewRequest


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, req: ApplyRequest) -> EnterpriseApplication:
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
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def get_all(self, status: Optional[str] = None) -> list[EnterpriseApplication]:
        stmt = select(EnterpriseApplication).order_by(EnterpriseApplication.created_at.desc())
        if status:
            stmt = stmt.where(EnterpriseApplication.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, app_id: int) -> EnterpriseApplication | None:
        result = await self.db.execute(select(EnterpriseApplication).where(EnterpriseApplication.id == app_id))
        return result.scalar_one_or_none()

    async def review(self, app_id: int, req: ReviewRequest) -> EnterpriseApplication:
        app = await self.get_by_id(app_id)
        if not app:
            raise ValueError("申请不存在")
        app.status = req.status
        app.reject_reason = req.reject_reason
        await self.db.commit()
        await self.db.refresh(app)
        return app
```

注意：Service 层用 `ValueError` 表示"未找到"，由 endpoints 层捕获并转为 `HTTPException(404)`。

- [ ] **验证导入:**
```bash
cd backend && python3 -c "
from app.services.banner import BannerService
from app.services.skill import SkillService
from app.services.policy import PolicyService
from app.services.contact import ContactService
from app.services.application import ApplicationService
print('OK')
"
```

Expected: `OK`

- [ ] **提交:**
```bash
git add backend/app/services/
git commit -m "refactor: add service layer with CRUD for all entities"
```

---

### Task D3: 精简 endpoints.py

**Files:**
- Modify: `backend/app/api/v1/endpoints.py`

将 `endpoints.py` 从 420 行缩减为路由层（仅调用 service）：

```python
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


# ── 公开路由 ──


@router.get("/cms/banners")
async def get_banners(db: AsyncSession = Depends(get_db)):
    data = await BannerService(db).get_active()
    return success(data=data)


@router.get("/cms/skills")
async def get_skills(db: AsyncSession = Depends(get_db)):
    data = await SkillService(db).get_active()
    return success(data=data)


@router.get("/cms/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    data = await PolicyService(db).get_active()
    return success(data=data)


@router.get("/cms/contact")
async def get_contact(db: AsyncSession = Depends(get_db)):
    data = await ContactService(db).get_all()
    return success(data=data)


# ── 入驻申请 ──


@router.post("/apply")
async def create_application(req: ApplyRequest, db: AsyncSession = Depends(get_db)):
    app = await ApplicationService(db).create(req)
    return success(data={"tracking_code": app.tracking_code}, message="提交成功")


# ── 管理路由 ──


def handle_not_found(exc: ValueError):
    raise HTTPException(status_code=404, detail=str(exc))


@router.get("/admin/applications")
async def get_applications(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await ApplicationService(db).get_all(status=status)
    return success(data=data)


@router.put("/admin/applications/{app_id}")
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


# Banner CRUD


@router.get("/admin/banners")
async def admin_get_banners(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await BannerService(db).get_all()
    return success(data=data)


@router.post("/admin/banners")
async def admin_create_banner(
    req: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    banner = await BannerService(db).create(req)
    return success(data=banner, message="创建成功")


@router.put("/admin/banners/{banner_id}")
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


@router.delete("/admin/banners/{banner_id}")
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


# Skill CRUD (同理)


@router.get("/admin/skills")
async def admin_get_skills(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await SkillService(db).get_all()
    return success(data=data)


@router.post("/admin/skills")
async def admin_create_skill(
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    skill = await SkillService(db).create(req)
    return success(data=skill, message="创建成功")


@router.put("/admin/skills/{skill_id}")
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


@router.delete("/admin/skills/{skill_id}")
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


# Policy CRUD (同理)


@router.get("/admin/policies")
async def admin_get_policies(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await PolicyService(db).get_all()
    return success(data=data)


@router.post("/admin/policies")
async def admin_create_policy(
    req: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    policy = await PolicyService(db).create(req)
    return success(data=policy, message="创建成功")


@router.put("/admin/policies/{policy_id}")
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


@router.delete("/admin/policies/{policy_id}")
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


# Contact CRUD (同理)


@router.get("/admin/contacts")
async def admin_get_contacts(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    data = await ContactService(db).get_all()
    return success(data=data)


@router.post("/admin/contacts")
async def admin_create_contact(
    req: ContactCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    contact = await ContactService(db).create(req)
    return success(data=contact, message="创建成功")


@router.put("/admin/contacts/{contact_id}")
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


@router.delete("/admin/contacts/{contact_id}")
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
```

- [ ] **验证导入:**
```bash
cd backend && python3 -c "from app.api.v1.endpoints import router; print('OK')"
```

Expected: `OK`

- [ ] **提交:**
```bash
git add backend/app/api/v1/endpoints.py
git commit -m "refactor: simplify endpoints.py to thin routing layer"
```

---

### Task D4: 运行测试验证

- [ ] **运行全部测试:**
```bash
cd backend && PYTHONPATH=. python3 -m pytest tests/ -v
```

Expected: 6 tests PASS

- [ ] **如果有测试依赖 endpoints.py 内部细节，更新测试**
  预期不需要改动测试，因为 service 层保持了相同的异常行为和返回值。

---

### 验证清单

- [ ] `endpoints.py` 从 420 行缩减到 ~180 行（仅路由 + 参数校验）
- [ ] 所有 Pydantic schema 在 `app/schemas/` 下
- [ ] 所有业务逻辑在 `app/services/` 下
- [ ] Service 层用 `ValueError` 表示未找到资源
- [ ] `endpoints.py` 捕获 `ValueError` 转为 `HTTPException(404)`
- [ ] 6 tests PASS
