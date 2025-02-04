from .base import *
from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",   
]

SECRET_KEY = os.getenv('SECRET_KEY')

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    'PORT': '',
  }
}

CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'family_tree_cache_table',
    },
  'password_reset': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'password_reset_cache_table',
  },
  'email_verification': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'email_verification_cache_table',
    },
}


STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
