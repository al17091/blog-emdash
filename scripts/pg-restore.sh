#!/bin/bash
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is required."
  echo "Usage: DATABASE_URL=postgres://user:pass@host/db ./scripts/pg-restore.sh < dump.sql"
  exit 1
fi

psql "$DATABASE_URL"
