import tempfile
import time
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    RecaptchaChallengeForm,
    ReloginAttemptExceeded,
    SelectContactPointRecoveryForm,
    TwoFactorRequired,
)

from app.config import settings


class InstagramService:
    def __init__(self):
        self.client = Client()
        self.session_file = Path("instagram_session.json")
        self._logged_in = False
        self._last_error = None

        # デバイス情報を設定（ボット検出回避）
        self.client.set_locale("ja_JP")
        self.client.set_timezone_offset(9 * 3600)  # JST (UTC+9)

        # リアルなiPhoneデバイスをシミュレート
        self.client.set_device({
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "devitron",
            "model": "6T Dev",
            "cpu": "qcom",
            "version_code": "314665256",
        })

        # User-Agentを設定
        self.client.set_user_agent(
            "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; OnePlus; 6T Dev; devitron; qcom; ja_JP; 314665256)"
        )

    def get_last_error(self) -> str | None:
        """最後のエラーメッセージを取得"""
        return self._last_error

    async def login(self) -> bool:
        """Instagramにログイン（セッションキャッシュ対応）"""
        if self._logged_in:
            return True

        self._last_error = None

        try:
            # Try to load existing session
            if self.session_file.exists():
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(settings.instagram_username, settings.instagram_password)
                    self.client.get_timeline_feed()
                    self._logged_in = True
                    print("Instagram login successful (from session)")
                    return True
                except LoginRequired:
                    print("Session expired, attempting fresh login...")
                    # セッションファイルを削除
                    self.session_file.unlink()
                except Exception as e:
                    print(f"Session load failed: {e}, attempting fresh login...")
                    # セッションファイルを削除
                    if self.session_file.exists():
                        self.session_file.unlink()

            # Fresh login with delay to appear more human-like
            time.sleep(3)  # 少し長めに待機してから新規ログイン
            print(f"Attempting login with username: {settings.instagram_username}")
            self.client.login(settings.instagram_username, settings.instagram_password)
            self.client.dump_settings(self.session_file)
            self._logged_in = True
            print("Instagram login successful (fresh login)")
            return True

        except BadPassword as e:
            self._last_error = f"パスワードが間違っています (詳細: {e})"
            print(f"Instagram login failed: {self._last_error}")
            # セッションファイルを削除して次回クリーンな状態でリトライ
            if self.session_file.exists():
                self.session_file.unlink()
            return False

        except TwoFactorRequired:
            self._last_error = "2要素認証が必要です。Instagramの設定で2FAを無効にするか、認証コード対応を実装してください"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except ChallengeRequired as e:
            self._last_error = f"ログインチャレンジが必要です。Instagramアプリまたはメールで承認してください: {e}"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except RecaptchaChallengeForm:
            self._last_error = "reCAPTCHA認証が必要です。しばらく待ってから再試行してください"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except SelectContactPointRecoveryForm:
            self._last_error = "アカウント回復が必要です。Instagramアプリで確認してください"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except PleaseWaitFewMinutes:
            self._last_error = "リクエストが多すぎます。数分待ってから再試行してください"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except ReloginAttemptExceeded:
            self._last_error = "ログイン試行回数を超えました。しばらく待ってから再試行してください"
            print(f"Instagram login failed: {self._last_error}")
            return False

        except Exception as e:
            self._last_error = f"不明なエラー: {type(e).__name__}: {e}"
            print(f"Instagram login failed: {self._last_error}")
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
