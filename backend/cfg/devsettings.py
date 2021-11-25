"""
Developer settings for bshop backend
"""
from datetime import timedelta

from .common_settings import *  # noqa: F401, F403
from django.utils.translation import gettext_lazy as _

SITEMAP_GENERATE_PATH = '/home/avasilenko/projects/bshop/frontend/test-ssr/sitemap-generate.js'
SITE_DIR = '/var/www/html/'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)

JWT_AUTH = {'JWT_EXPIRATION_DELTA': timedelta(days=30)}

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'ru'

INTERNAL_IPS = ('127.0.0.1', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'PASSWORD': 'postgres',
        'TEST': {
            'NAME': 'postgres',
        },
    },
}

# ADMIN_TOOLS_MENU = 'menu.CustomMenu'

DEBUG = True

BASE_URL = 'http://127.0.0.1:8000/'
SHORT_BASE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/api/appuser/home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'home'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'login'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = '/home/pashok/Bshop/bshop/backend/static/media'
MEDIA_URL = '/media/'

EMAIL_NOTICE = 'avavasilenko@gmail.com'

PAYMENT_MAIL_LIST = ('avavasilenko@gmail.com', )
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
        'handler_blog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/blog.log',
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
            'backupCount': 3,
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
        'handler_support': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 5 * 5,
            'backupCount': 3,
            'filename': 'log/support.log',
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
        'blog': {
            'handlers': ['console', 'handler_blog'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shop': {
            'handlers': ['console', 'handler_shop'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'support': {
            'handlers': ['console', 'handler_support'],
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
