import os
from django.core.wsgi import get_wsgi_application
from django.db import connection
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lostfound.settings')
application = get_wsgi_application()

# Attempt a lightweight auto-migrate on startup if core tables are missing.
# This is safe to run; migrations are idempotent and will no-op when applied.
try:
	with connection.cursor() as cursor:
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('items_message','items_lostitem')")
		rows = cursor.fetchall()
	existing = {r[0] for r in rows}
	if 'items_message' not in existing or 'items_lostitem' not in existing:
		call_command('migrate', interactive=False, run_syncdb=True)
except Exception:
	# If database isn't ready or using a different engine, ignore silently.
	pass
