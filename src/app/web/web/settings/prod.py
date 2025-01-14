# settings/production.py
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME_PROD'),
        'USER': os.getenv('DB_USER_PROD'),
        'PASSWORD': os.getenv('DB_PASSWORD_PROD'),
        'HOST': os.getenv('DB_HOST_PROD'),
        'PORT': os.getenv('DB_PORT_PROD'),
    }
}

DEBUG = False
# Add other production-specific settings