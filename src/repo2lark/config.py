from functools import lru_cache

from pydantic_settings import BaseSettings


@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    app_name: str = "r2lark"

    push_template_id: str = "ctp_AAydM4VlgIBl"

    webhook_url: str = ""
    webhook_secret: str = ""

    class Config:
        env_file = ".env"


settings = get_settings()
