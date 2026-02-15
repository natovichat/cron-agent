#!/bin/bash
# Wrapper script to run cron_agent.py with environment variables

# Change to script directory
cd "$(dirname "$0")"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the Python script using virtual environment
./venv/bin/python3 cron_agent.py
