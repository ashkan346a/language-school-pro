"""
Aether Language Institute — Professional Space-Themed Language Platform
Django settings (env-driven, Railway + Whitenoise ready)
"""

from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SECURITY & ENVIRONMENT
# =============================================================================
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver,.railway.app,language-school-pro-production.up.railway.app', cast=Csv())

# SECRET_KEY handling with automatic generation for convenience.
# In production (DEBUG=False) if not provided, we generate one and raise with the value
# so you can copy-paste it directly into your Railway Variables dashboard.
_raw_secret = config('SECRET_KEY', default=None)
if _raw_secret:
    SECRET_KEY = _raw_secret
else:
    if DEBUG:
        # Safe dev fallback (never use in real production)
        SECRET_KEY = 'django-insecure-dev-aether-2026-persian-premium-space-xyz9876543210'
    else:
        from django.core.management.utils import get_random_secret_key
        generated = get_random_secret_key()
        raise ValueError(
            "SECRET_KEY is required in production.\n"
            "Copy the following value into your Railway project Variables as SECRET_KEY "
            "and redeploy:\n\n"
            f"{generated}\n"
        )


# =============================================================================
# APPLICATIONS
# =============================================================================
INSTALLED_APPS = [
    # Admin (modern dark feel can be extended)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Local apps (namespaced under apps/)
    'apps.core',
    'apps.accounts',
    'apps.catalog',
    'apps.learning',
    'apps.payments',
]


# =============================================================================
# MIDDLEWARE (Whitenoise for static in prod, security)
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # After security, before others
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'

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
                'apps.core.context_processors.site_settings',  # global defensive site settings
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# =============================================================================
# DATABASE (SQLite for now per request; easy Postgres via DATABASE_URL)
# =============================================================================
if config('DATABASE_URL', default=None):
    # e.g. postgres://... on Railway
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =============================================================================
# AUTH
# =============================================================================
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'  # Will point to dashboard once implemented
LOGOUT_REDIRECT_URL = 'home'


# =============================================================================
# PRODUCTION SECURITY (only enforce when DEBUG=False / HTTPS)
# =============================================================================
if not DEBUG:
    # Trust Railway's proxy for HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS - start conservative (can increase after testing)
    SECURE_HSTS_SECONDS = 3600  # 1 hour; increase to 31536000 (1 year) once stable
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Additional
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# I18N / TIME  — Full Persian experience (RTL + fa locale). Hardcoded Persian UI.
# =============================================================================
LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# Add LocaleMiddleware for future if we extract .po, but current site is fully Persian hardcoded
# MIDDLEWARE will get it below if needed. For now explicit Persian strings in templates.


# =============================================================================
# STATIC & MEDIA (Whitenoise + Railway friendly)
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure the staticfiles directory exists at startup (prevents whitenoise
# "No directory at: /app/staticfiles/" warning on Railway when release phase
# hasn't run collectstatic yet or on fresh containers).
import os
os.makedirs(STATIC_ROOT, exist_ok=True)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# STRIPE (real integration, keys via env)
# =============================================================================
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')


# =============================================================================
# DEFAULTS
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# EMAIL (console for dev; override in prod via env)
# =============================================================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='missions@aether.example')
