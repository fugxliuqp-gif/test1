from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import Banner
from app.schemas.banner import BannerCreate


class BannerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active(self) -> list[Banner]:
        result = await self.db.execute(
            select(Banner).where(Banner.is_active == True).order_by(Banner.sort_order)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Banner]:
        result = await self.db.execute(
            select(Banner).order_by(Banner.sort_order)
        )
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
