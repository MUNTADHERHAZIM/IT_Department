"""
WSGI config for kunuz_tickets project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kunuz_tickets.settings')

application = get_wsgi_application()
