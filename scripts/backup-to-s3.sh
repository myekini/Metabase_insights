#!/bin/bash

LOG_FILE="backup_s3.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Exit immediately if a command exits with a non-zero status
set -e

BACKUP_DIR="data/backups"
S3_BUCKET="your-s3-bucket-name"
POSTGRES_CONTAINER="postgres-production"
DB_NAME="metabase_production"
DB_USER="metabase_prod"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

echo "[$(date)] Starting backup process..."

# Create backup directory if it doesn't exist
echo "[$(date)] Ensuring backup directory exists at $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"

# Dump the PostgreSQL database
echo "[$(date)] Backing up PostgreSQL database $DB_NAME..."
docker exec "$POSTGRES_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.sql"
echo "[$(date)] PostgreSQL backup completed."

# Archive the Docker volume
echo "[$(date)] Archiving Metabase data volume..."
tar -czf "$BACKUP_DIR/metabase_data_backup_$TIMESTAMP.tar.gz" -C /var/lib/docker/volumes metabase-data/_data
echo "[$(date)] Metabase data volume archived."

# Upload backups to S3
echo "[$(date)] Uploading backups to S3 bucket $S3_BUCKET..."
aws s3 cp "$BACKUP_DIR" "s3://$S3_BUCKET/$TIMESTAMP/" --recursive
echo "[$(date)] Backup uploaded to S3 successfully."

echo "[$(date)] Backup process completed."
