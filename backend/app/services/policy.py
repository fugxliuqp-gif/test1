from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import Policy
from app.schemas.policy import PolicyCreate


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active(self) -> list[Policy]:
        result = await self.db.execute(
            select(Policy).where(Policy.is_active == True).order_by(Policy.sort_order)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Policy]:
        result = await self.db.execute(
            select(Policy).order_by(Policy.sort_order)
        )
        return list(result.scalars().all())

    async def get_by_id(self, policy_id: int) -> Policy | None:
        result = await self.db.execute(select(Policy).where(Policy.id == policy_id))
        return result.scalar_one_or_none()

    async def create(self, req: PolicyCreate) -> Policy:
        policy = Policy(**req.model_dump())
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def update(self, policy_id: int, req: PolicyCreate) -> Policy:
        policy = await self.get_by_id(policy_id)
        if not policy:
            raise ValueError("政策不存在")
        for k, v in req.model_dump().items():
            setattr(policy, k, v)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def delete(self, policy_id: int) -> None:
        policy = await self.get_by_id(policy_id)
        if not policy:
            raise ValueError("政策不存在")
        await self.db.delete(policy)
        await self.db.commit()
