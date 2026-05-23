#!/bin/bash
# Script to easily start J.A.R.V.I.S. with the correct virtual environment

echo "Starting J.A.R.V.I.S. in virtual environment..."

# Check if envjarvis exists
if [ -d "envjarvis" ]; then
    source envjarvis/bin/activate
    python run.py
else
    echo "Virtual environment 'envjarvis' not found. Running with system python..."
    python3 run.py
fi
