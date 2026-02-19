"""
WSGI config for cctv_pontianak project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cctv_pontianak.settings')

application = get_wsgi_application()
