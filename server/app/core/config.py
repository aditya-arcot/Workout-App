import os
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


class DatabaseSettings(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str

    @computed_field
    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password}@{self.host}:"
            f"{self.port}/{self.name}"
        )


class EmailSmtpSettings(BaseModel):
    backend: Literal["smtp"]
    # allow arbitrary string
    email_from: str
    smtp_host: str
    smtp_username: str
    smtp_password: str

    @computed_field
    @property
    def smtp_port(self) -> int:
        return 1025


class EmailLocalSettings(BaseModel):
    backend: Literal["local"]
    email_from: str
    smtp_host: str

    @computed_field
    @property
    def smtp_port(self) -> int:
        return 1026

    @computed_field
    @property
    def smtp_username(self) -> None:
        return None

    @computed_field
    @property
    def smtp_password(self) -> None:
        return None


class EmailConsoleSettings(BaseModel):
    backend: Literal["console"]

    @computed_field
    @property
    def email_from(self) -> None:
        return None

    @computed_field
    @property
    def smtp_host(self) -> None:
        return None

    @computed_field
    @property
    def smtp_port(self) -> None:
        return None

    @computed_field
    @property
    def smtp_username(self) -> None:
        return None

    @computed_field
    @property
    def smtp_password(self) -> None:
        return None


class EmailDisabledSettings(BaseModel):
    backend: Literal["disabled"]

    @computed_field
    @property
    def email_from(self) -> None:
        return None

    @computed_field
    @property
    def smtp_host(self) -> None:
        return None

    @computed_field
    @property
    def smtp_port(self) -> None:
        return None

    @computed_field
    @property
    def smtp_username(self) -> None:
        return None

    @computed_field
    @property
    def smtp_password(self) -> None:
        return None


EmailSettings = Union[
    EmailSmtpSettings, EmailLocalSettings, EmailConsoleSettings, EmailDisabledSettings
]


class GitHubApiSettings(BaseModel):
    backend: Literal["api"]
    repo_owner: str
    token: str


class GitHubConsoleSettings(BaseModel):
    backend: Literal["console"]

    @computed_field
    @property
    def repo_owner(self) -> None:
        return None

    @computed_field
    @property
    def token(self) -> None:
        return None


GitHubSettings = Union[GitHubApiSettings, GitHubConsoleSettings]


class Settings(BaseSettings):
    env: Literal["dev", "test", "stage", "prod"]
    log_level: Literal["debug", "info", "warning", "error", "critical"]
    client_url: str

    admin: AdminSettings
    jwt: JWTSettings
    database: DatabaseSettings
    # discriminator with any caps does not work
    email: Annotated[EmailSettings, Field(discriminator="backend")]
    gh: Annotated[GitHubSettings, Field(discriminator="backend")]

    @computed_field
    @property
    def repo_name(self) -> str:
        return "RepTrack"

    @computed_field
    @property
    def project_name(self) -> str:
        if self.env == "prod":
            return self.repo_name
        return f"{self.repo_name}-{self.env.capitalize()}"

    @computed_field
    @property
    def is_prod(self) -> bool:
        return self.env == "stage" or self.env == "prod"

    @computed_field
    @property
    def cors_urls(self) -> list[str]:
        cors_urls = [self.client_url]
        if not self.is_prod:
            cors_urls.append("http://localhost")
        return cors_urls

    @computed_field
    @property
    def cookie_secure(self) -> bool:
        # must be False for pytest in test env
        return self.env != "test"

    @computed_field
    @property
    def cookie_same_site(self) -> Literal["lax", "none"]:
        return "lax" if self.is_prod else "none"

    @computed_field
    @property
    def data_dir(self) -> Path:
        path = Path("data")
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        return path.resolve()

    @computed_field
    @property
    def log_dir(self) -> Path:
        path = Path("logs")
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        return path.resolve()

    @model_validator(mode="after")
    def check_github_config(self):
        if self.is_prod and self.gh.backend != "api":
            raise ValueError("github.backend must be 'api' in production")
        return self

    @model_validator(mode="after")
    def check_email_config(self):
        if self.is_prod and self.email.backend != "smtp":
            raise ValueError("email.backend must be 'smtp' in production")
        return self

    model_config = SettingsConfigDict(
        env_file="../config/env/.env",
        # dot delimiter prevents loading in bash
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()  # type: ignore
