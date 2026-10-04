import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    places_api_key: str
    sender_name: str
    demo_output_dir: str
    demo_base_url: str
    daily_send_limit: int
    followup_after_days: int
    max_touches: int
    db_path: str


def load_config() -> Config:
    return Config(
        places_api_key=os.environ.get("GOOGLE_PLACES_API_KEY", ""),
        sender_name=os.environ.get("SENDER_NAME", ""),
        demo_output_dir=os.environ.get("DEMO_OUTPUT_DIR", "demos"),
        demo_base_url=os.environ.get("DEMO_BASE_URL", "https://example.com/demos"),
        daily_send_limit=int(os.environ.get("DAILY_SEND_LIMIT", "20")),
        followup_after_days=int(os.environ.get("FOLLOWUP_AFTER_DAYS", "7")),
        max_touches=int(os.environ.get("MAX_TOUCHES", "2")),
        db_path=os.environ.get("DB_PATH", "leads.db"),
    )


CONFIG = load_config()
