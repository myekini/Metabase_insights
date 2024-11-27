#!/bin/bash

LOG_FILE="setup_instance.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Exit immediately if a command exits with a non-zero status
set -e

echo "[$(date)] Starting instance setup for Metabase..."

# Update and install required packages
echo "[$(date)] Updating system and installing required packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose curl

# Start Docker service
echo "[$(date)] Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to the Docker group
echo "[$(date)] Adding user to Docker group..."
sudo usermod -aG docker $USER

# Install AWS CLI
echo "[$(date)] Installing AWS CLI..."
sudo apt install -y awscli

# Confirm installation
echo "[$(date)] Confirming installations..."
docker --version
docker-compose --version
aws --version

echo "[$(date)] Instance setup complete. Please log out and log back in to apply Docker group changes."
