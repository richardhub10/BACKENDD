#!/usr/bin/env bash
set -euo pipefail

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and collect static assets
python manage.py migrate
python manage.py collectstatic --noinput

# Create a superuser if env vars are present; don't fail if it already exists
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  echo "Creating Django superuser non-interactively (will be ignored if exists)..."
  python manage.py createsuperuser --noinput || true
else
  echo "Skipping createsuperuser: missing DJANGO_SUPERUSER_* env vars"
fi
