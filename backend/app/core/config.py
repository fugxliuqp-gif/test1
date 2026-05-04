from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "南京流苏官网"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/cms.db"
    SECRET_KEY: str = ""  # 必须从环境变量设置，无默认值
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""  # bcrypt 哈希，必须从环境变量设置
    CORS_ORIGINS: list[str] = ["http://localhost:5174", "http://localhost:8000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# 启动时校验安全配置
if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY 未配置！请在 .env 或环境变量中设置。")
if not settings.ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_PASSWORD_HASH 未配置！请在 .env 或环境变量中设置。")
