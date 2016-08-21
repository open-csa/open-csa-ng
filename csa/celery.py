import os

from celery import Celery
import django

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'csa.settings')

from django.conf import settings  # noqa

app = Celery()
django.setup()

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
