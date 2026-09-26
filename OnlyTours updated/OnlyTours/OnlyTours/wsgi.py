"""
WSGI config for OnlyTours project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlyTours.settings')

application = get_wsgi_application()
