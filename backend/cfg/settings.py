"""
Prod settings
"""
from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.utils.translation import gettext_lazy as _

SITEMAP_GENERATE_PATH = '/home/logshipping/bshop/frontend/ssr/sitemap-generate.js'
SITE_DIR = '/var/www/dari-ssr/'

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

from .common_settings import *  # noqa: F401, F403


sentry_sdk.init(
    dsn='https://1329091935514f24958369ccbba20bc0@o374309.ingest.sentry.io/5192113',
    integrations=[DjangoIntegration()])

DEBUG = False

ALLOWED_HOSTS = ["*"]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

JWT_AUTH = {'JWT_EXPIRATION_DELTA': timedelta(days=3650)}

STATIC_ROOT = "/var/www/dari-ssr/static"
MEDIA_ROOT = '/var/www/dari-ssr/static/media'
MEDIA_URL = '/media/'
BASE_URL = 'https://dari-cosmetics.ru/'
SHORT_BASE_URL = 'https://dari-cosmetics.ru'

EMAIL_NOTICE = 'info@dari-cosmetics.ru'

PAYMENT_MAIL_LIST = ('zakaz@dari-cosmetics.ru', 'oren.tiande@yandex.ru',
                     'uspeh.tiande@yandex.ru')

ORDER_DETAIL_URL = BASE_URL + 'order/'

USE_SBERBANK_ONLINE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'common': {
            'format': '%(asctime)-15s %(levelname)-9s %(name)-4s %(message)-4s'
        },
    },
    'handlers': {
        'handler_common': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/common.log',
            'formatter': 'common'
        },
        'handler_amocrm': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/amocrm.log',
            'formatter': 'common'
        },
        'handler_shop': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 20,
            'filename': 'log/shop.log',
            'formatter': 'common'
        },
        'handler_core': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/core.log',
            'formatter': 'common'
        },
        'handler_appuser': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/appuser.log',
            'formatter': 'common'
        },
        'handler_paykeeper': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/paykeeper.log',
            'formatter': 'common'
        },
        'handler_rp': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/russian_post.log',
            'formatter': 'common'
        },
        'handler_cdek': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/cdek.log',
            'formatter': 'common'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'common',
        },
    },
    'loggers': {
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console', ],
        # },
        'common': {
            'handlers': ['console', 'handler_common'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'amocrm': {
            'handlers': ['console', 'handler_amocrm'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shop': {
            'handlers': ['console', 'handler_shop'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'handler_core'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'appuser': {
            'handlers': ['console', 'handler_appuser'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'paykeeper': {
            'handlers': ['console', 'handler_paykeeper'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rp': {
            'handlers': ['console', 'handler_rp'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cdek': {
            'handlers': ['console', 'handler_cdek'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
