#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

echo "Running Collectstatic..."
python manage.py collectstatic --no-input

echo "Build Process Completed!"
