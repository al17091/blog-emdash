#!/usr/bin/env sh
set -eu

DATA_DIR="${EMDASH_DATA_DIR:-/data}"
DB_ENGINE="${EMDASH_DB:-sqlite}"

mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/uploads"

# EmDash config is currently relative to /app:
# - SQLite: ./data.db (optional)
# - Uploads: ./uploads
#
# Keep those paths stable while persisting data on a mounted volume.
case "$DB_ENGINE" in
  postgres|pg)
    ;;
  *)
    if [ ! -e "/app/data.db" ]; then
      ln -s "$DATA_DIR/data.db" "/app/data.db"
    fi
    ;;
esac

if [ ! -e "/app/uploads" ]; then
  ln -s "$DATA_DIR/uploads" "/app/uploads"
fi

exec "$@"
