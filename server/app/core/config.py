from typing import Literal

from pydantic import EmailStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: Literal["dev", "test", "stage", "prod"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    CLIENT_URL: str

    @computed_field
    @property
    def IS_PROD(self) -> bool:
        return self.ENV == "stage" or self.ENV == "prod"

    @computed_field
    @property
    def CORS_URLS(self) -> list[str]:
        cors_urls = [self.CLIENT_URL]
        if not self.IS_PROD:
            cors_urls.append("http://localhost")
        return cors_urls

    @computed_field
    @property
    def COOKIE_SAME_SITE(self) -> Literal["lax", "none"]:
        return "lax" if self.IS_PROD else "none"

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_FIRST_NAME: str
    ADMIN_LAST_NAME: str
    ADMIN_PASSWORD: str

    EMAIL_BACKEND: Literal["smtp", "console", "disabled"]
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str | None
    SMTP_PASSWORD: str | None
    SMTP_USE_TLS: bool
    SMTP_USE_SSL: bool
    EMAIL_FROM: EmailStr

    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file="../config/env/.env",
        extra="ignore",
    )


settings = Settings()  # type: ignore
