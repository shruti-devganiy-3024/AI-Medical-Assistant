import os
from pathlib import Path
import dj_database_url
from decouple import config

# ===========================================================
# BASE DIRECTORY
# ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================================
# SECURITY
# ===========================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# ===========================================================
# GEMINI AI CONFIGURATION
# ===========================================================
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set in .env file!")

# ===========================================================
# INSTALLED APPS
# ===========================================================
INSTALLED_APPS = [
    # Built-in Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',

    'accounts',
    'chatbot',
    'appointments',
    'frontend',
]

# ===========================================================
# MIDDLEWARE
# ===========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # for static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================================================
# URL & WSGI
# ===========================================================
ROOT_URLCONF = 'medical_assistant.urls'
WSGI_APPLICATION = 'medical_assistant.wsgi.application'

# ===========================================================
# TEMPLATES
# ===========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ===========================================================
# DATABASE
# Locally: uses SQLite (simple file-based DB)
# On Render: uses PostgreSQL via DATABASE_URL env variable
# ===========================================================
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600,
    )
}

# ===========================================================
# DJANGO REST FRAMEWORK
# ===========================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# ===========================================================
# PASSWORD VALIDATION
# ===========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================================================
# INTERNATIONALIZATION
# ===========================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================================================
# STATIC FILES (CSS, JS, Images)
# ===========================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================================================
# DEFAULT PRIMARY KEY
# ===========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'