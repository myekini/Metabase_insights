#!/bin/bash

LOG_FILE="migrate_database.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Exit immediately if a command exits with a non-zero status
set -e

POSTGRES_CONTAINER="postgres-staging"
DB_NAME="metabase_staging"
DB_USER="metabase_stg"
SCHEMA_FILE="data/schema/metabase_schema.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "[$(date)] ERROR: Schema file not found at $SCHEMA_FILE"
    exit 1
fi

echo "[$(date)] Starting database migration for $DB_NAME..."

# Apply the schema changes
echo "[$(date)] Applying schema changes from $SCHEMA_FILE..."
docker exec -i "$POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SCHEMA_FILE"
echo "[$(date)] Database migration completed successfully."

echo "[$(date)] Migration process completed."
