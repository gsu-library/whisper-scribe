#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

PYTHON_EXEC=""

# Find Python version
if command -v python3 &> /dev/null; then
   PYTHON_EXEC="python3"
elif command -v python &> /dev/null; then
   PYTHON_EXEC="python"
fi

# If Python was not found
if [ -z "$PYTHON_EXEC" ]; then
   echo "ERROR: Could not find 'python3' or 'python' executable in PATH." >&2
   echo "Please ensure Python is installed and in your system's PATH, or a virtual environment is activated." >&2
   exit 1
fi

echo "Starting WhisperScribe update process."
echo "Using Python executable: $PYTHON_EXEC"

echo "Installing/updating Python dependencies from requirements-freeze.txt..."
# We use '$PYTHON_EXEC -m pip' to ensure the correct pip is used.
$PYTHON_EXEC -m pip install -r requirements-freeze.txt
echo "Dependencies installed successfully."

echo "Applying database migrations..."
$PYTHON_EXEC manage.py migrate
echo "Database migrations applied successfully."

echo "Collecting static files..."
$PYTHON_EXEC manage.py collectstatic --noinput
echo "Static files collected successfully."

echo "WhisperScribe update complete."
