"""
Common utils
"""
import logging
import re
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import connection

from .tasks import send_mail

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('core')  # pylint: disable=invalid-name


def get_next_id(params):
    """
    Генератор кастомных id для любой модели
    """
    args = (params['app_label'], params['model_name'], params['min_val'],
            params['step'], params['max_val'])
    with connection.cursor() as c:  # pylint: disable=invalid-name
        c.execute('SELECT * FROM get_next_id(%s, %s, %s, %s, %s)', args)
        last_id = c.fetchone()[0]
    new_id = last_id + params['step']
    return new_id


def get_list_item_by_key(key, val, lst):
    """"
    Поиск элемента в массиве словарей по значению ключа
    """
    for item in lst:
        for k, v in item.items():  # pylint: disable=invalid-name
            if key == k and v == val:
                return item
    return None


def get_decimal(x):  # pylint: disable=invalid-name
    """
    Convert object to decimal
    :param x:
    :return:
    """
    return Decimal(str(x)).quantize(Decimal('1.00'))


def isnull(x, y):  # pylint: disable=invalid-name
    """
    SQL isnull analogue
    """
    if x is None:
        return y
    return x


def get_cdek_method_id(shipping_method_id):
    """
    Получение ID способа доставки СДЭК по идентификатору способа доставки модели Order
    :param shipping_method_id:
    :return:
    """
    for i in settings.CDEK_SHIPPING_METHODS:
        if i[0] == shipping_method_id:
            return i[2]
    return None


def transliterate(string):
    """
    Транслитерация строки в латинице
    :param string:
    :return:
    """
    capital_letters = {
        u'А': u'A',
        u'Б': u'B',
        u'В': u'V',
        u'Г': u'G',
        u'Д': u'D',
        u'Е': u'E',
        u'Ё': u'E',
        u'З': u'Z',
        u'И': u'I',
        u'Й': u'Y',
        u'К': u'K',
        u'Л': u'L',
        u'М': u'M',
        u'Н': u'N',
        u'О': u'O',
        u'П': u'P',
        u'Р': u'R',
        u'С': u'S',
        u'Т': u'T',
        u'У': u'U',
        u'Ф': u'F',
        u'Х': u'H',
        u'Ъ': u'',
        u'Ы': u'Y',
        u'Ь': u'',
        u'Э': u'E',
    }

    capital_letters_transliterated_to_multiple_letters = {
        u'Ж': u'Zh',
        u'Ц': u'Ts',
        u'Ч': u'Ch',
        u'Ш': u'Sh',
        u'Щ': u'Sch',
        u'Ю': u'Yu',
        u'Я': u'Ya',
    }

    lower_case_letters = {
        u'а': u'a',
        u'б': u'b',
        u'в': u'v',
        u'г': u'g',
        u'д': u'd',
        u'е': u'e',
        u'ё': u'e',
        u'ж': u'zh',
        u'з': u'z',
        u'и': u'i',
        u'й': u'y',
        u'к': u'k',
        u'л': u'l',
        u'м': u'm',
        u'н': u'n',
        u'о': u'o',
        u'п': u'p',
        u'р': u'r',
        u'с': u's',
        u'т': u't',
        u'у': u'u',
        u'ф': u'f',
        u'х': u'h',
        u'ц': u'ts',
        u'ч': u'ch',
        u'ш': u'sh',
        u'щ': u'sch',
        u'ъ': u'',
        u'ы': u'y',
        u'ь': u'',
        u'э': u'e',
        u'ю': u'yu',
        u'я': u'ya',
    }

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items(
    ):
        string = re.sub(r"%s([а-я])" % cyrillic_string, r'%s\1' % latin_string,
                        string)

    for dictionary in (capital_letters, lower_case_letters):
        for cyrillic_string, latin_string in dictionary.items():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items(
    ):
        string = string.replace(cyrillic_string, latin_string.upper())

    return string


def normalize_phone(phone):
    """
    Нормализация номера телефона
    """
    return ''.join([s for s in phone if s.isdigit()])


def normalize_float(x):  # pylint: disable=invalid-name
    """
    Нормализация строки, содержащей число float
    """
    return ''.join([s for s in x if s.isdigit() or s in ('.', '-')])


def send_mail_after_user_register(email, username, password):
    """
    Отправка email об успешной регистрации пользователя
    :param email: адрес email
    :param username: логин пользователя
    :param password: пароль
    """
    context = {'username': username, 'password': password}
    body = f"""
         Добрый день!

         Вы успешно зарегистрировались на сайте dari-cosmetics.ru.

         Данные для доступа в ваш личный кабинет:

         Логин: {username}
         Пароль: {password}

        С уважением,
        Интернет-магазин dari-cosmetics.ru"""
    send_mail.delay(recipient_list=[
        email,
    ],
                    subject='Завершение регистрации на dari-cosmetics.ru',
                    plain_text=body,
                    template_name='reg_complete.html',
                    context=context)


def get_random_email():
    """генерация рандомного email"""
    return uuid.uuid4().hex[:10] + '@' + uuid.uuid4().hex[:10] + '.' + uuid.uuid4().hex[:10]
