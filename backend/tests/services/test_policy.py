import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.policy import PolicyCreate
from app.services.policy import PolicyService


@pytest.mark.asyncio
async def test_create_policy(db_session: AsyncSession):
    svc = PolicyService(db_session)
    policy = await svc.create(PolicyCreate(dept="工信部", title="测试政策"))
    assert policy.id is not None
    assert policy.dept == "工信部"
    assert policy.title == "测试政策"


@pytest.mark.asyncio
async def test_get_all_policies(db_session: AsyncSession):
    svc = PolicyService(db_session)
    await svc.create(PolicyCreate(dept="D1", title="P1"))
    await svc.create(PolicyCreate(dept="D2", title="P2"))
    policies = await svc.get_all()
    assert len(policies) == 2


@pytest.mark.asyncio
async def test_get_active_policies_only(db_session: AsyncSession):
    svc = PolicyService(db_session)
    await svc.create(PolicyCreate(dept="D1", title="Active", is_active=True))
    await svc.create(PolicyCreate(dept="D2", title="Inactive", is_active=False))
    active = await svc.get_active()
    assert len(active) == 1
    assert active[0].title == "Active"


@pytest.mark.asyncio
async def test_get_policy_by_id(db_session: AsyncSession):
    svc = PolicyService(db_session)
    created = await svc.create(PolicyCreate(dept="D1", title="查找"))
    found = await svc.get_by_id(created.id)
    assert found is not None
    assert found.title == "查找"


@pytest.mark.asyncio
async def test_get_policy_by_id_not_found(db_session: AsyncSession):
    svc = PolicyService(db_session)
    assert await svc.get_by_id(999) is None


@pytest.mark.asyncio
async def test_update_policy(db_session: AsyncSession):
    svc = PolicyService(db_session)
    created = await svc.create(PolicyCreate(dept="D1", title="旧标题"))
    updated = await svc.update(created.id, PolicyCreate(dept="D2", title="新标题"))
    assert updated.title == "新标题"
    assert updated.dept == "D2"


@pytest.mark.asyncio
async def test_update_policy_not_found(db_session: AsyncSession):
    svc = PolicyService(db_session)
    with pytest.raises(ValueError, match="政策不存在"):
        await svc.update(999, PolicyCreate(dept="D", title="无"))


@pytest.mark.asyncio
async def test_delete_policy(db_session: AsyncSession):
    svc = PolicyService(db_session)
    created = await svc.create(PolicyCreate(dept="D1", title="待删除"))
    await svc.delete(created.id)
    assert await svc.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_policy_not_found(db_session: AsyncSession):
    svc = PolicyService(db_session)
    with pytest.raises(ValueError, match="政策不存在"):
        await svc.delete(999)
