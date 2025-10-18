import os
from celery import Celery

# Define o settings do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

app = Celery('setup')

# Lê configurações do Django com prefixo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tasks.py nos apps
app.autodiscover_tasks()
