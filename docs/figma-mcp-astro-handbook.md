# Figma MCP 連携で Astro サイトを構築する手順書

## 0. 目的
Google Stitch で作成した UI を Figma に取り込み済みの状態から、MCP 経由でデータを取得し、Astro 側の構造化データ (`src/data/home.design.json`) に反映して Web サイトを構築する。

このリポジトリは、すでに以下の受け皿が用意されている。
- `src/data/home.design.json`: Figma 由来データの入力
- `src/lib/figma/mapHomePageDesign.ts`: 欠損値を吸収するマッパー
- `src/pages/index.astro`: マッパー結果をコンポーネントへ渡して描画

## 1. 全体フロー
1. Figma 側で「公開用フレーム」と命名ルールを整理
2. MCP クライアントから Figma ファイル/ノードを取得
3. 取得データを `home.design.json` のスキーマに合わせて整形
4. `pnpm dev` で見た目確認
5. コンポーネント不足分を Astro 側に追加
6. 変更をコミットし、以後は「Figma更新→JSON更新→確認」を反復

## 2. 事前準備

### 2.1 ローカル起動
1. Dev Container でこのリポジトリを開く
2. 依存が未導入なら `pnpm install`
3. 開発サーバー起動: `pnpm dev`
4. `http://localhost:4321` で初期ページ表示を確認

### 2.2 Figma 側の準備
1. Stitch から取り込んだページで、公開対象フレームを 1 つ決める
2. テキストやボタンに意味的な命名を付ける（例: `hero.heading`, `hero.primaryCta.label`）
3. 不要なレイヤー（装飾のみ、非表示、試作残骸）を整理
4. 可能なら「Web 反映対象」ページを分離しておく

### 2.3 MCP 接続情報
使う MCP クライアント（例: IDE 拡張、デスクトップクライアント）で、以下を設定する。
- Figma API トークン
- 対象ファイル ID
- 取得対象ノード ID（必要な場合）

## 3. データ取得（MCP）
1. MCP クライアントで Figma サーバーへ接続
2. 対象ファイルのメタ情報を取得し、接続できることを確認
3. 公開対象フレームのノード情報（テキスト、リンク、セクション構造）を取得
4. まずは以下キーだけを取り出す
   - `hero.eyebrow`
   - `hero.heading`
   - `hero.description`
   - `hero.primaryCta.label`
   - `hero.primaryCta.href`
   - `hero.secondaryCta.label`
   - `hero.secondaryCta.href`
   - `features[]` の `title` / `description`

## 4. JSON 反映
1. `src/data/home.design.json` を開く
2. MCP 出力を次の形式に合わせて更新する

```json
{
  "meta": {
    "title": "ページタイトル"
  },
  "hero": {
    "eyebrow": "...",
    "heading": "...",
    "description": "...",
    "primaryCta": {
      "label": "...",
      "href": "..."
    },
    "secondaryCta": {
      "label": "...",
      "href": "..."
    }
  },
  "features": [
    {
      "title": "...",
      "description": "..."
    }
  ]
}
```

3. 未確定値は空文字ではなく、暫定値を入れる（ビルド確認しやすくするため）
4. 保存後、`pnpm dev` で画面確認

## 5. Astro 側実装ルール

### 5.1 既存ページへの反映
- `src/pages/index.astro` は `mapHomePageDesign` を経由して描画する
- 欠損があっても `mapHomePageDesign.ts` のデフォルトで崩れにくい

### 5.2 セクション追加時
1. Figma 側でセクション名を確定（例: testimonials）
2. `home.design.json` に新キー追加
3. `src/lib/figma/mapHomePageDesign.ts` に型とデフォルト値を追加
4. `src/components/sections/` に Astro コンポーネント追加
5. `src/pages/index.astro` から呼び出す

## 6. 運用サイクル（実務向け）
1. Figma で文言/構成更新
2. MCP で差分取得
3. `home.design.json` 更新
4. 目視確認（PC/SP）
5. 必要ならスタイル微調整
6. コミット

コミットメッセージ例:
- `feat: sync hero copy from figma mcp`
- `feat: add feature cards section from figma`
- `fix: fallback defaults for missing figma fields`

## 7. トラブルシュート

### 症状: 文言が画面に出ない
- `home.design.json` のキー名が `mapHomePageDesign.ts` の期待と一致しているか確認
- `features` の各要素に `title` と `description` が両方あるか確認（片方欠けると除外される）

### 症状: ボタンリンクが効かない
- `href` が空文字になっていないか確認
- 外部リンクの場合は `https://` 付きか確認

### 症状: Figma 側の変更が取り込みづらい
- レイヤー命名を「意味ベース」に寄せる
- 公開対象フレームを分ける
- 抽出対象をまずテキスト中心に絞り、画像や装飾は後段で対応する

## 8. 最短チェックリスト
- [ ] `pnpm dev` でページが起動する
- [ ] MCP で対象フレームのデータが取得できる
- [ ] `src/data/home.design.json` を更新できた
- [ ] 画面で Hero / Features が更新反映された
- [ ] 変更をコミットした

