"""
Клиент для взаимодействия с API Paykeeper
"""
import base64
import logging
from json.decoder import JSONDecodeError

import requests
import urllib3
from django.conf import settings
from requests.exceptions import (ConnectionError, ConnectTimeout, HTTPError,  # pylint: disable=redefined-builtin
                                 ReadTimeout)

from core.models import ServiceParam

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('paykeeper')  # pylint: disable=invalid-name


class PaykeeperClient:
    """
    Клиент для взаимодействия с API Paykeeper
    """
    SERVICES = {
        'get_token': {
            'method': 'GET',
            'url': '/info/settings/token/'
        },
        'get_link': {
            'method': 'POST',
            'url': '/change/invoice/preview/'
        }
    }

    def __init__(self):
        self.base_url = settings.PAYKEEPER_BASE_URL
        self.login = ServiceParam.objects.get(service_name='paykeeper',
                                              param_name='login').param_value
        self.password = ServiceParam.objects.get(
            service_name='paykeeper', param_name='password').param_value

        auth_string = base64.b64encode(
            bytes(f'{self.login}:{self.password}', 'utf-8')).decode('utf-8')
        self.headers = {
            'authorization': f'Basic {auth_string}',
            'content-type': 'application/x-www-form-urlencoded'
        }
        self.conn_timeout = settings.PAYKEEPER_REQUEST_CONNECTION_TIMEOUT
        self.read_timeout = settings.PAYKEEPER_REQUEST_READ_TIMEOUT
        self.token = None

    def process_request(self, request, params):
        """
        Метод выполнения запроса к API
        :param request: тело запроса (dict или xml)
        :param params: словарь, содежащий параметры запрроса (метод, URL и тип)
        :return: ответ в JSON
        """
        method = params['method']
        url = params['url']

        try:
            if method == 'POST':
                resp = requests.post(url=self.base_url + url,
                                     data=request,
                                     params=request,
                                     headers=self.headers,
                                     verify=False,
                                     timeout=(self.conn_timeout,
                                              self.read_timeout))
            elif method == 'PUT':
                resp = requests.put(url=self.base_url + url,
                                    data=request,
                                    headers=self.headers,
                                    verify=False,
                                    timeout=(self.conn_timeout,
                                             self.read_timeout))
            elif method == 'GET':
                resp = requests.get(url=self.base_url + url,
                                    headers=self.headers,
                                    verify=False,
                                    params=request,
                                    timeout=(self.conn_timeout,
                                             self.read_timeout))
            elif method == 'DELETE':
                resp = requests.delete(url=self.base_url + url,
                                       headers=self.headers,
                                       verify=False,
                                       timeout=(self.conn_timeout,
                                                self.read_timeout))
            logger.debug(f'method: {method}, response: {resp.text}')
            return resp.json()
        except (ReadTimeout, ConnectTimeout, ConnectionError, HTTPError) as e:  # pylint: disable=invalid-name
            logger.exception(
                f'В процессе обработки запроса к API Paykeeper возникло исключение: {e}')
            return {'error': 'Ошибка соединения с сервером Paykeeper!'}
        except JSONDecodeError:
            logger.error('Ошибка обработки ответа от API Paykeeper')
            return {
                'error':
                    'Ошибка обработки запроса к платежному шлюзу! Пожалуйста, обратитесь к администратору'}

    def get_token(self):
        """
        Получение токена для ауентификации
        """
        params = self.SERVICES.get('get_token')
        resp = self.process_request(request=None, params=params)
        self.token = resp.get('token', None)

    def get_pay_link(self, request):
        """
        Получение ссылки на оплату
        """
        if not self.token:
            self.get_token()
        params = self.SERVICES.get('get_link')
        request['token'] = self.token
        resp = self.process_request(request, params)
        logger.debug(f'Ответ на запрос ссылки на оплату: {resp}')
        if 'invoice_id' in resp:
            return {
                'error': False,
                'message': 'Ссылка на оплату получена',
                'data': resp['invoice_url']
            }
        return {
            'error':
            True,
            'message':
            resp.get(
                'msg', 'Ошибка получения ссылки на оплату! '
                'Пожалуйста, обратитесь к администратору'),
            'data':
            None
        }
