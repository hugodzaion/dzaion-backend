import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "harlee-toxophilitic-marita.ngrok-free.dev",
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-Party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_api_key',
    'drf_spectacular',
    "corsheaders",
    'viewflow',
    # 'dzaion',
    # Components Apps
    'locations',
    'contacts',
    'core',
    'accounts',
    'activities.apps.ActivitiesConfig',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'setup.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
AUTH_USER_MODEL = 'accounts.User'
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
AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend',
    'accounts.authentication.backends.EmailOrWhatsAppBackend',
]

# Internationalization
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

#media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cors Allowed
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5173'
]

# Simple JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Sites Framework
SITE_ID = 1

# Redis como broker
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'

# LOGGING DE ERROS
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {  # log no terminal
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/info.log'),
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'dzaion_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/dzaion.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'finance_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/finance.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'user_activity_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/user_activity.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'dispather_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/dispathery.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'error_file', 'info_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'myapp': {
            'handlers': ['console', 'error_file', 'info_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'dzaion': {
            'handlers': ['console', 'dzaion_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'finance_log': {
            'handlers': ['console', 'finance_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'user_activity_log': {
            'handlers': ['console', 'user_activity_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'dispather_log': {
            'handlers': ['console', 'dispather_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# CONFIGURAÇÃO DE E-MAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.dzaion.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@dzaion.com' 
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'Dzaion <noreply@dzaion.com>'

# Chave API da OpenAI
OPENAI_API_KEY = config('OPENAI_API_KEY')

# Serviço de Mensagem Whatsapp
MESSAGING_PROVIDER = 'whatsgw'

# Documentação
SPECTACULAR_SETTINGS = {
    'TITLE': 'Dzaion Web API',
    'DESCRIPTION': 'A Plataforma de Experiência de Vida (Life Experience Platform) para unificar e simplificar interações digitais.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
