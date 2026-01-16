#!/bin/bash

set -e

echo "Deploying Fresha Email Automation..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
mkdir -p logs db backups

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "Warning: config/.env not found. Please create it from config/.env.example"
fi

# Initialize database
echo "Initializing database..."
python -m src.cli init

# Run health check
echo "Running health check..."
python -m src.cli health || echo "Health check failed, but continuing..."

echo "Deployment complete!"
echo "To start the scheduler, run: python -m src.main"
