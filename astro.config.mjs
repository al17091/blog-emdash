// Astroの設定ファイル: Tailwind CSSインテグレーションを有効化
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  // インテグレーション: Tailwind CSS を使用
  integrations: [tailwind()],
});
