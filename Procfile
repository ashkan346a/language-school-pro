web: python manage.py collectstatic --noinput --clear && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file - --preload
release: python manage.py migrate --noinput
