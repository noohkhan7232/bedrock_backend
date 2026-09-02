import os
from datetime import timedelta
from pathlib import Path

import environ
from kombu import Exchange, Queue


# ============================================================
# Helpers
# ============================================================

def ensure_trailing_slash(path: str) -> str:
  normalized_path = path.strip('/')
  return f'{normalized_path}/' if normalized_path else ''


def join_url(base_url: str, path: str) -> str:
  normalized_base_url = base_url.rstrip('/')
  normalized_path = path.lstrip('/')
  return f'{normalized_base_url}/{normalized_path}'


# ============================================================
# Paths and environment
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DJANGO_TEST = os.environ.get('DJANGO_TEST') == 'True'
ENV_FILE = 'env.test' if DJANGO_TEST else '.env'

environ.Env.read_env(BASE_DIR / ENV_FILE)
env = environ.Env()


# ============================================================
# Application
# ============================================================

APP_NAME = env.str('APP_NAME')
API_SERVER_URL = env.str('API_SERVER_URL')
CLIENT_URL = env.str('CLIENT_URL', default=API_SERVER_URL)


# ============================================================
# Django core
# ============================================================

# Do not rename `DEBUG`, which is used by django internals and
# third-party packages.
DEBUG = env.bool('DJANGO_DEBUG', default=False)
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# Hosts and CORS
# ============================================================

ALLOWED_HOSTS = env.tuple(
  'ALLOWED_HOSTS',
  default=('localhost', '0.0.0.0',),
)

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=False)
CORS_ORIGIN_WHITELIST = env.tuple(
  'CORS_ORIGIN_WHITELIST',
  default=(API_SERVER_URL, CLIENT_URL,),
)

CORS_ALLOW_HEADERS = [
  'content-disposition',
  'content-type',
  'x-xss-protection',
  'authorization',
]
CORS_EXPOSE_HEADERS = [
  'content-disposition',
]


# ============================================================
# Security
# ============================================================

IS_PRODUCTION = not DEBUG and not DJANGO_TEST

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

LANGUAGE_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION

SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = False


# ============================================================
# Installed apps and middleware
# ============================================================

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.postgres',
  'django_extensions',
  'corsheaders',
  'rest_framework',
  'rest_framework_simplejwt.token_blacklist',
  'django_celery_beat',
  'django_cleanup.apps.CleanupConfig',
  'drf_spectacular',
  'core.apps.CoreConfig',
  'api.apps.ApiConfig',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'api.middleware.TenantContextMiddleware',
]


# ============================================================
# Templates, static files, and media
# ============================================================

TEMPLATE_DIR = BASE_DIR.parent / env.str('DJANGO_TEMPLATE_DIR')
TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [TEMPLATE_DIR, BASE_DIR / 'templates'],
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
  BASE_DIR.parent / env.str('DJANGO_STATIC_DIR'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, env.str('MEDIA_ROOT'))
MEDIA_URL = env.str('MEDIA_URL')

STORAGES = {
  'default': {
    'BACKEND': 'django.core.files.storage.FileSystemStorage',
  },
  'staticfiles': {
    'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
  },
}


# ============================================================
# Database
# ============================================================

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': env.str('POSTGRES_DB'),
    'USER': env.str('POSTGRES_USER'),
    'PASSWORD': env.str('POSTGRES_PASSWORD'),
    'HOST': env.str('POSTGRES_HOST'),
    'PORT': env.int('POSTGRES_PORT'),
    'TEST': {
      'NAME': 'postgres_test',
    },
  },
}


# ============================================================
# Authentication
# ============================================================

AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = (
  'django.contrib.auth.backends.ModelBackend',
  'core.backends.CustomModelBackend',
  'core.backends.SSOBackend',
)

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': (
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'),
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


# ============================================================
# Django REST Framework and JWT
# ============================================================

REST_FRAMEWORK = {
  'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',
  ],
  'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
  ],
  'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
  ],
  'DEFAULT_THROTTLE_RATES': {
    'anon': env.str('DRF_THROTTLE_RATES_ANONYMOUS'),
    'user': env.str('DRF_THROTTLE_RATES_USER'),
  },
  'EXCEPTION_HANDLER': 'api.exception_handler.custom_exception_handler',
  'DEFAULT_PAGINATION_CLASS': 'api.paginations.DefaultPageNumberPagination',
  'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
  'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
  'ACCESS_TOKEN_LIFETIME': timedelta(
    minutes=env.int('ACCESS_TOKEN_LIFETIME_MINS'),
  ),
  'REFRESH_TOKEN_LIFETIME': timedelta(
    days=env.int('REFRESH_TOKEN_LIFETIME_DAYS'),
  ),
  'ALGORITHM': 'HS256',
  'AUTH_HEADER_TYPES': ('Bearer',),
  'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
  'USER_ID_FIELD': 'id',
  'UPDATE_LAST_LOGIN': env.bool('UPDATE_LAST_LOGIN'),
}


# ============================================================
# Email
# ============================================================

EMAIL_DRIVER = env.str('EMAIL_DRIVER')
EMAIL_BACKEND = env.str('EMAIL_BACKEND')
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
DEFAULT_FROM_EMAIL = env.str(
  'DEFAULT_FROM_EMAIL',
  default='noreply@example.local',
)

EMAIL_TEMPLATE_DIR = env.str('EMAIL_TEMPLATE_DIR')
EMAIL_ASSET_BASE_URL = ensure_trailing_slash(env.str('EMAIL_ASSET_BASE_URL'))


# ============================================================
# Celery
# ============================================================

