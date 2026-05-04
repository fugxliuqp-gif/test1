"""种子数据脚本 — 初始化 CMS 示例数据。

用法:
    cd backend && python seed.py
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.models.cms import Banner, ContactInfo, EnterpriseApplication, Policy, Skill


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # 检查是否已有数据
        result = await session.execute(text("SELECT COUNT(*) FROM banners"))
        count = result.scalar()
        if count and count > 0:
            print("数据库已有数据，跳过种子数据插入。")
            await engine.dispose()
            return

        # Banner
        session.add_all([
            Banner(
                title="智驭安全，赋能工业",
                subtitle="AI 智能体驱动的工业安全底座",
                image_url="/images/hero-bg.jpg",
                button_text="申请入驻",
                button_link="#apply",
                sort_order=1, is_active=True,
            ),
            Banner(
                title="让隐患无所遁形",
                subtitle="全链路 AI 安全管理体系",
                image_url="/images/hero-bg2.jpg",
                button_text="了解更多",
                button_link="#skills",
                sort_order=2, is_active=True,
            ),
        ])

        # Skill
        session.add_all([
            Skill(
                key="skill-a", name="工业视觉安全监测",
                icon="📂",
                summary="基于计算机视觉的实时安全监测系统，自动识别违规操作与安全隐患",
                description="利用深度学习模型对工厂视频流进行实时分析，覆盖安全帽检测、区域入侵识别、违规操作预警等场景。支持对接已有视频监控系统，零改造部署。",
                capabilities='["安全帽检测","区域入侵","违规操作预警","烟火识别","实时告警"]',
                platforms='["海康","大华","宇视","定制 RTSP"]',
                sort_order=1, is_active=True,
            ),
            Skill(
                key="skill-b", name="智能风险预警平台",
                icon="📤",
                summary="多维度风险数据融合分析，实现从被动响应到主动预防的跨越",
                description="汇聚设备传感器、环境监测、人员行为等多源数据，通过 AI 模型进行风险分级预警。支持自定义预警规则、自动派单、闭环跟踪。",
                capabilities='["多源数据融合","风险分级","自动派单","闭环跟踪","趋势分析"]',
                platforms='["Web","移动端","大屏"]',
                sort_order=2, is_active=True,
            ),
            Skill(
                key="skill-c", name="安全生产知识图谱",
                icon="🛡️",
                summary="构建行业级安全生产知识底座，赋能智能决策与合规审查",
                description="整合法律法规、标准规范、事故案例、应急预案等多维知识，构建安全生产领域知识图谱。支持智能问答、合规检查、辅助决策。",
                capabilities='["知识建模","智能问答","合规检查","辅助决策","案例检索"]',
                platforms='["Web","API"]',
                sort_order=3, is_active=True,
            ),
        ])

        # Policy
        session.add_all([
            Policy(
                dept="应急管理部", doc_number="应急〔2023〕1号",
                title="《关于推进安全生产数字化转型的指导意见》",
                description="明确 2025 年底前完成重点行业安全生产数字化平台建设，推动 AI、大数据等技术在安全管理中的深度应用。",
                sort_order=1, is_active=True,
            ),
            Policy(
                dept="工业和信息化部", doc_number="工信部联安全〔2023〕60号",
                title="《工业互联网安全分类分级管理办法》",
                description="要求工业互联网平台企业按照安全风险等级落实安全防护措施，建立安全监测预警机制。",
                sort_order=2, is_active=True,
            ),
            Policy(
                dept="江苏省应急管理厅", doc_number="苏应急规〔2024〕2号",
                title="《江苏省工贸企业安全生产数字化建设指引》",
                description="指导省内工贸企业开展安全生产数字化建设，鼓励采用 AI 智能体等新技术提升安全管理水平。",
                sort_order=3, is_active=True,
            ),
        ])

        # ContactInfo
        session.add_all([
            ContactInfo(type="manager", label="客户经理", value="王经理：025-83211234", display_order=1),
            ContactInfo(type="email", label="电子邮箱", value="contact@njliusu.com", display_order=2),
            ContactInfo(type="phone", label="服务热线", value="400-888-9999", display_order=3),
            ContactInfo(type="address", label="办公地址", value="江苏省南京市雨花台区软件大道 168 号", display_order=4),
        ])

        await session.commit()

    print("种子数据插入成功！")
    print(f"  - Banner: 2 条")
    print(f"  - Skill: 3 条")
    print(f"  - Policy: 3 条")
    print(f"  - ContactInfo: 4 条")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
