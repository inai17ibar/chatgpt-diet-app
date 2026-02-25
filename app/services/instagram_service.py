import tempfile
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from app.config import settings


class InstagramService:
    def __init__(self):
        self.client = Client()
        self.session_file = Path("instagram_session.json")
        self._logged_in = False

    async def login(self) -> bool:
        """Instagramにログイン（セッションキャッシュ対応）"""
        if self._logged_in:
            return True

        try:
            # Try to load existing session
            if self.session_file.exists():
                self.client.load_settings(self.session_file)
                self.client.login(settings.instagram_username, settings.instagram_password)
                try:
                    self.client.get_timeline_feed()
                    self._logged_in = True
                    return True
                except LoginRequired:
                    # Session expired, re-login
                    pass

            # Fresh login
            self.client.login(settings.instagram_username, settings.instagram_password)
            self.client.dump_settings(self.session_file)
            self._logged_in = True
            return True

        except Exception as e:
            print(f"Instagram login failed: {e}")
            return False

    async def post_photo(self, image_data: bytes, caption: str) -> str | None:
        """写真を投稿してpost_idを返す"""
        if not await self.login():
            raise Exception("Instagram login failed")

        # Add hashtags
        hashtags = " ".join(settings.default_hashtags)
        full_caption = f"{caption}\n\n{hashtags}"

        # Save image to temp file (instagrapi requires file path)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(image_data)
            temp_path = Path(f.name)

        try:
            media = self.client.photo_upload(temp_path, full_caption)
            return media.pk
        finally:
            temp_path.unlink()  # Clean up temp file

    async def post_photo_from_path(self, image_path: Path, caption: str) -> str | None:
        """ファイルパスから写真を投稿"""
        if not await self.login():
            raise Exception("Instagram login failed")

        hashtags = " ".join(settings.default_hashtags)
        full_caption = f"{caption}\n\n{hashtags}"

        media = self.client.photo_upload(image_path, full_caption)
        return media.pk


# Singleton instance
instagram_service = InstagramService()
