import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.application import ApplyRequest, ReviewRequest
from app.services.application import ApplicationService


@pytest.mark.asyncio
async def test_create_application(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    app = await svc.create(ApplyRequest(
        company_name="测试公司",
        credit_code="91310115MA1H123456",
        industry="科技",
        scale="小型",
        contact_name="张三",
        contact_phone="13800138000",
        contact_email="zhangsan@test.com",
    ))
    assert app.id is not None
    assert app.tracking_code is not None
    assert len(app.tracking_code) == 32
    assert app.status == "pending"


@pytest.mark.asyncio
async def test_get_all_applications(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    await svc.create(ApplyRequest(
        company_name="公司A", credit_code="C1", industry="I1", scale="S1",
        contact_name="N1", contact_phone="P1", contact_email="E1",
    ))
    await svc.create(ApplyRequest(
        company_name="公司B", credit_code="C2", industry="I2", scale="S2",
        contact_name="N2", contact_phone="P2", contact_email="E2",
    ))
    apps = await svc.get_all()
    assert len(apps) == 2


@pytest.mark.asyncio
async def test_get_applications_filter_by_status(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    req = ApplyRequest(
        company_name="公司", credit_code="C", industry="I", scale="S",
        contact_name="N", contact_phone="P", contact_email="E",
    )
    app1 = await svc.create(req)
    app2 = await svc.create(req)

    # 模拟不同状态
    await svc.review(app1.id, ReviewRequest(status="approved"))

    pending = await svc.get_all(status="pending")
    approved = await svc.get_all(status="approved")
    assert len(pending) == 1
    assert len(approved) == 1
    assert approved[0].id == app1.id


@pytest.mark.asyncio
async def test_review_application_approve(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    app = await svc.create(ApplyRequest(
        company_name="审核测试", credit_code="C", industry="I", scale="S",
        contact_name="N", contact_phone="P", contact_email="E",
    ))
    reviewed = await svc.review(app.id, ReviewRequest(status="approved"))
    assert reviewed.status == "approved"


@pytest.mark.asyncio
async def test_review_application_reject(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    app = await svc.create(ApplyRequest(
        company_name="驳回测试", credit_code="C", industry="I", scale="S",
        contact_name="N", contact_phone="P", contact_email="E",
    ))
    reviewed = await svc.review(app.id, ReviewRequest(status="rejected", reject_reason="资料不全"))
    assert reviewed.status == "rejected"
    assert reviewed.reject_reason == "资料不全"


@pytest.mark.asyncio
async def test_review_application_not_found(db_session: AsyncSession):
    svc = ApplicationService(db_session)
    with pytest.raises(ValueError, match="申请不存在"):
        await svc.review(999, ReviewRequest(status="approved"))
