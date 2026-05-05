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

※ `pnpm dev` 実行時に別ポートが表示される場合は、ターミナルに出ているURLを優先してください。

## 運用コマンド

```bash
# ビルド
pnpm build

# 本番起動（build後）
pnpm start
```

## 本番デプロイ時のシード（重要）

`seed/seed.json` を更新しても、本番のDBは自動では更新されません。**本番でEmDashの管理/DBを使う場合は、デプロイ後にシード適用が必要**です。

- 初回デプロイ（DBが空）: `pnpm bootstrap`（マイグレーション + seed投入）
- 以降、`seed/seed.json` を変更したとき: `pnpm seed:update`（seedの再適用 + 既存スキーマ/フィールドの更新）

本番で記事/ユーザー/設定/アップロードを保持したい場合は、`data.db` と `uploads/` がデプロイのたびに消えないように**永続化**してください（環境によってはコンテナ再作成で初期化されます）。

## 補足

- SQLite DB は `data.db`
- 画像アップロード先は `uploads/`
- どちらも `.gitignore` 対象

## Admin導線の表示

ヘッダー等に `/_emdash/admin` へのリンクを表示したい場合だけ、環境変数を有効化します。

```bash
PUBLIC_SHOW_ADMIN_LINK=1 pnpm dev
```
