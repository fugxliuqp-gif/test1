import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.banner import BannerCreate
from app.services.banner import BannerService


@pytest.mark.asyncio
async def test_create_banner(db_session: AsyncSession):
    svc = BannerService(db_session)
    banner = await svc.create(BannerCreate(title="测试Banner", image_url="https://example.com/img.jpg"))
    assert banner.id is not None
    assert banner.title == "测试Banner"
    assert banner.is_active is True
    assert banner.sort_order == 0


@pytest.mark.asyncio
async def test_get_all_banners(db_session: AsyncSession):
    svc = BannerService(db_session)
    await svc.create(BannerCreate(title="B1", image_url="https://example.com/1.jpg", sort_order=1))
    await svc.create(BannerCreate(title="B2", image_url="https://example.com/2.jpg", sort_order=2))
    banners = await svc.get_all()
    assert len(banners) == 2


@pytest.mark.asyncio
async def test_get_active_banners_only(db_session: AsyncSession):
    svc = BannerService(db_session)
    await svc.create(BannerCreate(title="Active", image_url="https://example.com/a.jpg", is_active=True))
    await svc.create(BannerCreate(title="Inactive", image_url="https://example.com/i.jpg", is_active=False))
    active = await svc.get_active()
    assert len(active) == 1
    assert active[0].title == "Active"


@pytest.mark.asyncio
async def test_get_banner_by_id(db_session: AsyncSession):
    svc = BannerService(db_session)
    created = await svc.create(BannerCreate(title="查找测试", image_url="https://example.com/find.jpg"))
    found = await svc.get_by_id(created.id)
    assert found is not None
    assert found.title == "查找测试"


@pytest.mark.asyncio
async def test_get_banner_by_id_not_found(db_session: AsyncSession):
    svc = BannerService(db_session)
    result = await svc.get_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_update_banner(db_session: AsyncSession):
    svc = BannerService(db_session)
    created = await svc.create(BannerCreate(title="旧标题", image_url="https://example.jpg"))
    updated = await svc.update(created.id, BannerCreate(title="新标题", image_url="https://example.jpg"))
    assert updated.title == "新标题"


@pytest.mark.asyncio
async def test_update_banner_not_found(db_session: AsyncSession):
    svc = BannerService(db_session)
    with pytest.raises(ValueError, match="Banner 不存在"):
        await svc.update(999, BannerCreate(title="无", image_url="https://example.jpg"))


@pytest.mark.asyncio
async def test_delete_banner(db_session: AsyncSession):
    svc = BannerService(db_session)
    created = await svc.create(BannerCreate(title="待删除", image_url="https://example.jpg"))
    await svc.delete(created.id)
    assert await svc.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_banner_not_found(db_session: AsyncSession):
    svc = BannerService(db_session)
    with pytest.raises(ValueError, match="Banner 不存在"):
        await svc.delete(999)
