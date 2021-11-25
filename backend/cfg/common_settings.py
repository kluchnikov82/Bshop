#! /usr/bin/env python
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Общие настройки приложения
"""
import os
import uuid
from decimal import Decimal as D

from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'h$5@m*ek!zub$s@bt&og&1%auq(!kn28wemui_xbr=v88bw8t0'

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + ('Access-Control-Allow-Origin', )

SITE_ID = 1
"""
Настройки all-auth
"""

REST_USE_JWT = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
# ACCOUNT_USERNAME_VALIDATORS = ('portal.validators.username_validators', )
"""
Настройки celery
"""

CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Europe/Moscow'

INSTALLED_APPS = [
    'rest_auth',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'social_django',
    'corsheaders',
    'amocrm',
    'appuser',
    'core',
    'shop',
    'djmoney',
    'blog',
    'support',
    'ckeditor',
    'django_better_admin_arrayfield.apps.DjangoBetterAdminArrayfieldConfig',
    'nested_admin'
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':
    ('rest_framework.permissions.IsAuthenticated', ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ),
    'SEARCH_PARAM':
    'q',
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.LimitOffsetPagination',
    'COERCE_DECIMAL_TO_STRING':
    False,
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'support.middleware.primer',
]

AUTHENTICATION_BACKENDS = (
    'appuser.vk.MyVKOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'core.backends.EmailBackend',
    'core.backends.PhoneBackend',
)

ROOT_URLCONF = 'cfg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'loaders': [
                'admin_tools.template_loaders.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'cfg.wsgi.application'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

AUTH_USER_MODEL = 'appuser.AppUser'

# Значения настроек по умолчанию
OPTIONS_DEFAULT_VALUES = dict(
    # Длительность периода в минутах, по истечении которого, если пользователь не совершал запросов,
    # происходит завершение сессии
    auto_logout_delay=60, )

STATIC_URL = '/static/'
STATIC_ROOT = '/static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Количество элементов на странице, возвращаемых в запросе при пейджинге
DEFAULT_PAGINATE_LIMIT = 10
'''
Настройки приложения Facebook
'''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_KEY = '930428823969368'
SOCIAL_AUTH_FACEBOOK_SECRET = 'f89921442f0080181f20d55078bcbb70'
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'ru_RU',
    'fields': 'id, name, email, age_range'
}
'''
Настройки приложения Vkontakte
'''
SOCIAL_AUTH_VK_OAUTH2_KEY = '6991642'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'HwqHOxs39AVDJjMFRRXT'
SOCIAL_AUTH_VK_OAUTH2_SCOPE = [
    'email',
]
SOCIAL_AUTH_VK_APP_USER_MODE = 2

SOCIAL_AUTH_CREATE_USERS = True

VK_GET_ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token'
VK_REDIRECT_URI = 'https://dari-cosmetics.ru/social-callback'

SOCIAL_AUTH_PIPELINE = ('social_core.pipeline.social_auth.social_details',
                        'social_core.pipeline.social_auth.social_uid',
                        'social_core.pipeline.social_auth.social_user',
                        'social_core.pipeline.user.get_username',
                        'social_core.pipeline.user.create_user',
                        'social_core.pipeline.social_auth.associate_user',
                        'social_core.pipeline.social_auth.load_extra_data',
                        'social_core.pipeline.user.user_details',
                        'appuser.pipeline.get_fb_user_avatar',
                        'social_core.pipeline.debug.debug')
SOCIAL_AUTH_USER_MODEL = 'appuser.AppUser'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# габариты стандартной коробки, см
BOX_DIMENSIONS = {'length': 30, 'width': 25, 'height': 20}

# максимальный объем товаров в одной коробке с запасом 15%, м3
MAX_BOX_VOLUME = BOX_DIMENSIONS['length'] * \
                 BOX_DIMENSIONS['width'] * \
                 BOX_DIMENSIONS['height'] * 0.85
"""
Настройки Paykeeper
"""
PAYKEEPER_BASE_URL = 'https://3dari-cosmetics.server.paykeeper.ru'
PAYKEEPER_REQUEST_CONNECTION_TIMEOUT = 5
PAYKEEPER_REQUEST_READ_TIMEOUT = 7
"""
Настройки API Почты России
"""
RP_API_BASE_URL = 'https://otpravka-api.pochta.ru'
RP_REQUEST_CONNECTION_TIMEOUT = 7
RP_REQUEST_READ_TIMEOUT = 7
RP_SENDER_POSTOFFICE_INDEX = 460000
RP_DEFAULT_MAIL_TYPE = 'POSTAL_PARCEL'
"""
Настройки API CDEK
"""
CDEK_REQUEST_CONNECTION_TIMEOUT = 7
CDEK_REQUEST_READ_TIMEOUT = 7
CDEK_SENDER = {
    'postcode': '460000',
    'phone': '+7-903-360-00-43',
    'company_name': 'ИП Посадский Дмитрий Викторович',
    'name': 'Посадский Дмитрий Викторович',
    'address': {
        'flat': '',
        'house': '39/12',
        'street': 'Ленинская',
        'full': '460000, Russia, Orenburg, Leninskaya str. 39/12',
    }
}
# Код города отправителя
CDEK_SENDER_CITY_ID = 261
# Коды стран, в которые возможна доставка СДЭК
CDEK_COUNTRIES = ('ru', 'kz', 'by')

"""
Параметры доставки
"""

# Коды типов доставки для поля shop.models.Order.shipment_method_id
RUSSIAN_POST = 0
EMS_RUSSIA = 1
CDEK_COURIER = 2
CDEK_DELIVERY_POINT = 3
EMS_INTERNATIONAL = 4
CDEK_INTERNATIONAL_COURIER = 5
SMALL_PACKET = 6
PICKUP = 7
COURIER_ORENBURG = 8
CDEK_INTERNATIONAL_DELIVERY_POINT = 9

# цена доставки курьером по Оренбургу
COURIER_ORENBURG_PRICE = 200

PICKUP_ADDRESS_ID = uuid.UUID('f45cbe02-8810-43a1-9e54-c5a49109404e')

SHIPPING_METHODS = (
    (RUSSIAN_POST, 'Почта России'),
    (EMS_RUSSIA, 'EMS по России'),
    (EMS_INTERNATIONAL, 'EMS международная доставка'),
    (SMALL_PACKET, 'Мелкий пакет МН'),
    (CDEK_DELIVERY_POINT, 'Пункт самовывоза СДЭК'),
    (CDEK_COURIER, 'СДЭК курьер'),
    (CDEK_INTERNATIONAL_COURIER, 'СДЭК международная доставка до двери'),
    (PICKUP, 'Самовывоз (ТК Успех, ул. Ленинская 39)'),
    (COURIER_ORENBURG, 'Курьером по Оренбургу'),
    (CDEK_INTERNATIONAL_DELIVERY_POINT, 'СДЭК международная доставка до ПВЗ'),
)

RUSSIA_SHIPPING_METHODS = (
    SHIPPING_METHODS[0], SHIPPING_METHODS[1],
    SHIPPING_METHODS[4], SHIPPING_METHODS[5],
)

INTERNATIONAL_SHIPPING_METHODS = (
    SHIPPING_METHODS[2], SHIPPING_METHODS[6],
    SHIPPING_METHODS[9],)
"""
Массив способов доставки CDEK:
- идентификатор метода
- текстовое описание метода
- код тарифа
- id метода доставки (3 - до двери курьером, 4 - до ПВЗ)
"""

CDEK_SHIPPING_METHODS = (
    (CDEK_COURIER, 'CDEK до двери по России', 137, 3),
    (CDEK_DELIVERY_POINT, 'CDEK до ПВЗ по России', 136, 4),
    (CDEK_INTERNATIONAL_COURIER, 'CDEK международная доставка до двери', 137, 3),
    (CDEK_INTERNATIONAL_DELIVERY_POINT, 'CDEK международная доставка до ПВЗ', 136, 4),
)

# Коды стран, в которые осуществляется доставка СДЭК
CDEK_COUNTRY_CODES = {
    'iso_alpha2':  ('kz', 'by'),
    'iso_numeric': (112, 398)
}

"""
Массив способов доставки Почтой России:
- идентификатор метода
- текстовое описание метода
- кодовое обозначение метода в термиинах API Почты России
- признак курьерской доставки
"""
RP_SHIPPING_METHODS = (
    (RUSSIAN_POST, 'Почта России', 'POSTAL_PARCEL', False),
    (EMS_RUSSIA, 'EMS по России', 'EMS_OPTIMAL', True),
    (EMS_INTERNATIONAL, 'EMS МН', 'EMS', False),
    (SMALL_PACKET, 'Мелкий пакет МН', 'SMALL_PACKET', False)
)
"""
Длина периода в днях по истечение которого начисленные на бонусный баланс средства
становятся доступными для расходования
"""
BONUS_PERIOD = 14
"""
Настройки почтового сервера
"""
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin@dari-cosmetics.ru'
EMAIL_HOST_PASSWORD = "zxcDFG2010"
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_MAIL_LIST = ('avasilenko@iplatforms.ru',)
"""
Максимальная сумма оплаты заказа бонусами
"""
MAX_BONUS_PAYMENT_SHARE = 0.8
"""
Префикс промокода для реферралов
"""
REF_PROMO_PREFIX = 'AJFAGP'
"""
URL платежного сервиса Сбербанк-Онлайн
"""
SBERBANK_REF_URL = 'https://securepayments.sberbank.ru'
"""
Период действия ссылки на оплату в системе Сбербанк-онлайн, дней
"""
SBERBANK_LINK_EXPIRATION_PERIOD = 1
"""
Коэффициент наценки на доставку. При отсутствии наценки должен быть равен 1
"""
SHIPMENT_EXTRA_CHARGE = D('1.2')
"""Длина периода в часах с момента создания, в течение которого возможно редактирование заказа"""
ORDER_EDIT_PERIOD = 24

TEST_USER_IDS = ('f2a0710a-2b1f-41c6-a75f-8cafeef38fc1',)
