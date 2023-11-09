from .base import *
from decouple import config

print('Using local')
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DEBUG = True

ALLOWED_HOSTS = ['*']
SECRET_KEY = config("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS headers
CORS_ALLOWED_ORIGIN_REGEXES = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://estate-iq.netlify.app",
    "https://estateiq.ng",

]


# Paystack configurations
PAYSTACK_SECRET_KEY = config("PAYSTACK_TEST_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_TEST_PUBLIC_KEY")
PAYSTACK_BASE_URL = " https://api.paystack.co/"

# Flutterwave configurations
RAVE_SECRET_KEY = config("RAVE_TEST_SECRET_KEY")
RAVE_PUBLIC_KEY = config("RAVE_TEST_PUBLIC_KEY")
RAVE_BASE_URL = "https://ravesandboxapi.flutterwave.com/v3/"
