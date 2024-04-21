#!/bin/sh

# Start Celery worker
celery -A ecom worker --detach

# Start Gunicorn server with 3 workers
exec gunicorn ecom.wsgi:application --bind 0.0.0.0:8000 --workers 3
