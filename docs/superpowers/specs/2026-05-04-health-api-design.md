# 健康检查 API 设计文档

> 为南京流苏后端服务添加标准健康检查端点

**目标：** 提供详细的健康检查接口，用于监控服务运行状态

**架构：** 独立模块 + 现有路由注册模式

**技术栈：** FastAPI, SQLAlchemy (async), Pydantic

---

## API 规范

### `GET /api/v1/health`

返回服务运行状态和依赖组件的健康信息。

**请求示例：**
```
GET /api/v1/health
```

**成功响应 (200)：**
```json
{
  "status": "healthy",
  "app_name": "南京流苏官网",
  "version": "1.0.0",
  "uptime_seconds": 1234,
  "database": "connected",
  "timestamp": "2026-05-04T09:30:00Z"
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | `"healthy"` 或 `"degraded"` |
| `app_name` | string | 应用名称，取自 Settings |
| `version` | string | 版本号 |
| `uptime_seconds` | number | 服务已运行秒数 |
| `database` | string | `"connected"` 或 `"disconnected"` |
| `timestamp` | string | ISO 8601 时间戳 |

**降级场景：** 数据库连接失败时，status 返回 `"degraded"`，HTTP 状态码仍为 200（不触发告警误报），由监控系统根据 `database` 字段判断。

---

## 文件改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/api/v1/health.py` | 新建 | 健康检查模块，含 lifespan 启动时间和 DB 检测 |
| `backend/app/api/v1/router.py` | 修改 | 注册 health_router |
| `backend/app/main.py` | 修改 | 移除旧的 `GET /health`（已被独立模块替代） |

---

## 实现设计

**启动时间记录：** 使用 FastAPI lifespan 上下文，在应用启动时记录 `start_time`，通过 `time.monotonic()` 计算 uptime。

**数据库健康检查：** 创建一个数据库会话池，执行 `SELECT 1`，成功返回 `"connected"`，失败返回 `"disconnected"` 且主状态降级为 `"degraded"`。

**版本号：** 当前硬编码为 `"1.0.0"`。

---

## 测试用例

1. 请求 `GET /api/v1/health` 返回 200
2. `status` 字段为 `"healthy"` 或 `"degraded"`
3. `database` 字段反映真实数据库状态
4. 旧 `GET /health` 端点不再可用
