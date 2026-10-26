from pydantic_settings import BaseSettings
from typing import List


def _parse_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Solomentor Backend"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # AI Models (primary + 3 secondaries)
    AI_PRIMARY_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    AI_SECONDARY_MODELS_CSV: str = "google/gemini-2.0-flash-exp:free,qwen/qwen-2.5-7b-instruct:free,microsoft/phi-3-mini-128k-instruct:free"

    def get_secondary_models(self) -> List[str]:
        return _parse_csv(self.AI_SECONDARY_MODELS_CSV)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()