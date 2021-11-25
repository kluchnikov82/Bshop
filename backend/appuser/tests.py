"""В данном модуле происходит тестировние следующих API-сервисов:
1. Аутентификация.
2. Регистрация.
3. Выход пользователя из системы.
4. Изменение пароля.
5. Изменение профиля пользователя.
6. Получение данных профиля пользователя.
7. Получение списка реферральных заказов пользователя.
8. Получение списка реферралов пользователя.
9. Загрузка аватара в профиль пользователя.
10. Перенос средств с бонусного баланса на депозит.
11. Получение истории начислений/списаний с бонусного баланса пользователя.
12. Переход по реферральной ссылке.
13. Получение пользовательских данных для 1С | Изменение бонусного баланса.
"""
import logging
import sys

from django.test import TestCase, TransactionTestCase  # noqa: F401
from rest_framework.test import APIClient
from core.models import ServiceParam  # pylint: disable=no-name-in-module,import-error
from .utils import random_local, random_local_telephone, test_auth, send_response, send_response_jwt

from bshop.backend.cfg import devsettings  # pylint: disable=wrong-import-position,wrong-import-order

logging.config.dictConfig(devsettings.LOGGING)
logger = logging.getLogger('appuser')  # pylint: disable=invalid-name


class Authentication(TestCase):
    """Аутентификация"""
    def test_auth(self):  # pylint: disable=missing-function-docstring,no-self-use
        return test_auth()



