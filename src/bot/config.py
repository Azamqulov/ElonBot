from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Bot Token
    BOT_TOKEN: str = Field(default="YOUR_TELEGRAM_BOT_TOKEN_HERE")

    # Superadmin IDs (vergul bilan ajratilgan raqamlar ro'yxati)
    SUPERADMIN_IDS: Union[str, List[int]] = Field(default="123456789")

    # Database URL
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/elonbot.db")

    # Default Telegram Channel (ID yoki username)
    DEFAULT_CHANNEL_ID: str = Field(default="@freelance_uzb")

    # Watermark text
    WATERMARK_TEXT: str = Field(default="@freelance_uzb")

    @field_validator("SUPERADMIN_IDS", mode="before")
    @classmethod
    def parse_superadmin_ids(cls, v: Union[str, List[int], int]) -> List[int]:
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            ids = []
            for item in v.split(","):
                item = item.strip()
                if item.isdigit() or (item.startswith("-") and item[1:].isdigit()):
                    ids.append(int(item))
            return ids
        return []


settings = Settings()
