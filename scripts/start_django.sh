#!/bin/sh
set -e

python /app/scripts/wait_for_mysql.py
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:${PORT:-8000}
