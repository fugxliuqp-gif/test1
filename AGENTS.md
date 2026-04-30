# AGENTS.md — 南京流苏智慧官网 + AI 智能体平台

> **作用范围**: 本项目根目录及所有子目录
> **最后更新**: 2026-04-30
> **关联文档**: `docs/PRD/01-产品概述与定位.md`, `docs/PRD/02-Skill规格说明书.md`, `docs/PRD/03-官网规格说明书.md`, `docs/PRD/04-SaaS平台规格说明书.md`

---

## 1. 项目概述

本项目为**南京流苏智慧信息技术有限公司**的 AI 智能体平台产品体系，包含：

| 子系统 | 说明 | 依赖关系 |
|--------|------|---------|
| **官网 (www)** | 品牌展示 + Skill 能力宣传 + 企业入驻申请 | 独立 |
| **SaaS 管理后台 (admin)** | 我司超级管理员：入驻审核 + 企业管理 + License + Skill 分配 | 依赖官网的申请数据 |
| **企业端 (enterprise)** | 企业租户独立空间：AI 对话 + Skill 运行 + 数据看板 + 成员管理 | 依赖 admin 创建租户 |
| **Skill 生态** | 可复用的业务智能体，按 License 控制开通 | 依赖企业端运行时 |

---

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 19 + TypeScript + Vite | 三端统一技术栈 |
| **UI** | Ant Design 6 + Tailwind CSS | 企业级组件 + 灵活样式 |
| **状态** | React Query (服务端) + Zustand (客户端) | |
| **后端** | FastAPI + Python 3.11+ | 异步高性能 |
| **ORM** | SQLAlchemy 2.0 async + Alembic | 已有积累 |
| **数据库** | PostgreSQL 15（生产）/ SQLite（开发） | |
| **鉴权** | JWT 双令牌 + RBAC | 参考 ai-admin-demo 实现 |
| **文件存储** | MinIO | 静态文件 + 企业文件 |
| **AI 推理** | LLM Gateway + RAG Pipeline | 基于 Hermes 架构二次开发 |
| **部署** | Docker Compose + Nginx + 腾讯云 | |

---

## 3. 架构约束

### 3.1 分层约束

```
┌────────────────────────────────────┐
│  官网层 (LandingPage / Apply)      │
│  ─ 公开访问，无需认证               │
├────────────────────────────────────┤
│  SaaS 管理层 (super_admin)         │
│  ─ 仅我司超级管理员可访问           │
│  ─ 管理所有企业租户                 │
├────────────────────────────────────┤
│  企业端 (enterprise_admin/member)  │
│  ─ 每个企业独立租户，数据隔离        │
│  ─ 企业管理员管理本企业成员和 Skill  │
├────────────────────────────────────┤
│  Skill 层 (可复用智能体模块)         │
│  ─ 技能即产品，独立注册/部署/升级    │
│  ─ License 控制开通权限             │
└────────────────────────────────────┘
```

### 3.2 路由前缀规范

| 端 | 路由前缀 | 说明 |
|----|---------|------|
| 官网 | `/` | 公开访问 |
| 官网 API | `/api/cms/*` | 官网 CMS 内容管理 |
| 入驻申请 | `/api/apply/*` | 公开提交 |
| SaaS 管理 | `/api/admin/*` | 需 super_admin 认证 |
| 企业端 | `/api/enterprise/*` | 需企业租户认证 |

### 3.3 租户隔离

- 所有企业端 API 必须通过 `get_current_enterprise_user` 中间件
- `tenant_id` 从 JWT 自动注入，禁止从前端传入
- 跨企业数据查询必须带 `tenant_id` 过滤，否则默认拦截

### 3.4 License 控制

- 所有企业端 API 受 License 检查中间件保护
- 过期后白名单操作：查看数据、下载报告、管理成员
- 过期后禁止操作：新增数据、调用 AI 接口、自动上报

---

## 4. 项目目录结构

