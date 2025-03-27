from functools import lru_cache

from pydantic_settings import BaseSettings


@lru_cache()
def get_settings():
    return Settings()


class Settings(BaseSettings):
    app_name: str = "r2lark"

    push_template_id: str = "ctp_AAydM4VlgIBl"
    issue_template_id: str = "ctp_AAydOzv3yGRD"
    issue_comment_template_id: str = "ctp_AAy45ODQkUZY"
    pr_template_id: str = "ctp_AAyISOdEupq3"

    lark_webhook_base_url: str = "https://open.feishu.cn/open-apis/bot/v2/hook/"
    lark_webhook_url: str = ""
    lark_webhook_secret: str = ""

    github_webhook_secret: str = ""

    use_secret: bool = False

    class Config:
        env_file = ".env"


settings = get_settings()
