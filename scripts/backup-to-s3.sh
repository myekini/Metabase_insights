#!/bin/bash

# Configuration
BACKUP_DIR="/var/metabase-backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
S3_BUCKET_NAME="${BACKUP_BUCKET_NAME}"  # Ensure this environment variable is set
BACKUP_FILE="metabase-backup-${TIMESTAMP}.tar.gz"
LOG_FILE="/var/log/metabase-backup.log"

# Check if AWS CLI is installed
if ! command -v aws &>/dev/null; then
    echo "Error: AWS CLI is not installed. Please install it before running this script." | tee -a "$LOG_FILE"
    exit 1
fi

# Function: Create backup
create_backup() {
    echo "[$(date)] Starting backup process..." | tee -a "$LOG_FILE"

    # Ensure the backup directory exists
    if [ ! -d "$BACKUP_DIR" ]; then
        echo "Backup directory $BACKUP_DIR does not exist. Creating it..." | tee -a "$LOG_FILE"
        mkdir -p "$BACKUP_DIR"
    fi

    # Create a tar.gz file from the backup directory
    echo "[$(date)] Creating compressed backup file..." | tee -a "$LOG_FILE"
    tar -czf "/tmp/${BACKUP_FILE}" -C "$BACKUP_DIR" .

    if [ $? -ne 0 ]; then
        echo "Error: Failed to create backup file." | tee -a "$LOG_FILE"
        exit 1
    fi
}

# Function: Upload to S3
upload_to_s3() {
    echo "[$(date)] Uploading backup to S3 bucket: $S3_BUCKET_NAME" | tee -a "$LOG_FILE"
    aws s3 cp "/tmp/${BACKUP_FILE}" "s3://${S3_BUCKET_NAME}/backups/${BACKUP_FILE}"

    if [ $? -eq 0 ]; then
        echo "[$(date)] Backup successfully uploaded to S3." | tee -a "$LOG_FILE"
    else
        echo "Error: Failed to upload backup to S3." | tee -a "$LOG_FILE"
        exit 1
    fi

    # Clean up local backup file
    echo "[$(date)] Cleaning up local temporary backup file..." | tee -a "$LOG_FILE"
    rm -f "/tmp/${BACKUP_FILE}"
}

# Function: Schedule Backup
schedule_backup() {
    CRON_JOB="0 0 * * * /bin/bash $0"
    crontab -l | grep -F "$CRON_JOB" &>/dev/null

    if [ $? -ne 0 ]; then
        echo "[$(date)] Setting up cron job for daily backups..." | tee -a "$LOG_FILE"
        (crontab -l 2>/dev/null; echo "$CRON_JOB >> $LOG_FILE 2>&1") | crontab -
        echo "[$(date)] Cron job added successfully." | tee -a "$LOG_FILE"
    else
        echo "[$(date)] Cron job already exists. No changes made." | tee -a "$LOG_FILE"
    fi
}

# Main Execution
if [ -z "$S3_BUCKET_NAME" ]; then
    echo "Error: BACKUP_BUCKET_NAME environment variable is not set." | tee -a "$LOG_FILE"
    exit 1
fi

create_backup
upload_to_s3
schedule_backup

echo "[$(date)] Backup process completed successfully." | tee -a "$LOG_FILE"
