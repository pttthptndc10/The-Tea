"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
app = application

# Auto apply database migrations & initial admin creation on cold start
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('create_initial_admin')
except Exception as e:
    print(f"[WSGI] Migration notice: {e}")


