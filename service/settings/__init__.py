import os
from datetime import timedelta
from pathlib import Path

APPLICATION_STAGE = os.environ.get("APPLICATION_STAGE", "development")
APPLICATION_NAME = 'CONFIRMIFY'
APPLICATION_SHORT_NAME = 'CNFRM'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'user.apps.UserConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'service.urls'

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

WSGI_APPLICATION = 'service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

APPEND_SLASH = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


"""
Connect to local database by default.
"""
DEFAULT_DATABASE_HOST = "127.0.0.1" if os.name == "nt" else "0.0.0.0"

"""
Django database configuration.
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DATABASE_NAME", "core"),
        "USER": os.environ.get("DATABASE_USER", "postgres"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", "secret"),
        "HOST": os.environ.get("DATABASE_HOST", DEFAULT_DATABASE_HOST),
        "PORT": os.environ.get("DATABASE_PORT", "5496"),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        )
    }
}

#
# Caching
#

"""
Connect to local redis by default.
"""
DEFAULT_REDIS_HOST = "127.0.0.1" if os.name == "nt" else "0.0.0.0"

"""
Base URL for connecting to redis cache.
"""
redis_base_url = (
    "redis://"
    + os.environ.get("REDIS_HOST", DEFAULT_REDIS_HOST)
    + ":"
    + os.environ.get("REDIS_PORT", "6365")
)

"""
Django cache settings.
"""
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_base_url + "/3",
        "TIMEOUT": 24 * 60 * 60 * 7,
    },
    "session": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_base_url + "/4",
        "TIMEOUT": 24 * 60 * 60 * 7 * 4,
    },
}

#
# Sessions
#

"""
Use the cache backend for session management.
"""
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

"""
Cache bucket name.
"""
SESSION_CACHE_ALIAS = "session"

"""
Django REST framework configuration.
"""
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_FILTER_BACKENDS": ["rest_framework.filters.SearchFilter"],
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "10000/day", "user": "100000/day"},
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    "EXCEPTION_HANDLER": "core.utils.exceptions.rest_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": (
        "core.utils.permissions.ExtendedDjangoModelPermissions",
    ),

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'SIGNING_KEY': os.environ.get('JWT_SIGNING_KEY', '74ptH!T3G$#MF&pAX4kiRNq@XtJ?'),
    'BLACKLIST_AFTER_ROTATION': False
}

# Email
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "admin@deep-ink.ventures")
EMAIL_UUID_MAPPING = {
    'en': {
        'confirmation': 1,
        'password_reset': 2,
        'activation': 3
    },
}
EMAIL_SERVICE_API_KEY = os.environ.get('EMAIL_SERVICE_API_KEY')
EMAIL_ADAPTER = 'core.email.adapter.send_in_blue.SendInBlue'
EMAIL_ACTIVATION_URL = os.environ.get('EMAIL_ACTIVATION_URL', 'http://localhost:3000/actication')
EMAIL_PASSWORD_RESET_URL = os.environ.get('EMAIL_PASSWORD_RESET_URL', 'http://localhost:3000/pw-reset')
EMAIL_EMAIL_RESET_URL = os.environ.get('EMAIL_EMAIL_RESET_URL', 'http://localhost:3000/pw-reset')
USER_CAN_CHANGE_EMAIL = True
EMAIL_SEND_CONFIRMATION_EMAIL = True
EMAIL_SEND_PATIENT_RELEASE_EMAIL = False

AUTH_USER_MODEL = 'user.User'
FRONT_URL = os.environ.get('FRONT_URL', 'https://deep-ink.ventures')
DASHBOARD_URL = os.environ.get('DASHBOARD_URL', 'https://deep-ink.ventures')
BASE_URL = os.environ.get('BASE_URL', 'https://deep-ink.ventures')

NFT_STORAGE_API_KEY = os.environ.get('NFT_STORAGE_API_KEY')
XRP_RPC_URL = os.environ.get('XRP_RPC_URL', "https://s.altnet.rippletest.net:51234/")
NETWORK_EXPLORER_URL = os.environ.get('NETWORK_EXPLORER_URL', 'https://testnet.xrpl.org')