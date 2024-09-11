#!/bin/bash

# Check for processes using port 8000 and terminate them
echo "Checking for processes using port 8000..."
PORT_PROCESS=$(lsof -ti :8000)
if [ -n "$PORT_PROCESS" ]; then
    echo "Terminating process $PORT_PROCESS using port 8000..."
    kill -9 $PORT_PROCESS || { echo "Failed to terminate the process using port 8000!"; exit 1; }
else
    echo "No process is using port 8000."
fi

# Navigate to the flask_api directory
echo "Navigating to the flask_api directory..."
cd flask_api || { echo "Directory not found!"; exit 1; }

# List contents to confirm the correct directory
ls

# Pull the latest changes from the main branch
echo "Pulling latest changes..."
git pull origin main

# Activate the virtual environment outside the screen session for installations
echo "Activating the virtual environment..."
source venv/bin/activate || { echo "Failed to activate virtual environment!"; exit 1; }

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || { echo "Failed to install dependencies!"; exit 1; }

# Check for existing screen session and terminate it
SESSION_ID=$(screen -ls | grep flask | awk '{print $1}')
if [ -n "$SESSION_ID" ]; then
    echo "Terminating existing screen session $SESSION_ID"
    screen -S "$SESSION_ID" -X quit
else
    echo "No existing screen session found."
fi

# Create a new screen session, activate the virtual environment, and start Gunicorn
echo "Starting a new screen session and running Gunicorn..."
screen -dmS flask bash -c 'source venv/bin/activate && gunicorn -c gunicorn.conf.py app:app'

echo "Deployment completed!"