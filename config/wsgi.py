"""
WSGI config for tnpsc_affairs project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Read from env, fall back to production in wsgi context
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
