"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join
from workbench.settings import *


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


LOCALE_PATHS = [
    root('skill_tagging', 'conf', 'locale'),
]

ROOT_URLCONF = 'test_urls'

SECRET_KEY = 'insecure-secret-key'

MIDDLEWARE = (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': False,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',  # this is required for admin
            'django.contrib.messages.context_processors.messages',  # this is required for admin
        ],
    },
}]

TAXONOMY_API_BASE_URL = 'http://example.com'
