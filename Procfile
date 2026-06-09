web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file - --preload
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
