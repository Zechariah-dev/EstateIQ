import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

print('Using production')

DEBUG = False
SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = ["api.estateiq.ng", "24.199.114.239"]

#  read more https://docs.djangoproject.com/en/4.1/ref/middleware/#http-strict-transport-security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600  # one hour
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
#  I JUST ONLY SET THE DATABASE FOR POSTGRES BUT IT COULD BE MODIFIED
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB', default=''),
        'USER': config('POSTGRES_USER', default=''),
        'PASSWORD': config('POSTGRES_PASSWORD', default=''),
        'HOST': config('POSTGRES_HOST', default=''),
        'PORT': config('POSTGRES_PORT', default=''),
    }
}

# CORS headers
CORS_ALLOWED_ORIGIN_REGEXES = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://estate-iq.netlify.app",
    "https://estateiq.ng"

]

sentry_sdk.init(
    dsn=config("SENTRY_URL"),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Paystack configurations
PAYSTACK_SECRET_KEY = config("PAYSTACK_LIVE_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_LIVE_PUBLIC_KEY")
PAYSTACK_BASE_URL = " https://api.paystack.co/"

# Flutterwave configurations
RAVE_SECRET_KEY = config("RAVE_LIVE_SECRET_KEY")
RAVE_PUBLIC_KEY = config("RAVE_LIVE_PUBLIC_KEY")
RAVE_BASE_URL = "https://api.flutterwave.com/v3/"
