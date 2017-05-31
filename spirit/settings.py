# Django settings for spirit project.
import os
from memcacheify import memcacheify

ROOT_PATH = os.path.dirname(__file__)

OFFLINE = False

# the number of days allowed after which spirit scores can still be entered with raising suspicion
ALLOWED_DAYS_TO_ENTER = 14

# try:
#     from local_settings import *
# except ImportError, e:
#     pass

# allows to switch between the real and the testing leaguevine server
#HOST="http://api.playwithlv.com"
HOST="https://api.leaguevine.com"
# HOST = "http://api.localhost:8000"

ALLOWED_HOSTS = ['spiritapp.herokuapp.com', 'spirit.leaguevine.com', '127.0.0.1']


# expects credentials to be stored in environmental variables!
ON_HEROKU = False
if 'ON_HEROKU' in os.environ:
    ON_HEROKU = True
    DEBUG = os.environ.get('DEBUG', False)  # if DEBUG exists on Heroku, use DEBUG mode, otherwise not
else:
    DEBUG = True

if ON_HEROKU:
    if HOST == "http://api.playwithlv.com":
        CLIENT_ID = os.environ['CLIENT_ID_PLAYWITHLV']
        CLIENT_PWD = os.environ['CLIENT_PWD_PLAYWITHLV']
        TOKEN_URL = 'http://www.playwithlv.com'
    else:
        CLIENT_ID = os.environ['CLIENT_ID']
        CLIENT_PWD = os.environ['CLIENT_PWD']
        TOKEN_URL = 'https://www.leaguevine.com'
    REDIRECT_URI = os.environ['REDIRECT_URI']
    # CLIENT_ID = '691cad4da330e02a36539d2f412eb0'
    # CLIENT_PWD = '2ef5a2643216c35efac0500f7752e6'
else:
    # these credentials refer to an app which redirects to  http://127.0.0.1:8000/code/
    # https://www.leaguevine.com/apps/84/
    CLIENT_ID = 'e41df6413799888cbf02987ebede49'
    CLIENT_PWD = '6bbbd86bef4b4359d3298ce9112f56'
    REDIRECT_URI = 'http://127.0.0.1:8000/code/'
    # REDIRECT_URI = 'http://10.10.255.179:8000/code/'



CACHES = memcacheify()
CACHE_TIME = 60 * 60 * 24 * 5 # 5 days
CACHE_TIME_VIEWS = 60 * 60    # 1 hour\

if not ON_HEROKU:
    CACHE_TIME_VIEWS = 0    # no view caching locally



if HOST == "http://api.playwithlv.com":
    TOKEN_URL = 'http://www.playwithlv.com'
elif HOST == "http://api.localhost:8000":
    TOKEN_URL = 'http://localhost:8000'
else:
    TOKEN_URL = 'https://www.leaguevine.com'

LOGINURL = '{0}/oauth2/authorize/?client_id={1}&response_type=code&redirect_uri={2}&scope=universal'.format(TOKEN_URL,
                                                                                                            CLIENT_ID,
                                                                                                            REDIRECT_URI)

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Christian Schaffner', 'huebli@gmail.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'info@spirit.leaguevine.com'
SERVER_EMAIL = 'info@spirit.leaguevine.com'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

if not ON_HEROKU:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '{0}/app-messages'.format(ROOT_PATH)
#    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
elif ON_HEROKU:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST_USER = os.environ['MAILGUN_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['MAILGUN_PASSWORD']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'staticfiles'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'e^+fnmfdajh)bx#63@em02*ezm75!4_-@eqe^#-@uy-quki*h&amp;'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'spirit.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'spirit.wsgi.application'

TEMPLATE_DIRS = (
    '~/Sites/spirit/spirit/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'spirit',
    'bootstrapform',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#AUTHENTICATION_BACKENDS = ('spirit.lv_backend.LeaguevineBackend','django.contrib.auth.backends.ModelBackend',)
SESSION_ENGINE = 'django.contrib.sessions.backends.file'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'spirit': {
            'handlers': ['console'],
            'level': 'INFO',
        },

    }
}
