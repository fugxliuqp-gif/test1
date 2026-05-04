import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.contact import ContactCreate
from app.services.contact import ContactService


@pytest.mark.asyncio
async def test_create_contact(db_session: AsyncSession):
    svc = ContactService(db_session)
    contact = await svc.create(ContactCreate(type="email", label="邮箱", value="test@example.com"))
    assert contact.id is not None
    assert contact.type == "email"
    assert contact.value == "test@example.com"


@pytest.mark.asyncio
async def test_get_all_contacts(db_session: AsyncSession):
    svc = ContactService(db_session)
    await svc.create(ContactCreate(type="email", label="邮箱1", value="a@example.com", display_order=1))
    await svc.create(ContactCreate(type="phone", label="电话", value="123456", display_order=2))
    contacts = await svc.get_all()
    assert len(contacts) == 2


@pytest.mark.asyncio
async def test_get_contact_by_id(db_session: AsyncSession):
    svc = ContactService(db_session)
    created = await svc.create(ContactCreate(type="email", label="查找", value="find@example.com"))
    found = await svc.get_by_id(created.id)
    assert found is not None
    assert found.label == "查找"


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(db_session: AsyncSession):
    svc = ContactService(db_session)
    assert await svc.get_by_id(999) is None


@pytest.mark.asyncio
async def test_update_contact(db_session: AsyncSession):
    svc = ContactService(db_session)
    created = await svc.create(ContactCreate(type="email", label="旧标签", value="old@example.com"))
    updated = await svc.update(created.id, ContactCreate(type="phone", label="新标签", value="new@example.com"))
    assert updated.label == "新标签"
    assert updated.value == "new@example.com"


@pytest.mark.asyncio
async def test_update_contact_not_found(db_session: AsyncSession):
    svc = ContactService(db_session)
    with pytest.raises(ValueError, match="联系方式不存在"):
        await svc.update(999, ContactCreate(type="email", label="无", value="x@x.com"))


@pytest.mark.asyncio
async def test_delete_contact(db_session: AsyncSession):
    svc = ContactService(db_session)
    created = await svc.create(ContactCreate(type="email", label="待删除", value="del@example.com"))
    await svc.delete(created.id)
    assert await svc.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_contact_not_found(db_session: AsyncSession):
    svc = ContactService(db_session)
    with pytest.raises(ValueError, match="联系方式不存在"):
        await svc.delete(999)
