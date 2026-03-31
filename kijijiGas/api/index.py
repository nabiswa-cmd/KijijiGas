import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kijijiGas.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()