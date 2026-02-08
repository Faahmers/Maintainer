#!/bin/bash
set -e

echo "Installing repo dependencies if present"

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Running agent"
python agent.py repo || true

echo "Docker execution finished"