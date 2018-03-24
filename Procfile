release: python manage.py migrate
python manage.py collectstatic --noinput;
web: gunicorn dashboard.wsgi --log-file -
