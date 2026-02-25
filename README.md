# ChatGPT Diet App

AI × 自動化 × Instagram自動投稿でダイエット記録を継続するアプリ

## 機能

- **写真モード**: 食事写真をアップロード → GPT-4 Visionで自動PFC計算
- **テキストモード**: 食事をテキストで入力 → AI画像生成 + PFC計算
- **自動Instagram投稿**: キャプション自動生成、ハッシュタグ自動追加
- **iPhoneショートカット対応**: 1タップで記録・投稿

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集:

```
OPENAI_API_KEY=sk-your-openai-api-key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
SECRET_KEY=your-secret-api-key
```

### 2. 起動方法

#### Docker（推奨）

```bash
docker compose up -d
```

#### ローカル実行

```bash
# Python 3.11以上が必要
pip install -e .
python -m app.main
```

サーバーが `http://localhost:8000` で起動します。

## API エンドポイント

### ヘルスチェック
```
GET /api/v1/health
```

### 簡易モード（テキストのみ）
```
POST /api/v1/meal/quick?description=昼：サラダチキン、夜：豚しゃぶ
Header: X-API-Key: your-secret-key
```

### フルモード（写真 or テキスト）
```
POST /api/v1/meal/post
Header: X-API-Key: your-secret-key
Content-Type: application/json

{
  "meals": [
    {
      "meal_type": "lunch",
      "description": "サラダチキンとおにぎり",
      "image_base64": "..."  // 任意
    }
  ]
}
```

### iPhoneショートカット用
```
POST /api/v1/shortcut/meal
Header: X-API-Key: your-secret-key

Form Data:
- meal_type: lunch
- description: サラダチキン
- image_base64: (写真のBase64、任意)
```

## iPhoneショートカットの作成

1. **ショートカット**アプリを開く
2. 新規ショートカットを作成
3. 以下のアクションを追加:

### テキストのみの場合:
```
1. [テキストを入力を求める] → 変数「食事」に保存
2. [URLの内容を取得]
   - URL: https://your-server.com/api/v1/meal/quick
   - メソッド: POST
   - ヘッダー: X-API-Key = your-secret-key
   - 本文: フォーム
     - description = 変数「食事」
```

### 写真ありの場合:
```
1. [写真を撮る] or [写真を選択]
2. [Base64エンコード]
3. [テキストを入力を求める] → 変数「説明」に保存
4. [URLの内容を取得]
   - URL: https://your-server.com/api/v1/shortcut/meal
   - メソッド: POST
   - ヘッダー: X-API-Key = your-secret-key
   - 本文: フォーム
     - meal_type = lunch
     - description = 変数「説明」
     - image_base64 = 変数「Base64」
```

## ワークフロー図

```
iPhone → ショートカット
           ↓
      [写真あり？]
         /    \
      Yes      No
       ↓        ↓
   Vision API  テキスト解析
       ↓        ↓
    PFC計算  ← ← ←
       ↓
   キャプション生成
       ↓
   [写真なしの場合]
       ↓
   DALL-E 画像生成
       ↓
   Instagram投稿
       ↓
   SQLite保存
```

## デプロイ

### Railway / Render / Fly.io

1. リポジトリをプッシュ
2. 環境変数を設定
3. Dockerfileでデプロイ

### VPS (Ubuntu)

```bash
# Clone
git clone https://github.com/your/chatgpt-diet-app.git
cd chatgpt-diet-app

# Setup
cp .env.example .env
nano .env  # 環境変数を設定

# Run
docker compose up -d
```

## 注意事項

- Instagram APIは非公式のため、頻繁なログインや大量投稿はアカウント制限の可能性あり
- 1日1-2回の投稿を推奨
- 初回ログイン時は2段階認証の確認が必要な場合あり
