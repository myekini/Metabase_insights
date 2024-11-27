#!/bin/bash

LOG_FILE="start_metabase.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Exit immediately if a command exits with a non-zero status
set -e

if [ -z "$1" ]; then
    echo "[$(date)] ERROR: Environment not specified. Usage: ./start_metabase.sh <staging|production>"
    exit 1
fi

ENV=$1
COMPOSE_FILE="config/$ENV/docker-compose.${ENV}.yml"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "[$(date)] ERROR: Docker Compose file for $ENV environment not found at $COMPOSE_FILE"
    exit 1
fi

echo "[$(date)] Starting Metabase services for $ENV environment..."
docker-compose -f "$COMPOSE_FILE" up -d
echo "[$(date)] Metabase services started successfully for $ENV environment."
