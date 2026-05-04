from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms import ContactInfo
from app.schemas.contact import ContactCreate


class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[ContactInfo]:
        result = await self.db.execute(
            select(ContactInfo).order_by(ContactInfo.display_order)
        )
        return list(result.scalars().all())

    async def get_by_id(self, contact_id: int) -> ContactInfo | None:
        result = await self.db.execute(select(ContactInfo).where(ContactInfo.id == contact_id))
        return result.scalar_one_or_none()

    async def create(self, req: ContactCreate) -> ContactInfo:
        contact = ContactInfo(**req.model_dump())
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update(self, contact_id: int, req: ContactCreate) -> ContactInfo:
        contact = await self.get_by_id(contact_id)
        if not contact:
            raise ValueError("联系方式不存在")
        for k, v in req.model_dump().items():
            setattr(contact, k, v)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int) -> None:
        contact = await self.get_by_id(contact_id)
        if not contact:
            raise ValueError("联系方式不存在")
        await self.db.delete(contact)
        await self.db.commit()
