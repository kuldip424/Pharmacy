#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

echo "Running Collectstatic..."
python manage.py collectstatic --no-input

echo "Checking Migration Status..."
python manage.py showmigrations

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Build Process Completed!"
