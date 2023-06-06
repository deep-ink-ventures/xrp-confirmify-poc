import sys
from . import *

DEBUG = True

SECRET_KEY = "django-insecure-rgry4=dk52ybc+01$ft6*&csql!&s@&$)3bq&vxk_ou_*lhs4!"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
EMAIL_ADAPTER = 'core.email.adapter.test_email.TestEmail'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
        "simple": {
            "format": "%(levelname)s %(asctime)s  %(module)s %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "app": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "kyc": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

try:
    from .local import *
except ImportError:
    pass

if "test" in sys.argv:
    from .testing import *
