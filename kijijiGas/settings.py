import os
from pathlib import Path
from decouple import config
import dj_database_url
import sys

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# Security
# ----------------------------
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['*']  # adjust for production

# ----------------------------
# Installed apps
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'suppliers',
    'customer',
    'widget_tweaks',
]

# ----------------------------
# Middleware
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----------------------------
# URLs and Templates
# ----------------------------
ROOT_URLCONF = 'kijijiGas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'suppliers.context_processors.unread_orders_count',
                'suppliers.context_processors.supplier_info',
                'suppliers.context_processors.unread_messages_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'kijijiGas.wsgi.application'

# ----------------------------
# Database
# ----------------------------
db_url = config('DATABASE_URL', default='sqlite:///db.sqlite3')

if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
    db_url = config('DIRECT_URL', default=db_url)

db_config = dj_database_url.parse(db_url, conn_max_age=600)

# Only PostgreSQL needs sslmode
if db_config['ENGINE'] == 'django.db.backends.postgresql':
    db_config['OPTIONS'] = {'sslmode': 'require'}

DATABASES = {
    'default': db_config
}

# ----------------------------
# Password validation
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# Internationalization
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------
# Static & Media Files
# ----------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Enable WhiteNoise compressed storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------------
# Default primary key
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------
# MPESA Settings
# ----------------------------
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='')
MPESA_PASSKEY = config('MPESA_PASSKEY', default='')
MPESA_CALLBACK_URL = config('MPESA_CALLBACK_URL', default='')

CSRF_TRUSTED_ORIGINS = [
    'https://kijijigas-production.up.railway.app',
    'https://kijijigas.com',
    'https://kijiji-gas.vercel.app'
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

import os

if os.getenv("DISABLE_COLLECTSTATIC") == "1":
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"