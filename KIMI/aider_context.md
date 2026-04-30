# Aider 上下文 — 项目架构摘要
# 每次调度 Aider 前，Hermes 会更新此文件
# aidexec.sh 的 AIDER_CONTEXT_FILE 指向此处

## 项目
南京流苏智慧信息技术有限公司 — AI 智能体平台官网 + SaaS

## 技术栈
- Backend: FastAPI + SQLAlchemy async + SQLite (开发) / PostgreSQL (生产)
- Frontend: React 19 + TypeScript + Vite + Ant Design 6
- Auth: JWT (python-jose HS256)

## 目录结构
- backend/app/main.py — 入口
- backend/app/core/ — config / database / security
- backend/app/models/cms.py — Banner, Skill, Policy, ContactInfo, EnterpriseApplication
- backend/app/api/v1/ — auth.py, endpoints.py (公开+管理路由), router.py
- frontend/src/pages/LandingPage.tsx — 官网首页
- frontend/src/pages/admin/ — AdminLogin, AdminDashboard

## 安全红线
- SEC-001: 禁止从前端传入 tenant_id
- SEC-002: 禁止暴露其他企业信息
- SEC-003: 禁止明文存储密码
- SEC-004: 禁止物理删除用户
- SEC-005: License 过期必须有中间件拦截

## 已完成的模块
- P1-01: 后端脚手架（Config / Database / JWT）
- P1-02: CMS 数据模型 + API（5 表 + 25 路由）
- P1-03: 官网前端 LandingPage（Hero / 关于 / Skill / 政策 / 申请）
- P1-04: 管理后台（登录 / 入驻审核 / Banner+Skill 管理）
