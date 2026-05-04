from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import Skill
from app.schemas.skill import SkillCreate


class SkillService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active(self) -> list[Skill]:
        result = await self.db.execute(
            select(Skill).where(Skill.is_active == True).order_by(Skill.sort_order.desc())
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Skill]:
        result = await self.db.execute(
            select(Skill).order_by(Skill.sort_order)
        )
        return list(result.scalars().all())

    async def get_by_id(self, skill_id: int) -> Skill | None:
        result = await self.db.execute(select(Skill).where(Skill.id == skill_id))
        return result.scalar_one_or_none()

    async def create(self, req: SkillCreate) -> Skill:
        skill = Skill(**req.model_dump())
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def update(self, skill_id: int, req: SkillCreate) -> Skill:
        skill = await self.get_by_id(skill_id)
        if not skill:
            raise ValueError("Skill 不存在")
        for k, v in req.model_dump().items():
            setattr(skill, k, v)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def delete(self, skill_id: int) -> None:
        skill = await self.get_by_id(skill_id)
        if not skill:
            raise ValueError("Skill 不存在")
        await self.db.delete(skill)
        await self.db.commit()
