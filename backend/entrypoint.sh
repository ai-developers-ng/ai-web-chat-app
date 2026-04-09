#!/bin/bash
set -e

echo "→ Initializing database..."
python init_db.py

echo "→ Starting gunicorn (gevent workers, SSE-ready)..."
exec gunicorn \
  --bind 0.0.0.0:5001 \
  --workers 2 \
  --worker-class gevent \
  --timeout 300 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  app:app
