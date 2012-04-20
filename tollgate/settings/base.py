"""
Django default settings for tollgate frontend project.
Copyright 2008-2011 Michael Farrell <http://micolous.id.au/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
PROJECT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))

# You probably should turn this off in an actual deployment.  We have stricter tracebacks anyways.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = dict(
	default=dict(
		ENGINE='django.db.backends.sqlite3',
		NAME='tollgate.db3'
	)
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_PATH, 'sitestatic')
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'tollgate.frontend.common.TollgateMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.messages.context_processors.messages',
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.static',
)

ROOT_URLCONF = 'tollgate.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
	'django.contrib.staticfiles',
    'south',
    'tollgate.frontend',
    'tollgate.api',
	'tollgate.scripts',

)
AUTH_PROFILE_MODULE = 'frontend.userprofile'

LAN_SUBNET = '10.4.0.0/23'
LAN_IFACE = 'eth1'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
# the default amount of quota
DEFAULT_QUOTA_AMOUNT = 150
# are reset excuses required?
RESET_EXCUSE_REQUIRED = True
# changes some texts to imply that quota resets are purchasable
RESET_PURCHASE = False

ONLY_CONSOLE = False
SOURCE_URL = None

# used for restricted-marked calls in the tollgate api
# you need to enter something here!!!!
RESTRICTED_CALLS_KEY = ''

_ = lambda s: s
LANGUAGES = (
  ('en', _('English (Australia)')),
  ('eo', _('Esperanto'))
)

