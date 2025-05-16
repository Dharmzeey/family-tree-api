#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec gunicorn --bind 0.0.0.0:8000 --workers 3 family_tree.wsgi:application