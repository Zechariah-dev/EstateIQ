INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

]

EXTERNAL_INSTALLED_APPS = [

    #  for authentications
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'rest_framework',
    #  if using token authentication
    'rest_framework.authtoken',
    #  using only jwt
    'rest_framework_simplejwt',

    #  for logging and sending mail
    #  it enable us to view failed and sent mails
    'post_office',
    #  this is used for django channels
    'channels',
    "corsheaders",

    # for running tasks
    'django_celery_beat',
]

LOCAL_INSTALLED_APPS = [
    'users',
    'estates',
    'estate_plans',
    'estate_users',
    'estate_chats',
    'estate_utilities',
    'estate_webhooks',
    'estate_access_logs',
    'estate_complaints',
    'estate_adverts',
    'estate_group_chats',
    'estate_user_notifications',
    'estate_home_pages',
]
INSTALLED_APPS += EXTERNAL_INSTALLED_APPS
INSTALLED_APPS += LOCAL_INSTALLED_APPS
