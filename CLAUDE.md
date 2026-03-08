# CLAUDE.md

このファイルはClaude Code（claude.ai/code）がこのリポジトリを扱う際の参考情報です。

## プロジェクト概要

ChatGPT Diet App - AI × Instagram自動投稿でダイエット記録を継続するフルスタックアプリ

## 技術スタック

- **バックエンド**: FastAPI (Python 3.11+)
- **フロントエンド**: Vanilla JS + Chart.js（SPA、`app/static/index.html`）
- **データベース**: SQLite + SQLAlchemy async
- **AI**: OpenAI GPT-4o（PFC分析）、DALL-E（画像生成）
- **外部連携**: Instagram（instagrapi）

## よく使うコマンド

```bash
# ローカル起動（Docker）
docker compose up -d

# ローカル起動（Python）
pip install -e .
python -m app.main

# テスト
pytest

# リント
ruff check .

# 本番デプロイ（Railway）
git push origin main
```

## プロジェクト構造

```
app/
├── main.py              # FastAPIアプリケーション
├── config.py            # 環境変数設定
├── api/routes.py        # APIエンドポイント
├── models/
│   ├── database.py      # SQLAlchemyモデル
│   └── schemas.py       # Pydanticスキーマ
├── services/
│   ├── meal_processor.py    # 食事処理パイプライン
│   ├── openai_service.py    # OpenAI連携
│   └── instagram_service.py # Instagram投稿
└── static/
    └── index.html       # フロントエンドSPA
```

## デプロイ

### 本番環境

- **URL**: https://chatgpt-diet-app-production.up.railway.app/
- **プラットフォーム**: Railway
- **デプロイ方法**: GitHub連携による自動デプロイ（`main`ブランチ）

### デプロイ時の注意事項

1. **自動デプロイ**: `main`ブランチへのプッシュで自動デプロイされる
2. **環境変数**: Railwayダッシュボードで管理（`.env`ファイルは使用されない）
3. **データ永続化**: Railway Volumeを`/data`にマウントすることでSQLiteを永続化（設定済み）
4. **ログ確認**: Railwayダッシュボードの「Logs」タブで確認
5. **ロールバック**: Railwayダッシュボードから過去のデプロイに戻すことが可能

### Railway Volume設定

SQLiteデータを永続化するためにVolumeが設定されている：
- Mount Path: `/data`
- DBファイル: `/data/diet_app.db`

アプリは`/data`ディレクトリが存在すれば自動的にそちらを使用する（`app/config.py`の`db_url`プロパティ）。

### 環境変数（本番で必要）

| 変数名 | 説明 |
|--------|------|
| `OPENAI_API_KEY` | OpenAI APIキー（必須） |
| `SECRET_KEY` | API認証キー（必須） |
| `INSTAGRAM_USERNAME` | Instagramユーザー名 |
| `INSTAGRAM_PASSWORD` | Instagramパスワード |

### トラブルシューティング

- **デプロイ失敗**: Railwayダッシュボードでビルドログを確認
- **APIエラー**: `X-API-Key`ヘッダーが正しいか確認
- **Instagram投稿失敗**: 2段階認証やアカウント制限を確認

## API認証

すべてのAPIエンドポイント（`/api/v1/health`を除く）は`X-API-Key`ヘッダーが必要：

```bash
curl -H "X-API-Key: YOUR_SECRET_KEY" https://chatgpt-diet-app-production.up.railway.app/api/v1/meal/history
```

## フロントエンド

- **入力タブ**: 食事記録（朝食・昼食・夕食・間食）
- **カレンダータブ**: 月間履歴表示
- **グラフタブ**: カロリー・タンパク質の推移（Chart.js）

PWAとしてiOSホーム画面に追加可能。
