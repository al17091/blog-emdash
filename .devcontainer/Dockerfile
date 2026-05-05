# EmDash/Astro 6 を使うため Node 24 ベースにしています。
FROM mcr.microsoft.com/devcontainers/javascript-node:24

# 必要に応じて追加のパッケージをインストール
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# pnpmを使用する場合（高速でおすすめ）
RUN su node -c "npm install -g pnpm"
