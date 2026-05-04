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
