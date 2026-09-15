from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Amazon Backend System"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/amazon_db"
    secret_key: str = "change-me-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    redis_url: str = "redis://127.0.0.1:6379/0"
    mongodb_url: str = "mongodb://127.0.0.1:27017"
    mongodb_database: str = "amazon_events"
    chroma_path: str = "./data/chroma"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
