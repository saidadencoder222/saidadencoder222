import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    youtube_api_key: str
    sender_name: str
    product_name: str
    product_link: str
    daily_send_limit: int
    followup_after_days: int
    max_touches: int
    db_path: str


def load_config() -> Config:
    return Config(
        youtube_api_key=os.environ.get("YOUTUBE_API_KEY", ""),
        sender_name=os.environ.get("SENDER_NAME", ""),
        product_name=os.environ.get("PRODUCT_NAME", ""),
        product_link=os.environ.get("PRODUCT_LINK", ""),
        daily_send_limit=int(os.environ.get("DAILY_SEND_LIMIT", "20")),
        followup_after_days=int(os.environ.get("FOLLOWUP_AFTER_DAYS", "7")),
        max_touches=int(os.environ.get("MAX_TOUCHES", "2")),
        db_path=os.environ.get("DB_PATH", "leads.db"),
    )


CONFIG = load_config()
