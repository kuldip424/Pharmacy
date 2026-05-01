#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Running Migrations ---"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "--- Starting Gunicorn ---"
gunicorn pharmacy.wsgi --log-file -