```
nanjingliusu/
├── docs/
│   ├── PRD/
│   │   ├── 01-产品概述与定位.md
│   │   ├── 02-Skill规格说明书.md
│   │   ├── 03-官网规格说明书.md
│   │   └── 04-SaaS平台规格说明书.md
│   ├── arch/
│   │   └── (架构设计文档，待补充)
│   ├── plan/
│   │   └── todo-list.md
│   └── .handoff/
│       ├── session-snapshot.md
│       ├── agent-state.md
│       └── (其他跨会话交接文件)
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── cms.py          # 官网 CMS API
│   │   │       │   ├── apply.py        # 入驻申请 API
│   │   │       │   ├── admin.py        # SaaS 管理 API
│   │   │       │   └── enterprise.py   # 企业端 API
│   │   │       └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── license.py
│   │   │   └── tenant.py
│   │   ├── models/
│   │   │   ├── cms.py
│   │   │   ├── enterprise.py
│   │   │   ├── user.py
│   │   │   └── license.py
│   │   ├── services/
│   │   │   ├── cms_service.py
│   │   │   ├── apply_service.py
│   │   │   └── enterprise_service.py
│   │   └── skills/
│   │       ├── base.py
│   │       └── builtins/     # 内置 Skill 实现
│   │           ├── skill_a/
│   │           ├── skill_b/
│   │           ├── skill_c/
│   │           └── skill_d/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   └── admin/
│   │   └── hooks/
│   ├── public/
│   ├── vite.config.ts
│   └── package.json
│
├── docker-compose.yml
├── .env.example
├── DEPLOY.md
└── README.md
```

---

## 5. 文档维护矩阵

当修改以下内容时，必须同步更新对应文档：

| 修改内容 | 需更新文档 |
|----------|-----------|
| 产品定位/业务方向 | `docs/PRD/01-产品概述与定位.md` |
| Skill 定义/能力/规格 | `docs/PRD/02-Skill规格说明书.md` |
| 官网内容/交互/API | `docs/PRD/03-官网规格说明书.md` |
| SaaS 平台/租户/License | `docs/PRD/04-SaaS平台规格说明书.md` |
| 架构约束/技术栈变更 | `AGENTS.md` (本文件) |
| 任务进度更新 | `docs/plan/todo-list.md` |
| 工作完成记录 | `docs/plan/work-progress-log.md` |

---

## 6. 编码规范

### 6.1 通用

- 前端使用 TypeScript，后端使用 Python 3.11+
- 所有 API 返回统一格式：`{ code: int, message: str, data?: T, error?: ErrorDetail }`
- 遵循现有 ESLint / Prettier / Ruff 配置

### 6.2 后端

- Router 层只做参数解析和响应组装，业务逻辑放 Service 层
- 数据库查询使用参数化查询，禁止字符串拼接 SQL
- 敏感操作（审核、License 操作）必须记录审计日志

### 6.3 前端

- API 调用统一封装在 `api/` 目录下
- 状态管理使用 Zustand，Store 定义在 `stores/` 目录下
- 组件拆分原则：每页独立文件，公共组件提取到 `components/`

---

## 7. 安全红线

| 编号 | 规则 | 违规后果 |
|------|------|----------|
| SEC-001 | 禁止从前端传入 `tenant_id` / `enterprise_id` 作为业务参数 | CR 直接拒绝 |
| SEC-002 | 禁止在错误信息中暴露其他企业的名称或 ID | CR 直接拒绝 |
| SEC-003 | 禁止明文存储或返回用户密码 | CR 直接拒绝 |
| SEC-004 | 企业间数据必须物理隔离 (行级 tenant_id) | CR 直接拒绝 |
| SEC-005 | License 过期后禁止的操作必须有中间件拦截 | CR 直接拒绝 |
| SEC-006 | 入驻审核操作必须由 super_admin 执行 | CR 直接拒绝 |

---

## 8. Skill 开发规范

每个 Skill 必须遵循以下结构：

```
skill/
├── skill.yaml        # 声明文件 (名称/版本/输入/输出/依赖)
├── executor.py       # Skill 主逻辑
│   ├── perceive()    # 感知：接入数据源
│   ├── analyze()     # 分析：AI 决策/规则引擎
│   ├── execute()     # 执行：调用 API/写入 DB/发送通知
│   └── feedback()    # 反馈：记录日志/通知用户
├── schema.py         # 数据模型
└── tests/
    └── test_*.py     # 测试用例
```

### Skill 接口契约

```python
class BaseSkill(ABC):
    @abstractmethod
    async def perceive(self, context: SkillContext) -> PerceiveResult: ...
    @abstractmethod
    async def analyze(self, context: SkillContext, data: PerceiveResult) -> AnalyzeResult: ...
    @abstractmethod
    async def execute(self, context: SkillContext, decision: AnalyzeResult) -> ExecuteResult: ...
    @abstractmethod
    async def feedback(self, context: SkillContext, result: ExecuteResult) -> None: ...
```

### Skill 注册

每个 Skill 在 `backend/app/skills/builtins/` 下独立目录，启动时自动扫描注册。
