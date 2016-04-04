web: gunicorn config.wsgi:application
worker: celery worker --app=velo.taskapp --loglevel=info
