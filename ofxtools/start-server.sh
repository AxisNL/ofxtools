#!/bin/bash
cd /app

echo "Starting manage.py migrate"
/app/venv/bin/python /app/manage.py makemigrations --no-input
/app/venv/bin/python /app/manage.py migrate --no-input
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (/app/venv/bin/python manage.py createsuperuser --no-input)
fi
chown -R www-data /app/db
chown -R www-data /app/log
/app/venv/bin/python /app/manage.py collectstatic --no-input
echo "Starting gunicorn"
#(/app/venv/bin/gunicorn app.wsgi --user www-data --bind 0.0.0.0:8001 --workers 5 --timeout 1200 --capture-output --log-level debug --access-logfile /app/log/gunicorn_access.log --error-logfile /app/log/gunicorn_error.log ) &
(/app/venv/bin/gunicorn app.wsgi) &
echo "Starting nginx"
nginx -g "daemon off;"

