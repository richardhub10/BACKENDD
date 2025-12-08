#!/usr/bin/env bash
set -euo pipefail

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and collect static assets
python manage.py migrate
python manage.py collectstatic --noinput
echo "Skipping build-time createsuperuser; will set/reset on startup via ItemsConfig.ready()"
echo "Force-setting admin password via management command"
python manage.py set_admin_password

# Ensure media directory exists on persistent disk if configured
if [ -n "${MEDIA_ROOT:-}" ]; then
	mkdir -p "$MEDIA_ROOT"
	echo "Ensured MEDIA_ROOT directory exists: $MEDIA_ROOT"
fi