class Registration(TransactionTestCase):
    """Регистрация"""
    def setUp(self):  # pylint: disable=missing-function-docstring,no-self-use,arguments-differ
        username = random_local()
        password = random_local()
        telephone = random_local_telephone()
        self.record = {
            "username": username,
            "password1": password,
            "password2": password,
            "last_name": "qwe",
            "first_name": "zx",
            "patronymic": "as",
            "email": username + "@gmail.com",
            "phone": "+79" + telephone,
            "is_jur": False}

    def test_create(self):  # pylint: disable=missing-function-docstring
        url = 'api/appuser/users'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class Logout(TestCase):
    """Выход пользователя из системы"""
    def test_logout(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/logout'
        flag = 'post'
        send_response_jwt(url, flag)


class ChangePassword(TestCase):
    """Изменение пароля"""
    def setUp(self):  # pylint: disable=missing-function-docstring,no-self-use
        response = test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        password = random_local_telephone()
        self.data = {
            "new_password1": password,
            "new_password2": password}

    def test_change_password(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/change_password'
        flag = 'post'
        send_response_jwt(url, flag, self.data)


class EmailPasswordRecovery(TestCase):
    """Отправка ссылки на восстановление пароля на email пользователя"""
    def setUp(self):  # pylint: disable=missing-function-docstring,no-self-use
        response = test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.data = {"email": "pashokkl@mail.ru"}

    def test_email_password_recovery(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/password/reset'
        flag = 'post'
        send_response_jwt(url, flag, self.data)


class ChangingUserProfile(TestCase):
    """Изменение профиля пользователя"""
    def setUp(self, null=None):  # pylint: disable=missing-function-docstring,no-self-use,arguments-differ
        response = test_auth()
        self.token = response.json()['token']
        dict_user = response.json()['user']
        self.id = dict_user['id']  # pylint: disable=invalid-name
        logger.debug(self.id)
        logger.debug(self.token)
        self.data = {
            "username": "gogi2",
            "email": "gogi2@gmail.com",
            "phone": "79019455212",
            "last_name": "Асланян",
            "first_name": "Гоги",
            "patronymic": "Альбертович",
            "is_partner": False,
            "is_jur": False,
            "sms_notice": False,
            "email_notice": True,
            "addresses": [
                {
                    "id": "55241ddc-97af-41cc-9c6e-d2ecf8237bfc",
                    "address_id": "55241ddc-97af-41cc-9c6e-d2ecf8237bfc",
                    "is_primary": False,
                    "postcode": "460540",
                    "country": "РФ",
                    "region": "Оренбург",
                    "settlement": null,
                    "district": null,
                    "building": "1",
                    "city": "Самара",
                    "street": "Набережная",
                    "house": "2",
                    "flat": "55",
                    "kladr_id": "1231"
                },
                {
                    "is_primary": False,
                    "postcode": "500000",
                    "country": "РФ",
                    "region": "Московская",
                    "settlement": null,
                    "district": null,
                    "building": null,
                    "city": "Москва",
                    "street": "фывфывфыв",
                    "house": "2",
                    "flat": "55",
                    "kladr_id": "226565"
                }
            ],
            "phys_profile": {},
            "jur_profile": {
                "id": "bac4b7fe-10fb-4781-9c42-ac8f98b43dd6",
                "phone_number": "72342134344",
                "inn": "56125565444",
                "org_name": "Гогина контора",
                "manager_name": "Сам Гога",
                "agent_name": null
            }
        }

    def test_changing_user_profile(self):  # pylint: disable=missing-function-docstring
        url = 'api/appuser/users/'+self.id
        flag = 'put'
        send_response_jwt(url, flag, self.data)


class GetUserProfile(TestCase):
    """Получение данных профиля пользователя"""
    def setUp(self):  # pylint: disable=missing-function-docstring,no-self-use
        response = test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        dict_user = response.json()['user']
        self.id = dict_user['id']  # pylint: disable=invalid-name
        logger.debug(self.id)

    def test_get_user_profile(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/users/' + self.id
        flag = 'get'
        send_response_jwt(url, flag)


class GetReferralOrders(TestCase):
    """Получение списка реферральных заказов пользователя"""
    def test_get_referral_orders(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/ref_orders?limit=5&offset=1'
        flag = 'get'
        send_response_jwt(url, flag)


class GetReferralsUser(TestCase):
    """Получение списка реферралов пользователя"""
    def test_get_referrals_user(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/referrals?limit=5&offset=1'
        flag = 'get'
        send_response_jwt(url, flag)


class AvatarUpload(TestCase):
    """Загрузка аватара в профиль пользователя"""
    def setUp(self):
        # Авторизация и получение токена из класса Authentication
        response = test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.data = {"file": "1.jpg"}

    def test_avatar_upload(self):  # pylint: disable=missing-function-docstring
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        file_name = '/home/pashok/1.jpg'
        files = {'file': (file_name, open(file_name, 'rb'), 'image/jpeg')}
        response = client.put(devsettings.BASE_URL + 'api/appuser/avatar_upload/ava90.jpg',
                              data=files
                              )
        if response.status_code == 201:
            logger.info('Тест выполнен успешно.')
        else:
            logger.info('Тест провален.')


class BonusToBalance(TestCase):
    """Перенос средств с бонусного баланса на депозит"""
    def setUp(self):
        self.data = {"amount": "5"}

    def test_bonus_to_balance(self):  # pylint: disable=missing-function-docstring
        url = 'api/appuser/bonus_to_balance'
        flag = 'post'
        send_response_jwt(url, flag, self.data)


class BonusHistory(TestCase):
    """Получение истории начислений/списаний с бонусного баланса пользователя"""
    def test_bonus_history(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/appuser/bonus-history?limit=5&offset=1'
        flag = 'get'
        send_response_jwt(url, flag)


class RefLink(TestCase):
    """Переход по реферральной ссылке"""
    def test_ref_link(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/ref/3'
        send_response(url)


class User1c(TransactionTestCase):
    """Получение пользовательских данных для 1С | Изменение бонусного баланса"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        response = test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        object_ser, created = ServiceParam.objects.get_or_create(service_name='1c',
                                                                 defaults={'service_name': '1c',
                                                                           'id': 'e20bf7b4-8c0b-4106-afac-46cce1f2f1f8',
                                                                           'param_name': 'token',
                                                                           'param_value': self.token})
        if not created:
            object_ser.param_value = self.token
            object_ser.save()

    def test_user_1c(self):  # pylint: disable=missing-function-docstring
        url = 'api/appuser/users_1c/79058191237?token='+self.token+'&bonus_amount=10&order_amount=20'
        send_response(url)
