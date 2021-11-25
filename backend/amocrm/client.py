"""
Клиент для взаимодействия с API AmoCRM
"""
import json
import logging

import requests
import urllib3
from django.conf import settings
from django.utils import timezone as tz
from requests.exceptions import (ConnectionError, ConnectTimeout, HTTPError,  # pylint: disable=redefined-builtin
                                 ReadTimeout)

from .custom_fields import get_field_id
from .errors import CRM_ERRORS
from .models import RequestType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('amocrm')  # pylint: disable=invalid-name
"""
Базовые настройки API
"""
OPTIONS = {
    'BASE_URL': 'https://vikaprobuet.amocrm.ru',
    'USER_LOGIN': 'giff20@mail.ru',
    'USER_HASH': 'ac016ce2f7e13a6785d447fc2ea110377b72f873',
    'USER_ID': 19048117,
    'RESPONSIBLE_USER_ID': 19048117,
    'TIMEOUTS': (7, 7),
    'TAGS': 'сайт',
    'PRODUCTS_CATALOG_ID': 4987
}


class CRMClient:
    """
    Класс для работы с amoCRM
    """
    URLS = {
        RequestType.AUTH:
        OPTIONS['BASE_URL'] + '/private/api/auth.php?type=json',
        RequestType.ADD_LEAD: OPTIONS['BASE_URL'] + '/api/v2/leads',
        RequestType.EDIT_LEAD: OPTIONS['BASE_URL'] + '/api/v2/leads',
        RequestType.ADD_CONTACT: OPTIONS['BASE_URL'] + '/api/v2/contacts',
        RequestType.EDIT_CONTACT: OPTIONS['BASE_URL'] + '/api/v2/contacts',
        RequestType.GET_CONTACT: OPTIONS['BASE_URL'] + '/api/v2/contacts',
        RequestType.GET_ACCOUNT_INFO: OPTIONS['BASE_URL'] + 'api/v2/account',
    }

    def __init__(self):
        self.login = OPTIONS['USER_LOGIN']
        self.hash = OPTIONS['USER_HASH']
        self.session_id = None
        self.timeout = OPTIONS['TIMEOUTS']
        self.tags = OPTIONS['TAGS']

    def do_auth(self):
        """
        Аутентификация в amoCRM и получение session_id
        :return:
        """
        result = None
        try:
            headers = {'content-type': 'application/json'}
            request = json.dumps(
                {
                    'USER_LOGIN': self.login,
                    'USER_HASH': self.hash
                },
                ensure_ascii=False).encode("utf-8")
            r = requests.post(url=self.URLS[RequestType.AUTH],  # pylint: disable=invalid-name
                              data=request,
                              headers=headers,
                              verify=False,
                              timeout=OPTIONS['TIMEOUTS'])
            self.session_id = r.cookies['session_id']
            logger.debug(f'session_id: {self.session_id}')
            result = True
            logger.info('Аутентификация в amoCRM успешна!')
        except (ReadTimeout, ConnectTimeout, ConnectionError, HTTPError) as e:  # pylint: disable=invalid-name
            logger.exception(
                f'В процессе аутентификации в ЛК amoCRM возникло исключение: {e}')
        return result

    def build_add_contact_request(self, params):
        """
        Создание запроса добавления контакта к API amoCRM
        :param params: словарь параметров запроса
        :return: endpoint + текст запроса на добавления контакта
        """
        if 'tags' in params:
            tags = f'{self.tags},{params["tags"]}'
        else:
            tags = self.tags
        email_id = get_field_id('contacts', 'EMAIL')
        phone_id = get_field_id('contacts', 'PHONE')
        email = params.get('email', '')
        phone = params.get('phone', '')

        request = dict(add=[
            dict(name=params['name'],
                 created_by=OPTIONS['USER_ID'],
                 responsible_user_id=OPTIONS['RESPONSIBLE_USER_ID'],
                 tags=tags,
                 custom_fields=[
                     dict(id=email_id, values=[dict(value=email, enum='PRIV')
                                               ]),
                     dict(id=phone_id, values=[dict(value=phone, enum='MOB')])
                 ])
        ])
        request_method = 'POST'
        return request, request_method

    def build_edit_contact_request(self, params):
        """
        Создание запроса добавления контакта к API amoCRM
        :param params: словарь параметров запроса
        :return: endpoint + текст запроса на добавления контакта
        """
        if 'tags' in params:
            tags = f'{self.tags},{params["tags"]}'
        else:
            tags = self.tags
        email_id = get_field_id('contacts', 'EMAIL')
        phone_id = get_field_id('contacts', 'PHONE')
        email = params.get('email', '')
        phone = params.get('phone', '')
        contact_id = params.get('contact_id', '')
        updated_at = str(int(tz.now().timestamp()))

        request = dict(update=[
            dict(id=contact_id,
                 updated_at=updated_at,
                 name=params['name'],
                 created_by=OPTIONS['USER_ID'],
                 responsible_user_id=OPTIONS['RESPONSIBLE_USER_ID'],
                 tags=tags,
                 custom_fields=[
                     dict(id=email_id, values=[dict(value=email, enum='PRIV')
                                               ]),
                     dict(id=phone_id, values=[dict(value=phone, enum='MOB')])
                 ])
        ])
        request_method = 'POST'
        return request, request_method

    def build_add_lead_request(self, params):
        """
        Создание запроса к API amoCRM на добавление сделки
        :param params: словарь параметров запроса
        :return: endpoint + текст запроса на добавления сделки
        """
        request = None
        contact_id = params.get('contact_id', None)
        company_id = params.get('company_id', None)

        if 'tags' in params:
            tags = f'{self.tags},{params["tags"]}'
        else:
            tags = self.tags

        if contact_id or company_id:
            lead_source_id = get_field_id('leads', 'Источник лида')
            custom_fields = [
                dict(id=lead_source_id,
                     values=[dict(value='Сайт', enum='745175')])
            ]

            feedback_text = params.get('feedback', None)
            if feedback_text:
                feedback_id = get_field_id('leads', 'Отзыв')
                logger.debug(
                    f'feedback_id: {feedback_id}, feedback_text: {feedback_text}'
                )
                custom_fields.append(
                    dict(id=feedback_id, values=[dict(value=feedback_text)]))

            address = params.get('address', None)
            if address:
                address_id = get_field_id('leads', 'Адрес доставки')
                logger.debug(f'address_id: {address_id}, address: {address}')
                custom_fields.append(
                    dict(id=address_id, values=[dict(value=address)]))

            memo = params.get('memo', None)
            if memo:
                memo_id = get_field_id('leads', 'Комментарий к заказу')
                logger.debug(f'memo_id: {memo_id}, memo: {memo}')
                custom_fields.append(
                    dict(id=memo_id, values=[dict(value=memo)]))

            href = params.get('href', None)
            if href:
                href_id = get_field_id('leads', 'Онлайн счет')
                logger.debug(f'href_id: {href_id}, href: {href}')
                custom_fields.append(
                    dict(id=href_id, values=[dict(value=href)]))

            tags = f'{self.tags},{tags}'
            sale = params.get('sale', 0)
            lead_name = params.get('lead_name', None)
            request = dict(add=[
                dict(name=lead_name,
                     created_by=OPTIONS['USER_ID'],
                     responsible_user_id=OPTIONS['RESPONSIBLE_USER_ID'],
                     tags=tags,
                     sale=sale,
                     contacts_id=contact_id,
                     company_id=company_id,
                     custom_fields=custom_fields)
            ])
        request_method = 'POST'
        return request, request_method

    def process_request(self, request_type, params=None):
        """
        Выполнение запроса к API amoCRM
        :param: request_type: тип запроса
         params: словарь параметров запроса
          - req_type: обязательный, тип запроса
          - user_id: обязательный, ID пользователя сайта
          - tags: строка, содержащая список тегов через запятую без пробелов
          - name: логин пользователя
          - email: email пользователя
          - lead_name: название сделки
          - contact_id: ID контакта в amoCRM
          - company_id: ID компании в amoCRM
          - lead_id: ID сделки
        :return:
        """
        def response_add_contact(data):
            """
            Обработчик ответа на запрос создания контакта
            :param data: тело ответа
            :return: словарь результатов обработки ответа
            """
            contact_id = data['_embedded']['items'][0]['id']
            return {'contact_id': contact_id}

        def response_add_lead(data):
            """
            Обработчик ответа на запрос создания сделки
            :param data: тело ответа
            :return: словарь результатов обработки ответа
            """
            lead_id = data['_embedded']['items'][0]['id']
            return {'lead_id': lead_id}

        def response_get_contact(data):
            """
            Обработчик ответа на запрос контаков
            :param data: тело ответа
            :return: словарь результатов обработки ответа
            """
            data = data['_embedded']['items']
            return {'items': data}

        def case_request_response_funcs(request_type):
            """
            Реализация switch-case для выбора функции построения запроса и обработчика ответа
            :param request_type: тип запроса
            :return: функция создания запроса + обработчик ответа
            """
            def build_get_contact_request(params):
                """
                Создание запроса к API amoCRM на поиск контакта
                :param params: словарь параметров запроса
                :return: endpoint + текст запроса на добавления контакта
                """
                req = dict(id=params['id']) if 'id' in params else dict(query=params['query'])
                req_method = 'GET'
                return req, req_method

            switcher_request = {
                RequestType.ADD_CONTACT: self.build_add_contact_request,
                RequestType.EDIT_CONTACT: self.build_edit_contact_request,
                RequestType.ADD_LEAD: self.build_add_lead_request,
                RequestType.GET_CONTACT: build_get_contact_request
            }
            switcher_response = {
                RequestType.ADD_CONTACT: response_add_contact,
                RequestType.EDIT_CONTACT: response_add_contact,
                RequestType.ADD_LEAD: response_add_lead,
                RequestType.GET_CONTACT: response_get_contact
            }
            f_req = switcher_request.get(request_type, None)
            f_resp = switcher_response.get(request_type, None)
            return f_req, f_resp

        def get_resp_errors(data):
            """
            Анализ полученного от API amoCRM ответа и формирование сообщения об ошибках
            :param data: ответ от amoCRM
            :return: None если запрос выполнен успешно, словарь с описанием ошибок в ином случае
            """
            embedded = data.get('_embedded', None)
            errors = embedded.get('errors', None)
            err_code = 0
            err_desc = ''
            if errors is None:
                err = data.get('title', data.get('response', None))
                if err is None:
                    return None
                if err == 'Error':
                    err_code = data.get('status', None)
                    err_desc = CRM_ERRORS.get(
                        err_code,
                        'Неизвестная ошибка - описание отсутствует!')
                else:
                    resp = data.get('response', None)
                    err_code = resp.get('error_code', None)
                    err_desc = resp.get('error', None)
            else:
                for v in errors:  # pylint: disable=invalid-name
                    if isinstance(v, list):
                        err_code = -1
                        err_desc = v[0]
                    elif isinstance(v, dict):
                        for key, val in v.items():
                            err_code = key
                            err_desc = val
            return {'err_code': err_code, 'err_desc': err_desc}

        url = self.URLS[request_type]
        create_request, process_response = case_request_response_funcs(
            request_type)
        request, request_method = create_request(params)
        if request:
            try:
                if request_method == 'POST':
                    request_json = json.dumps(
                        request, ensure_ascii=False).encode('utf-8')
                    logger.debug(f'request: {request}')
                    response = requests.post(
                        url=url,
                        data=request_json,
                        verify=False,
                        timeout=OPTIONS['TIMEOUTS'],
                        cookies={'session_id': self.session_id})
                else:
                    response = requests.get(
                        url=url,
                        params=request,
                        verify=False,
                        timeout=OPTIONS['TIMEOUTS'],
                        cookies={'session_id': self.session_id})
                if response.status_code == 204:
                    logger.warning(
                        f'Отсутствуют данные по запросу {request_type} с параметрами {params}'
                    )
                    return {
                        'status': 'error',
                        'request_type': request_type,
                        'result': {
                            'err_code': -204,
                            'err_desc': 'Нет данных'
                        }
                    }
                data = response.json()
                check_result = get_resp_errors(data)
                if check_result is None:
                    result = process_response(response.json())
                    return {
                        'status': 'ok',
                        'request_type': request_type,
                        'result': result
                    }
                return {
                    'status': 'error',
                    'request_type': request_type,
                    'result': check_result
                }
            except (ReadTimeout, ConnectTimeout, ConnectionError,  # pylint: disable=invalid-name
                    HTTPError) as e:
                logger.exception(
                    f'В процессе выполнения запроса к amoCRM возникло исключение: {e}')
                return {
                    'status': 'error',
                    'request_type': request_type,
                    'result': {
                        'err_code': -1,
                        'err_desc': e
                    }
                }
        else:
            logger.warning(
                f'Не удалось сформировать запрос типа {request_type} с параметрами {params}'
            )

    def get_custom_fields(self):
        """
        Получение нестандартных полей, созданных в AmoCRM
        """
        response = requests.get(url=OPTIONS['BASE_URL'] +
                                '/api/v2/account?with=custom_fields',
                                verify=False,
                                timeout=OPTIONS['TIMEOUTS'],
                                cookies={'session_id': self.session_id})
        return response.json()['_embedded']['custom_fields']