CELERY_BROKER_URL = env.str(
  'CELERY_BROKER_URL',
  default='redis://localhost:6379/0',
)
CELERY_TASK_IGNORE_RESULT = env.bool(
  'CELERY_TASK_IGNORE_RESULT',
  default=True,
)
CELERY_TASK_STORE_ERRORS_EVEN_IF_IGNORED = env.bool(
  'CELERY_TASK_STORE_ERRORS_EVEN_IF_IGNORED',
  default=True,
)

if not CELERY_TASK_IGNORE_RESULT:
  CELERY_RESULT_BACKEND = env.str(
    'CELERY_RESULT_BACKEND',
    default='redis://localhost:6379/1',
  )

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = (
  Queue('default', Exchange('default'), routing_key='default'),
  Queue('llm', Exchange('llm'), routing_key='llm'),
)
CELERY_TASK_ROUTES = {
  'core.services.agent.tasks.*': {
    'queue': 'llm',
    'routing_key': 'llm',
  },
}
CELERY_IMPORTS = (
  'core.services.agent.tasks',
  'core.services.email.tasks',
)


# ============================================================
# Logging
# ============================================================

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'default': {
      'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    },
  },
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
      'level': 'INFO',
      'formatter': 'default',
      'stream': 'ext://sys.stdout',
    },
    'file': {
      'class': 'logging.FileHandler',
      'level': 'INFO',
      'formatter': 'default',
      'filename': env.str(
        'LOGGER_FILE_PATH',
        default='/var/log/bedrock/application.log',
      ),
    },
  },
  'loggers': {
    '': {
      'handlers': env.list('LOGGER_HANDLERS', default=['file']),
      'level': env.str('LOGGER_LEVEL', default='INFO'),
      'propagate': False,
    },
    'django': {
      'handlers': env.list('LOGGER_HANDLERS', default=['file']),
      'level': env.str('LOGGER_LEVEL', default='INFO'),
      'propagate': False,
    },
  },
}


# ============================================================
# Admin
# ============================================================

DJANGO_ADMIN_SITE_ENABLED = env.bool(
  'DJANGO_ADMIN_SITE_ENABLED',
  default=False,
)
DJANGO_ADMIN_URL = ensure_trailing_slash(
  env.str('DJANGO_ADMIN_URL', 'division-2/devoffice/'),
)


# ============================================================
# API documentation
# ============================================================

API_DOC_LOGIN_URL = ensure_trailing_slash(env.str('API_DOC_LOGIN_URL'))
LOGIN_URL = f'/{API_DOC_LOGIN_URL}login/'

INTERNAL_API_DOC_ENABLED = env.bool(
  'INTERNAL_API_DOC_ENABLED',
  default=False,
)
INTERNAL_API_DOC_URL = ensure_trailing_slash(env.str('INTERNAL_API_DOC_URL'))
INTERNAL_API_DOWNLOAD_URL = ensure_trailing_slash(
  env.str('INTERNAL_API_DOWNLOAD_URL'),
)

EXTERNAL_API_DOC_ENABLED = env.bool(
  'EXTERNAL_API_DOC_ENABLED',
  default=False,
)
EXTERNAL_API_DOC_URL = ensure_trailing_slash(
  env.str('EXTERNAL_API_DOC_URL'),
)
EXTERNAL_API_DOWNLOAD_URL = ensure_trailing_slash(
  env.str('EXTERNAL_API_DOWNLOAD_URL'),
)


# ============================================================
# Application domain settings
# ============================================================

EMAIL_VERIFICATION_CODE_LENGTH = env.int(
  'EMAIL_VERIFICATION_CODE_LENGTH',
)
EMAIL_VERIFICATION_CODE_LIFETIME_HOURS = env.int(
  'EMAIL_VERIFICATION_CODE_LIFETIME_HOURS',
)

TENANT_DOMAIN_LENGTH = env.int(
  'TENANT_DOMAIN_LENGTH',
)
TENANT_ACCOUNT_ID_LENGTH = env.int(
  'TENANT_ACCOUNT_ID_LENGTH',
)

TENANT_INVITATION_CODE_LENGTH = env.int(
  'TENANT_INVITATION_CODE_LENGTH',
)
TENANT_INVITATION_CODE_LIFETIME_HOURS = env.int(
  'TENANT_INVITATION_CODE_LIFETIME_HOURS',
)
TENANT_INVITATION_CODE_REQUEST_MAX_SIZE = env.int(
  'TENANT_INVITATION_CODE_REQUEST_MAX_SIZE',
)

PASSWORD_RESET_CODE_LENGTH = env.int(
  'PASSWORD_RESET_CODE_LENGTH',
)
PASSWORD_RESET_CODE_LIFETIME_HOURS = env.int(
  'PASSWORD_RESET_CODE_LIFETIME_HOURS',
)

FAILED_LOGIN_ATTEMPT_MAX_COUNT = env.int(
  'FAILED_LOGIN_ATTEMPT_MAX_COUNT',
)
LOGIN_LOCK_PERIOD_MINS = env.int(
  'LOGIN_LOCK_PERIOD_MINS',
)


# ============================================================
# External services
# ============================================================

GOOGLE_SERVICE_ACCOUNT_PATH = env.str(
  'GOOGLE_SERVICE_ACCOUNT_PATH',
  default='',
)

OPENAI_API_KEY = env.str('OPENAI_API_KEY', default='')


# ============================================================
# SSO
# ============================================================

SSO_ENABLED = env.bool('SSO_ENABLED', default=False)

SSO_WORKOS_API_KEY = env.str('SSO_WORKOS_API_KEY') if SSO_ENABLED else ''
SSO_WORKOS_CLIENT_ID = env.str('SSO_WORKOS_CLIENT_ID') if SSO_ENABLED else ''
SSO_REDIRECT_URI = (
  join_url(CLIENT_URL, env.str('SSO_REDIRECT_PATH')) if SSO_ENABLED else ''
)

