"""Appuser utils"""

import logging
import uuid
import random
import sys

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from djmoney.models.fields import Money
from django.test import Client  # noqa: F401
from rest_framework.test import APIClient
from rest_framework.utils import json
from core.models import send_sms  # pylint: disable=no-name-in-module,import-error
from core.utils import get_random_email, normalize_phone  # pylint: disable=no-name-in-module,import-error
from .models import AppUser, OldUser, OldUserLog

sys.path.append('/home/pashok/Bshop')
sys.path.append('/home/pashok/Bshop/bshop/backend')
from bshop.backend.cfg import devsettings  # pylint: disable=wrong-import-position,wrong-import-order
from bshop.backend import test_security  # pylint: disable=wrong-import-position,wrong-import-order

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('appuser')  # pylint: disable=invalid-name


def import_old_users():
    """Импорт пользователей старого сайта"""
    users = OldUser.objects.all()  # pylint: disable=no-member
    for user in users:
        phone = normalize_phone(user.phone)
        phone = phone[:1].replace('8', '7') + phone[1:20]
        fio_array = user.fio.strip().split(' ')
        surname = fio_array[0]
        name = fio_array[1] if len(fio_array) >= 2 else ''
        patronymic = fio_array[2] if len(fio_array) >= 3 else ''
        cashback = user.cashback
        try:
            existed_user = AppUser.objects.get(phone=phone)
        except ObjectDoesNotExist:
            existed_user = None
        if existed_user:
            existed_user.bonus_balance += Money(cashback, 'RUB')
            existed_user.save()
            logger.debug(f'Увеличен ББ пользователя {phone} на {cashback} руб')
        else:
            password = uuid.uuid4().hex[:8]
            email = get_random_email()
            user_data = {
                'username': phone,
                'email': email,
                'phone': phone,
                'is_jur': False,
                'last_name': surname,
                'first_name': name,
                'patronymic': patronymic,
                'bonus_balance': cashback,
                'is_old': True
            }
            new_user = AppUser.objects.create(**user_data)
            new_user.set_password(password)
            new_user.save()
            logger.debug(f'Создан пользователь {phone}')
            OldUserLog.objects.update_or_create(
                old_user_id=new_user.id,
                defaults={
                    'is_sms_sent': False,
                    'password': password
                })


def send_sms_old_users():
    """Отправка SMS с паролями пользоватлям старого сайта"""
    old_user_logs = OldUserLog.objects.filter(is_sms_sent=False)
    for old_user_log in old_user_logs:
        user = AppUser.objects.get(id=old_user_log.old_user_id)
        password = old_user_log.password
        phone = user.phone
        result = send_sms(
            phone,
            f'Тебе начислен кэшбек {int(round(user.bonus_balance.amount))}₽ Dari-cosmetics.ru. '
            f'Вход в ЛК: логин: {phone}, пароль: {password}. Зайди и потрать его!')
        status = result.get('status')
        if status == 0:
            old_user_log.is_sms_sent = True
            old_user_log.save()


def test_auth():
    """Аутентификация"""
    client = Client()
    response = client.post(BASE_URL + 'api/appuser/login', {'username': test_security.username,
                                                            'password': test_security.password})
    logger.info(response.status_code)
    if response.status_code == 200:
        logger.info('Пользователь прошел аутентификацию')
    else:
        logger.info(response.json())
        logger.info('Пользователь не прошел аутентификацию')
    return response



def random_local():
    """Генерация произвольного пароля и логина"""
    str1 = '1234567890'
    str2 = 'qwertyuiopasdfghjklzxcvbnm'
    str3 = str2.upper()
    str4 = str1 + str2 + str3
    result = list(str4)
    random.shuffle(result)
    length = random.randint(8, 15)
    psw = ''.join([random.choice(result) for x in range(length)])
    return psw


def random_local_telephone():
    """Генерация произвольного номера телефона"""
    str1 = '1234567890'
    result = list(str1)
    random.shuffle(result)
    psw = ''.join([random.choice(result) for x in range(9)])
    return psw


def send_response(url):
    """Отправка запроса"""
    client = Client()
    response = client.get(devsettings.BASE_URL + url)
    if response.status_code == 200:
        logger.info('Тест выполнен успешно.')
        logger.info(response.json())
    else:
        logger.info('Тест провален.')
        logger.info(response.json())


def send_response_jwt(url, flag, record=' '):
    """Отправка запроса c токеном"""
    response_auth = test_auth()
    if response_auth.status_code == 200:
        token = response_auth.json()['token']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        if flag == 'put':
            response = client.put(devsettings.BASE_URL+url, content_type='application/json', data=json.dumps(record))
            if (response.status_code == 200) or (response.status_code == 201):
                logger.info('Тест выполнен успешно.')
            else:
                logger.debug(response.json())
                logger.info('Тест провален.')
        if flag == 'get':
            response = client.get(devsettings.BASE_URL + url)
            if (response.status_code == 200) or (response.status_code == 201):
                logger.info('Тест выполнен успешно.')
            else:
                logger.debug(response.json())
                logger.info('Тест провален.')
        if flag == 'post':
            response = client.post(devsettings.BASE_URL + url, content_type='application/json', data=json.dumps(record))
            if (response.status_code == 200) or (response.status_code == 201):
                logger.info('Тест выполнен успешно.')
            else:
                logger.debug(response.json())
                logger.info('Тест провален.')
    else:
        logger.debug(response_auth.json())
        logger.info('Тест провален.')
