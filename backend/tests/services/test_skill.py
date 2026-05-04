import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.skill import SkillCreate
from app.services.skill import SkillService


@pytest.mark.asyncio
async def test_create_skill(db_session: AsyncSession):
    svc = SkillService(db_session)
    skill = await svc.create(SkillCreate(key="python", name="Python", summary="Python 技能"))
    assert skill.id is not None
    assert skill.key == "python"
    assert skill.name == "Python"


@pytest.mark.asyncio
async def test_get_all_skills(db_session: AsyncSession):
    svc = SkillService(db_session)
    await svc.create(SkillCreate(key="go", name="Go", summary="Go 技能"))
    await svc.create(SkillCreate(key="rust", name="Rust", summary="Rust 技能"))
    skills = await svc.get_all()
    assert len(skills) == 2


@pytest.mark.asyncio
async def test_get_active_skills_only(db_session: AsyncSession):
    svc = SkillService(db_session)
    await svc.create(SkillCreate(key="active", name="Active", summary="A", is_active=True))
    await svc.create(SkillCreate(key="inactive", name="Inactive", summary="I", is_active=False))
    active = await svc.get_active()
    assert len(active) == 1
    assert active[0].key == "active"


@pytest.mark.asyncio
async def test_get_skill_by_id(db_session: AsyncSession):
    svc = SkillService(db_session)
    created = await svc.create(SkillCreate(key="find", name="查找", summary="查找测试"))
    found = await svc.get_by_id(created.id)
    assert found is not None
    assert found.key == "find"


@pytest.mark.asyncio
async def test_get_skill_by_id_not_found(db_session: AsyncSession):
    svc = SkillService(db_session)
    assert await svc.get_by_id(999) is None


@pytest.mark.asyncio
async def test_update_skill(db_session: AsyncSession):
    svc = SkillService(db_session)
    created = await svc.create(SkillCreate(key="old", name="旧名称", summary="旧"))
    updated = await svc.update(created.id, SkillCreate(key="new", name="新名称", summary="新"))
    assert updated.name == "新名称"
    assert updated.key == "new"


@pytest.mark.asyncio
async def test_update_skill_not_found(db_session: AsyncSession):
    svc = SkillService(db_session)
    with pytest.raises(ValueError, match="Skill 不存在"):
        await svc.update(999, SkillCreate(key="x", name="无", summary="无"))


@pytest.mark.asyncio
async def test_delete_skill(db_session: AsyncSession):
    svc = SkillService(db_session)
    created = await svc.create(SkillCreate(key="del", name="待删除", summary="待删除"))
    await svc.delete(created.id)
    assert await svc.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_skill_not_found(db_session: AsyncSession):
    svc = SkillService(db_session)
    with pytest.raises(ValueError, match="Skill 不存在"):
        await svc.delete(999)
