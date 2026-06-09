web: gunicorn config.wsgi:application --log-file - --preload
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
