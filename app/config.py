from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI
    openai_api_key: str

    # Instagram
    instagram_username: str
    instagram_password: str

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "change-me-in-production"

    # Paths
    images_dir: Path = Path("./images")
    database_url: str = "sqlite+aiosqlite:///./diet_app.db"

    # Instagram hashtags
    default_hashtags: list[str] = [
        "#chatgptダイエット",
        "#ダイエット記録",
        "#PFC管理",
        "#食事記録",
    ]


settings = Settings()

# Ensure images directory exists
settings.images_dir.mkdir(parents=True, exist_ok=True)
