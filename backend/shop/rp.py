"""
Клиент для взаимодействия с API Почты России
"""
import base64
import decimal
import json
import logging
from json import JSONDecodeError

import requests
import urllib3
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import (ConnectionError, ConnectTimeout, HTTPError,  # pylint: disable=redefined-builtin
                                 ReadTimeout)

from core.models import ServiceParam
from core.utils import isnull, transliterate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('rp')  # pylint: disable=invalid-name


class RPClient:
    """Клиент для взаимодействия с API Почты России"""
    QUALITY_CODES = {
        'UNDEF_01': 'Не определен регион',
        'UNDEF_02': 'Не определен город или населенный пункт',
        'UNDEF_03': 'Не определена улица',
        'UNDEF_04': 'Не определен номер дома',
        'UNDEF_05': 'Не определена квартира/офис',
        'UNDEF_06': 'Не определен',
        'UNDEF_07': 'Иностранный адрес'
    }

    SERVICES = {
        'normalize_address': {
            'method': 'POST',
            'url': '/1.0/clean/address'
        },
        'create_order': {
            'method': 'PUT',
            'url': '/1.0/user/backlog'
        },
        'get_order': {
            'method': 'GET',
            'url': '/1.0/backlog/'
        },
        'calc_shipping': {
            'method': 'POST',
            'url': '/1.0/tariff'
        },
        'get_delivery_points': {
            'method': 'GET',
            'url': '/postoffice/1.0/'
        }
    }

    MAIL_TYPES = {
        'POSTAL_PARCEL': 'Посылка нестандартная',
        'ONLINE_PARCEL': 'Посылка онлайн',
        'ONLINE_COURIER': 'Курьер онлайн',
        'EMS': 'Отправление EMS',
        'EMS_OPTIMAL': 'EMS оптимальное',
        'EMS_RT': 'EMS РТ',
        'EMS_TENDER': 'EMS тендер',
        'LETTER': 'Письмо',
        'LETTER_CLASS_1': 'Письмо 1-го класса',
        'BANDEROL': 'Бандероль',
        'BUSINESS_COURIER': 'Бизнес курьер',
        'BUSINESS_COURIER_ES': 'Бизнес курьер экпресс',
        'PARCEL_CLASS_1': 'Посылка 1-го класса',
        'BANDEROL_CLASS_1': 'Бандероль 1-го класса',
        'VGPO_CLASS_1': 'ВГПО 1-го класса',
        'SMALL_PACKET': 'Мелкий пакет',
        'EASY_RETURN': 'Легкий возврат',
        'VSD': 'Отправление ВСД',
        'ECOM': 'ЕКОМ',
        'COMBINED': 'Комбинированное'
    }

    @staticmethod
    def __get_rp_param_val(lst, service_name, param_name):
        for item in lst:
            if item['param_name'] == param_name and item[
                    'service_name'] == service_name:
                return item['param_value']
        return None

    def __init__(self):
        self.base_url = settings.RP_API_BASE_URL
        try:
            rp_params = list(
                ServiceParam.objects.filter(
                    service_name__in=('rp_international', 'rp'),
                    deleted__isnull=True).values('service_name', 'param_name',
                                                 'param_value'))
            token = self.__get_rp_param_val(rp_params, 'rp', 'token')
            login = self.__get_rp_param_val(rp_params, 'rp', 'login')
            password = self.__get_rp_param_val(rp_params, 'rp', 'password')
            user_key = base64.b64encode(
                f'{login}:{password}'.encode()).decode('utf-8')
            int_token = self.__get_rp_param_val(rp_params, 'rp_international',
                                                'token')
            int_login = self.__get_rp_param_val(rp_params, 'rp_international',
                                                'login')
            int_password = self.__get_rp_param_val(rp_params,
                                                   'rp_international',
                                                   'password')
            int_user_key = base64.b64encode(
                f'{int_login}:{int_password}'.encode()).decode('utf-8')
            self.headers = {
                'Accept': 'application/json;charset=UTF-8',
                'Authorization': f'AccessToken {token}',
                'Content-type': 'application/json',
                'X-User-Authorization': f'Basic {user_key}',
            }
            self.int_headers = {
                'Accept': 'application/json;charset=UTF-8',
                'Authorization': f'AccessToken {int_token}',
                'Content-type': 'application/json',
                'X-User-Authorization': f'Basic {int_user_key}',
            }
        except ObjectDoesNotExist:
            self.headers = {}
            logger.error(
                'Ошибка инициализации API Почты России! Не найдены параметры авторизации'
            )
        self.conn_timeout = settings.RP_REQUEST_CONNECTION_TIMEOUT
        self.read_timeout = settings.RP_REQUEST_READ_TIMEOUT

    def process_request(self, request, method, url, mail_type=None):
        """
        Метод выполнения запроса к API
        :param request: тело запроса (dict)
        :param method: метод запроса
        :param url: URL
        :param: mail_type: тип отправления (используется в запросах расчета стоимости доставки и создания отправления)
        :return: ответ в JSON
        """
        if mail_type in ('SMALL_PACKET', 'EMS'):
            headers = self.int_headers
        else:
            headers = self.headers
        logger.debug(f'Запрос к API Почты России: {request}')
        request = json.dumps(request, ensure_ascii=False).encode('utf-8')
        try:
            if method == 'POST':
                resp = requests.post(url=self.base_url + url,
                                     data=request,
                                     headers=headers,
                                     verify=False,
                                     timeout=(self.conn_timeout,
                                              self.read_timeout))
            elif method == 'PUT':
                resp = requests.put(url=self.base_url + url,
                                    data=request,
                                    headers=headers,
                                    verify=False,
                                    timeout=(self.conn_timeout,
                                             self.read_timeout))
            elif method == 'GET':
                resp = requests.get(url=self.base_url + url,
                                    headers=headers,
                                    verify=False,
                                    timeout=(self.conn_timeout,
                                             self.read_timeout))
            elif method == 'DELETE':
                resp = requests.delete(url=self.base_url + url,
                                       headers=headers,
                                       verify=False,
                                       timeout=(self.conn_timeout,
                                                self.read_timeout))
            logger.debug(f'method: {method}, response: {resp.text}')
            return resp.json()
        except (ReadTimeout, ConnectTimeout, ConnectionError, HTTPError) as e:  # pylint: disable=invalid-name
            logger.exception(
                f'В процессе обработки запроса к API Почты России возникло исключение: {e}')
            return {'error': 'Ошибка соединения с сервером Почты России!', 'service_unavailable': True}
        except JSONDecodeError:
            logger.error(f'{resp.text}')
            return {
                'error':
                f'Ошибка соединения с сервером Почты России!',
                'service_unavailable': True
            }

    def normalize_address(self, address):
        """
        Метод нормализации адреса
        :param address: строка адреса в свободной форме
        :return:
        """
        logger.debug(f'Нормализация адреса "{address}"...')
        params = [{'id': 0, "original-address": address}]
        data = self.process_request(
            request=params,
            method=self.SERVICES['normalize_address']['method'],
            url=self.SERVICES['normalize_address']['url'])
        if isinstance(data, list) and len(data) > 0:
            quality_code = data[0].pop('quality-code')
            validation_code = data[0].pop('validation-code')
            if validation_code in ('VALIDATED', 'OVERRIDDEN', 'CONFIRMED_MANUALLY')\
                    and quality_code in ('GOOD', 'POSTAL_BOX', 'ON_DEMAND', 'UNDEF_05'):
                logger.debug(
                    f'Успешно, quality_code {quality_code}, validation_code {validation_code}'
                )
                result = data[0]
            else:
                logger.error(
                    f'Ошибка нормализации адреса {address}. Код проверки {validation_code}, код качества {quality_code}'
                )
                error_desc = self.QUALITY_CODES.get(quality_code, '')
                result = {
                    'message': f'Ошибка проверки адреса! {error_desc}',
                    'error': True,
                    'data': None
                }
        else:
            logger.error(f'Ошибка нормализации адреса: {data}')
            result = {
                'message':
                'Ошибка нормализации адреса! Некорректный формат ответа API Почты России',
                'error': True,
                'data': None
            }
        return result

    def calculate_shipping(self, address, package, mail_type, courier):
        """
        Расчет стоимости доставки отправления
        :param address: словарь, содержащий параметры адреса
        :param package: словарь, содержащий параметры посылки (габариты, вес)
        :param mail_type: тип доставки
        :param courier: признак доставки курьером
        :return:
        """
        mail_category = 'ORDERED' if mail_type == 'SMALL_PACKET' else 'ORDINARY'
        request = {
            "index-from": settings.RP_SENDER_POSTOFFICE_INDEX,
            "completeness-checking": False,
            "courier": courier,
            "declared-value": 0,
            "dimension": {
                "height": package.get('height', 0),
                "length": package.get('length', 0),
                "width": package.get('width', 0)
            },
            "entries-type": "SALE_OF_GOODS",
            "fragile": False,
            "index-to": address.get('postcode', ''),
            "inventory": False,
            "mail-category": mail_category,
            "mail-direct": address.get('country', address.get('oksm_id', 643)),
            "mail-type": mail_type,
            "mass": package.get('weight', 0),
            "notice-payment-method": "CASHLESS",
            "payment-method": "CASHLESS",
            "sms-notice-recipient": 0,
            "transport-type": "SURFACE",
            "with-order-of-notice": False,
            "with-simple-notice": False
        }
        data = self.process_request(
            request=request,
            method=self.SERVICES['calc_shipping']['method'],
            url=self.SERVICES['calc_shipping']['url'],
            mail_type=mail_type)
        if 'code' not in data and 'error' not in data:
            delivery_time = data['delivery-time'].get(
                'max-days') if 'delivery-time' in data else 'Не определено'
            result = {
                'cost': decimal.Decimal(data.get('total-rate', 0) + data.get('total-vat', 0)) / 100,
                'delivery_time': delivery_time
            }
            return {
                'error': False,
                'message': 'Расчет выполнен успешно',
                'data': result,
                'service_unavailable': False
            }
        desc = data.get('desc')
        if desc is None or desc == 'null':
            desc = data.get('error', 'Ошибка расчета стоимости доставки!')
        return {
            'error': data.get('sub-code', True),
            'message': desc,
            'data': None,
            'service_unavailable': data.get('service_unavailable', False)
        }

    def create_shipment(self, address, mail_type, courier, recipient, package):
        """
        Метод создания отправления
        :param address: адрес получателя (dict)
        :param mail_type: тип отправления из массива MAIL_TYPES (обычное или EMS)
        :param courier: признак доставки курьером
        :param recipient: словарь, содержащий ФИО получателя
        :param package: словарь, содержащий параметры отправления (габариты, вес) и список товаров
        :return:
        """
        mail_category = 'ORDERED' if mail_type == 'SMALL_PACKET' else 'ORDINARY'
        country_code = isnull(address.get('oksm_id', 643), 643)
        if country_code != 643:
            if 'surname' in recipient:
                recipient['surname'] = transliterate(recipient['surname'])
            if 'patronymic' in recipient:
                recipient['patronymic'] = transliterate(
                    recipient['patronymic'])
            if 'name' in recipient:
                recipient['name'] = transliterate(recipient['name'])
            recipient.get('surname', '')
        recipient_full_name = recipient.get('surname', '') + ' ' + recipient.get('name', '') + ' ' + \
            recipient.get('patronymic', '')
        logger.debug(f'Отправка запроса на добавление посылки')
        logger.debug(
            f' - address: {address}, тип отправления {mail_type}, '
            f'courier: {courier}, recipient: {recipient}, package: {package}')

        postcode = address.get('postcode', '')
        postcode_int = int(postcode) if len(
            [i for i in postcode if i.isdigit()]) == len(postcode) else ''

        params = [{
            "address-type-to":
            "DEFAULT",
            "area-to":
            isnull(address.get('district', ''), ''),
            "building-to":
            isnull(address.get('building', ''), ''),
            "completeness-checking":
            False,
            "compulsory-payment":
            0,
            "corpus-to":
            isnull(address.get('housing', ''), ''),
            "courier":
            courier,
            "delivery-with-cod":
            False,
            "given-name":
            isnull(recipient.get('name', ''), ''),
            "house-to":
            isnull(address.get('house', ''), ''),
            "index-to":
            postcode_int,
            "mail-category":
            mail_category,
            "mail-direct":
            country_code,
            "mail-type":
            mail_type,
            "manual-address-input":
            False,
            "mass":
            package.get('weight', 0),
            "middle-name":
            isnull(recipient.get('patronymic', ''), ''),
            "order-num":
            isnull(package.get('order_no', ''), ''),
            "place-to":
            isnull(address.get('city', ''), ''),
            "postoffice-code":
            settings.RP_SENDER_POSTOFFICE_INDEX,
            # "raw-address":
            # isnull(address.get('raw_address'), ''),
            "recipient-name":
            recipient_full_name,
            "region-to":
            isnull(address.get('region', ''), ''),
            "location-to":
            isnull(address.get('settlement', ''), ''),
            "street-to":
            isnull(address.get('street', ''), ''),
            "room-to": isnull(address.get('flat', ''), ''),
            "str-index-to":
            isnull(address.get('postcode', ''), ''),
            "surname":
            isnull(recipient.get('surname', ''), ''),
            "tel-address":
            ''.join(i for i in recipient.get('phone', '') if i.isdigit()),
            "transport-type":
            'SURFACE',
        }]
        if mail_type in ('SMALL_PACKET', 'EMS'):
            params[0]['customs-declaration'] = {
                'currency':
                'RUB',
                'customs-entries': [{
                    'amount': 1,
                    'country-code': 643,
                    'description': 'Cosmetics',
                    'tnved-code': '3304990000',
                    'value': package.get('total_amount', 100),
                    'weight': package.get('weight', 0)
                }],
                'entries-type':
                'SALE_OF_GOODS',
                'with-certificate':
                False,
                'with-invoice':
                False,
                'with-license':
                False
            }

        logger.info(params)

        data = self.process_request(
            request=params,
            method=self.SERVICES['create_order']['method'],
            url=self.SERVICES['create_order']['url'],
            mail_type=mail_type)

        if 'errors' in data:
            codes = []
            descriptions = []
            for e in data['errors']:  # pylint: disable=invalid-name
                for code in e['error-codes']:
                    codes.append(code['code'])
                    descriptions.append(code['description'])
            logger.debug(f'errors: {", ".join(descriptions)}')
            return {
                'error': ','.join(codes),
                'message': ', '.join(descriptions),
                'data': None
            }
        if 'result-ids' in data and isinstance(
                data['result-ids'], list) and len(data['result-ids']) >= 1:
            return {
                'error': None,
                'message': f'Создано отправление №{data["result-ids"][0]}',
                'data': {
                    'shipment_id': data['result-ids'][0]
                }
            }
        logger.warning(
            f'Нестандартный ответ на запрос создания заказа: {data}')
        return {
            'error':
            True,
            'message':
            data.get('error',
                     'Ошибка в ответе на запрос создания заказа!'),
            'data':
            data
        }

    def get_order(self, shipment_id, mail_type=None):
        """
        Получение параметров посылки по id
        """
        data = self.process_request(
            request=None,
            method=self.SERVICES['get_order']['method'],
            url=self.SERVICES['get_order']['url'] + str(shipment_id),
            mail_type=mail_type)
        if 'code' not in data and 'error' not in data:
            return {
                'error': None,
                'message': 'Данные об отправлении получены успешно',
                'data': data
            }
        return {
            'error':
            data.get('sub-code', True),
            'message':
            data.get(
                'desc',
                data.get('error',
                         'Ошибка получения параметров отправления!')),
            'data':
            None
        }

    def get_delivery_points(self, postcode):
        """
        Получение списка ПВЗ
        :param postcode: почтовый индекс
        :return: массив ПВЗ
        """
        data = self.process_request(
            request=None,
            method=self.SERVICES['get_delivery_points']['method'],
            url=self.SERVICES['get_delivery_points']['url'] + str(postcode))
        return {
            'error': None,
            'message': 'Данные о ПВЗ получены успешно',
            'data': data
        }
