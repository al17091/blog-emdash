# web-s (EmDash)

このリポジトリは EmDash ベースのブログ構成です（Node.js + SQLite + ローカルストレージ）。

## ローカル起動手順

1. 依存関係をインストール

```bash
pnpm install
```

2. DB初期化とシード投入（初回のみ）

```bash
pnpm bootstrap
```

3. 開発サーバー起動

```bash
pnpm dev
```

4. ブラウザで確認

- サイト: `http://localhost:4321`
- 管理画面: `http://localhost:4321/_emdash/admin`

## 運用コマンド

```bash
# ビルド
pnpm build

# 本番起動（build後）
pnpm start
```

## 補足

- SQLite DB は `data.db`
- 画像アップロード先は `uploads/`
- どちらも `.gitignore` 対象
