#!/bin/sh
set -e

if [ "${INIT_DB:-false}" = "true" ]; then
    python -c "from Beatify.models import app, db; ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
fi

if [ "${POPULATE_DB:-false}" = "true" ]; then
    # Seed only when there is no artist data yet, so restarts do not fail on unique constraints.
    if python -c "from Beatify.models import app, Artist; ctx = app.app_context(); ctx.push(); import sys; sys.exit(0 if Artist.query.count() == 0 else 1)"; then
        python Database_folder/populate_DB.py
    fi
fi

# Start the API directly to avoid container start failure if supervisor runtime deps are missing.
exec gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 60 Beatify.wsgi:app
