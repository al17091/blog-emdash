// Astroの設定ファイル: Tailwind CSSインテグレーションを有効化
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  // RSS/OGの絶対URL生成用（本番では SITE_URL を設定推奨）
  site: process.env.SITE_URL ?? 'http://localhost:4321',
  // インテグレーション: Tailwind CSS を使用
  integrations: [tailwind()],
});
