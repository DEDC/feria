"""
Django settings for feria project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=list)


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'debug_toolbar',
    'apps.users',
    'apps.places',
    'apps.dates',
    'apps.admin',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware"
]

ROOT_URLCONF = 'feria.urls'

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

WSGI_APPLICATION = 'feria.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT', cast=int)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (BASE_DIR / 'static',)
MEDIA_URL = '/storage/'
MEDIA_ROOT = BASE_DIR / 'storage'
FILE_STRUCTURE_ROOT = BASE_DIR

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.Usuarios'
AUTHENTICATION_BACKENDS = ["apps.users.customlogin.EmailAuthBackend"]

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

CSRF_COOKIE_NAME = 'XSRF-TOKEN'
CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'

INTERNAL_IPS = [
    "127.0.0.1",
]

START_DATES  = '2025/3/4'
END_DATES = '2025/3/14'
START_HOURS = '9:00'
END_HOURS = '17:40'
PERIODS_TIME = '40min'
LIMIT_PLACES = 3
ATTENTION_MODULES = 6
LIMIT_ALL_PLACES = 900

URL_CURP = config('URL_CURP')
TOKEN_CURP = config('TOKEN_CURP')

# TPAY Config
TPAY_RUTA = config('TPAY_RUTA')
TPAY_SOCKET = config('TPAY_SOCKET')
TPAY_APIKEY = config('TPAY_APIKEY')
TPAY_SISTEMA = config('TPAY_SISTEMA')
TPAY_PROJECT_ID = config('TPAY_PROJECT_ID')
TPAY_SESSION_ABORDAJE = config('TPAY_SESSION_ABORDAJE')
TPAY_SESSION_ACCESS = config('TPAY_SESSION_ACCESS')
TPAY_CAPTURA = config('TPAY_CAPTURA')
TPAY_PROJECT = config('TPAY_PROJECT')
TPAY_CHANNEL_SERVICE = config('TPAY_CHANNEL_SERVICE')
TPAY_CHANNEL_INFO = config('TPAY_CHANNEL_INFO')
TPAY_CHANNEL_GESTOR = config('TPAY_CHANNEL_GESTOR')

kEYAES=config("AESKEY")
IVAES=config("AESIV")

# Configuración de correo en Django (settings.py)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_SMTP')  # Cambia esto por tu proveedor SMTP (ej: smtp.gmail.com, smtp.office365.com)
EMAIL_PORT = config('EMAIL_PORT')  # 465 para SSL, 587 para TLS
EMAIL_USE_TLS = True  # Usa TLS (seguro)
EMAIL_USE_SSL = False  # Usa SSL (poner en True si usas el puerto 465)
EMAIL_HOST_USER = config('EMAIL_USER')  # Tu correo
EMAIL_HOST_PASSWORD = config('EMAIL_PASS')  # Tu contraseña (usa variables de entorno para más seguridad)
DEFAULT_FROM_EMAIL = config('EMAIL_USER')  # Nombre que aparecerá en los correos enviados

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Mantener los loggers existentes
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',  # Nivel de log deseado
            'class': 'logging.FileHandler',
            # Puedes ajustar la ruta de archivo según permisos o conveniencia
            'filename': os.path.join(BASE_DIR, 'logs', 'django_app.log'),
            'formatter': 'verbose',
        },
        # Handler para imprimir en consola
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # Puedes agregar otros handlers (por ejemplo, para enviar mails a admin)
    },
    'loggers': {
        # Logger para la aplicación Django (se puede crear uno propio para cada módulo)
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        # Logger personalizado para nuestra aplicación (opcional)
        'dates': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
