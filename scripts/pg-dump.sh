#!/bin/bash
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is required."
  echo "Usage: DATABASE_URL=postgres://user:pass@host/db ./scripts/pg-dump.sh > dump.sql"
  exit 1
fi

# --clean: Drop tables before recreating them
# --if-exists: Use IF EXISTS when dropping objects
# --no-owner: Skip restoring ownership to the original user
# --no-privileges: Skip restoring access privileges
pg_dump "$DATABASE_URL" --clean --if-exists --no-owner --no-privileges
