import asyncio
import sys
import os

# 确保能找到 app 模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.core.database import engine, Base, async_session_maker
from app.models.cms import Banner, Skill, Policy, ContactInfo


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # 检查是否已有数据
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(Banner.id)))
        if result.scalar() > 0:
            print("✅ 数据已存在，跳过初始化")
            return

        # Banner
        session.add(Banner(
            title="智驭安全，赋能工业",
            subtitle="AI 智能体驱动的工业安全底座",
            image_url="",
            button_text="申请入驻",
            button_link="#apply",
            sort_order=1,
        ))

        # Skills
        skills_data = [
            Skill(key="skill-a", name="数字资产自动化管理", icon="📂",
                  summary="让企业的文件和数据'活'起来——自动扫描、识别、解析、入库",
                  description="自动扫描企业数据源，分类、清洗、入库、向量化，构建企业知识资产库。告别数据沉睡，让每份文件都能被检索和利用。",
                  capabilities='["自动感知","AI 解析","冲突检测","向量化入库"]',
                  sort_order=1),
            Skill(key="skill-b", name="政府合规自动上报", icon="📤",
                  summary="让企业从'每天填表上报'中彻底解放",
                  description="系统自动从企业内部数据提取、组装、上传到各政府监管平台。支持应急管理部、环保局、人社局、消防等多平台对接。",
                  capabilities='["自动提取","格式转换","自动填报","失败重试"]',
                  platforms='["应急管理部","环保局","人社局","消防"]',
                  sort_order=2),
            Skill(key="skill-c", name="重大危险源 & AI 视频监控", icon="🛡️",
                  summary="24 小时不眨眼的工业安全哨兵",
                  description="融合 IoT 传感器 + 视频 AI + 设备数据分析，实时感知风险、提前预警。支持安全帽检测、区域闯入、烟雾识别等多种 AI 分析场景。",
                  capabilities='["IoT 接入","视频 AI","趋势预测","自动联动"]',
                  sort_order=3),
            Skill(key="skill-d", name="企业内部管控中台", icon="⚙️",
                  summary="把写在纸上的制度变成自动运行的规则引擎",
                  description="双控机制、特殊作业、危化品管理、承包商管理、安全培训全链路数字化。AI 辅助审核作业票，自动派发巡查任务。",
                  capabilities='["风险分级","隐患排查","AI 审核","全链条追踪"]',
                  sort_order=4),
        ]
        for s in skills_data:
            session.add(s)

        # Policies
        policies_data = [
            Policy(dept="应急管理部", doc_number="应急厅〔2022〕5号",
                   title="《危险化学品企业安全风险智能化管控平台建设指南（试行）》",
                   description="流苏平台完全覆盖指南中要求的双重预防、特殊作业、人员定位、智能巡检等核心功能模块的建设标准。",
                   sort_order=1),
            Policy(dept="应急管理部", doc_number="应急厅〔2022〕5号",
                   title="《化工园区安全风险智能化管控平台建设指南（试行）》",
                   description="提供符合国家标准的化工园区与企业数据交互接口，支持区域安全感知、重大危险源监测预警与数据上报。",
                   sort_order=2),
            Policy(dept="应急管理部",
                   title="《危险化学品企业双重预防机制数字化建设工作指南》",
                   description="彻底解决企业双控体系'纸面化'问题，实现隐患排查任务的自动派发、动态跟踪与数据可视化。",
                   sort_order=3),
            Policy(dept="工信部、应急管理部等",
                   title='《"工业互联网+安全生产"行动计划》',
                   description="响应国家号召，将物联网、大数据及 AI 视觉技术深度融合到高危行业，推动企业实现数字化、网络化安全管理。",
                   sort_order=4),
            Policy(dept="中华人民共和国全国人民代表大会",
                   title="新版《中华人民共和国安全生产法》",
                   description="系统化支撑新《安法》中明确要求的'构建安全风险分级管控和隐患排查治理双重预防机制'的落地执行。",
                   sort_order=5),
            Policy(dept="国务院安委会",
                   title="《全国危险化学品安全风险集中治理方案》",
                   description="助力企业全面排查重大安全隐患，利用数字化手段提升危化品生产、储存、使用过程中的风险预警管控能力。",
                   sort_order=6),
        ]
        for p in policies_data:
            session.add(p)

        # Contact
        contacts_data = [
            ContactInfo(type="manager", label="客户经理", value="付先生", display_order=1),
            ContactInfo(type="email", label="电子邮箱", value="176585118@qq.com", display_order=2),
            ContactInfo(type="address", label="办公地址", value="江苏省南京市江北新区高新软件园研发大厦A座6楼612", display_order=3),
        ]
        for c in contacts_data:
            session.add(c)

        await session.commit()
        print("✅ 种子数据初始化完成")


if __name__ == "__main__":
    asyncio.run(init_db())
