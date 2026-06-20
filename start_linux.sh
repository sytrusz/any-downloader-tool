#!/bin/bash
echo "Starting Any Downloader Tool..."

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed! Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv and install requirements
source .venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo "Launching Web App..."
python3 main.py
