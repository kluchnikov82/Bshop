"""В данном модуле происходит тестировние следующих API-сервисов:
1. Создание обращения в техподдержку.
2. Получение списка типов обращений в техподдержку.
"""
import logging
import sys
from django.test import TestCase
from appuser.utils import send_response, send_response_jwt  # pylint: disable=import-error

from bshop.backend.cfg import devsettings  # pylint: disable=wrong-import-position

logging.config.dictConfig(devsettings.LOGGING)
logger = logging.getLogger('support')  # pylint: disable=invalid-name


class CreateSupportRequest(TestCase):
    """Создание обращения в техподдержку"""
    def test_create_support_request(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/support/requests'
        flag = 'get'
        send_response_jwt(url, flag)


class GetSupportRequestTypes(TestCase):
    """Получение списка типов обращений в техподдержку"""
    def test_get_support_request_types(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/support/req_types'
        send_response(url)
