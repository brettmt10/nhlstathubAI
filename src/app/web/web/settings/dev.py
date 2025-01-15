from web.settings.base import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME_DEV'),
        'USER': os.getenv('DB_USER_DEV'),
        'PASSWORD': os.getenv('DB_PASSWORD_DEV'),
        'HOST': os.getenv('DB_HOST_DEV'),
        'PORT': os.getenv('DB_PORT_DEV'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True