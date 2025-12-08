from pathlib import Path
import os
import dj_database_url  # Parse DATABASE_URL for production

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-me")
# Render sets environment variables; default DEBUG True for local development
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

# Allow hosts from env (comma separated). Fallback to local development hosts.
_allowed = os.getenv("ALLOWED_HOSTS")
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Render provides RENDER_EXTERNAL_URL for the deployed service; include automatically.
render_external = os.getenv("RENDER_EXTERNAL_URL")
if render_external:
    host = render_external.replace("https://", "").replace("http://", "")
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Allow any *.onrender.com host in production to avoid invalid Host header 400s
if ".onrender.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".onrender.com")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'items.apps.ItemsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lostfound.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'lostfound.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use DATABASE_URL if provided (e.g. from Render Postgres). ssl_require ensures encrypted connection.
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
# Prefer environment-provided media root (e.g., persistent disk on Render)
_media_root_env = os.getenv('MEDIA_ROOT')
if _media_root_env:
    MEDIA_ROOT = Path(_media_root_env)
else:
    # Default to project media folder in development
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Allow cross-origin requests from the app. If your frontend runs on a different
# origin and you want browser cookies (sessionid) to be sent, enable credentials
# on the CORS configuration and ensure the client uses fetch(..., {credentials: 'include'}).
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Extra security settings when not in DEBUG
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # For cross-site cookie support in production, set SameSite=None on session cookie
    SESSION_COOKIE_SAMESITE = 'None'
    # Trust Render hostnames for CSRF
    csrf_origins = []
    if render_external:
        csrf_origins.append(render_external)
    csrf_origins.append("https://*.onrender.com")
    CSRF_TRUSTED_ORIGINS = csrf_origins
else:
    # During local development keep cookies lax so the browser accepts them over HTTP
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    # CSRF trusted origins
    if render_external:
        CSRF_TRUSTED_ORIGINS = [render_external]
    # Prevent content sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
