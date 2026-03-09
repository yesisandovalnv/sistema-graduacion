#!/bin/sh
set -e

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
  sleep 1
done

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
