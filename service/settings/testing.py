from . import BASE_DIR

TESTING = True

MEDIAFILES_LOCATION = "test-media"
MEDIA_URL = "/test-media/"
MEDIA_ROOT = BASE_DIR / MEDIAFILES_LOCATION

EMAIL_ADAPTER = 'core.email.adapter.test_email.TestEmail'
