from .base import *
from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')



SECRET_KEY = os.getenv('SECRET_KEY')

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    # 'HOST': 'localhost',
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
  'password_tries': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'password_tries_cache_table',
  },
  'email_verification': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'email_verification_cache_table',
    },
}


STATIC_URL = 'static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = '/app/staticfiles'

MEDIA_URL = 'media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIA_ROOT = '/app/mediafiles'

# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')