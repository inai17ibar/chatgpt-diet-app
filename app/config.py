from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI
    openai_api_key: str

    # Instagram
    instagram_username: str = ""
    instagram_password: str = ""
    instagram_enabled: bool = False  # Instagram投稿を有効にするかどうか

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "change-me-in-production"

    # Paths
    images_dir: Path = Path("./images")
    data_dir: Path = Path("/data")  # Railway Volume用（本番）
    database_url: str | None = None  # 環境変数で上書き可能

    @property
    def db_url(self) -> str:
        """データベースURLを取得（環境変数 > data_dir > デフォルト）"""
        if self.database_url:
            return self.database_url
        # /data ディレクトリが存在する場合はそちらを使用（Railway Volume）
        if self.data_dir.exists():
            return f"sqlite+aiosqlite:///{self.data_dir}/diet_app.db"
        # ローカル開発用
        return "sqlite+aiosqlite:///./diet_app.db"

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
