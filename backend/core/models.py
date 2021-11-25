"""
Base models, options, refs, etc.
"""
import logging
import uuid

import requests
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.safestring import mark_safe
from requests.exceptions import (ConnectionError, ConnectTimeout, HTTPError,  # pylint: disable=redefined-builtin
                                 ReadTimeout)
from core.utils import get_next_id

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('core')  # pylint: disable=invalid-name

SMS_SEND_STATES = {
    'sms_sent': {
        'code': 0,
        'message': 'SMS успешно отправлено!'
    },
    'connection_error': {
        'code': -1,
        'message': 'Ошибка соединения с SMS-сервисом!'
    },
    'auth_error': {
        'code': -2,
        'message': 'Не найдены данные аутентификации!'
    },
    'unknown_error': {
        'code': -3,
        'message': 'Неизвестная ошибка отправки SMS!'
    },
}


class BaseModel(models.Model):
    """
       Базовая модель
    """
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name='ID')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True,
                                   verbose_name='Дата последнего изменения')
    deleted = models.DateTimeField(null=True,
                                   default=None,
                                   verbose_name='Дата удаления')

    def get_next_seq_no(self):
        """
        Генератор порядковых номеров
        """
        params = dict(app_label=self._meta.app_label,
                      model_name=self._meta.label_lower.split('.')[1],
                      min_val=0,
                      max_val=0,
                      step=1)
        new_id = get_next_id(params)
        return new_id

    class Meta:
        abstract = True


class Options(BaseModel):
    """
        Настройки приложения, изменяемые пользователем
    """
    STRING = 0
    DATETIME = 1
    BOOLEAN = 2
    DECIMAL = 3

    OPTION_TYPES = (
        (STRING, 'Текст'),
        (DATETIME, 'Дата/время'),
        (BOOLEAN, 'Логический тип'),
        (DECIMAL, 'Число'),
    )

    name = models.CharField(max_length=255,
                            blank=False,
                            verbose_name='Краткое наименование настройки')
    long_name = models.CharField(max_length=255,
                                 blank=False,
                                 verbose_name='Полное наименование настройки')
    data_type = models.IntegerField(choices=OPTION_TYPES, default=STRING)
    str_val = models.CharField(max_length=255,
                               null=True,
                               verbose_name='Текстовое значение')
    bool_val = models.NullBooleanField(
        verbose_name='Значение логического типа')
    dt_val = models.DateTimeField(null=True,
                                  verbose_name='Значение типа дата/время')
    dec_val = models.DecimalField(null=True,
                                  default=None,
                                  decimal_places=2,
                                  max_digits=10,
                                  verbose_name='Значение поля числового типа')

    def get_option_val(self, option_name):
        """
        Получение значения настройки
        """
        val = None
        if self.str_val is not None:
            val = self.str_val
        elif self.bool_val is not None:
            val = self.bool_val
        elif self.dt_val is not None:
            val = self.dt_val
        elif self.dec_val is not None:
            val = self.dec_val
        val = val if val is not None else settings.OPTIONS_DEFAULT_VALUES.get(
            option_name, None)
        return val

    class Meta:
        verbose_name = 'Настройка сайта, изменяемая администратором'
        verbose_name_plural = 'Настройки сайта, изменяемые администратором'
        db_table = 'core_options'


class ServiceParam(BaseModel):
    """
        Логины и пароли к внешним API
    """
    service_name = models.CharField(max_length=255,
                                    blank=False,
                                    verbose_name='Наименование сервиса')
    param_name = models.CharField(max_length=255,
                                  blank=False,
                                  verbose_name='Наименование параметра')
    param_value = models.CharField(max_length=255,
                                   blank=False,
                                   verbose_name='Значение параметра')

    class Meta:
        db_table = 'core_service_params'
        verbose_name = 'Данные для доступа к внешним API'
        verbose_name_plural = 'Данные для доступа к внешним API'


class BaseImage(BaseModel):
    """
    Базовая модель для использования изображений
    """
    def image_tag(self):
        """
        Генерация ссылки на превью
        :return:
        """
        return mark_safe(
            f'<img src="{settings.MEDIA_URL}{self.image}" width="100" height="100" />'
        )

    image_tag.short_description = 'Превью'

    class Meta:
        abstract = True


class OKSM(models.Model):
    """
        Общероссийский классификатор стран мира
    """
    short_name = models.CharField(max_length=255,
                                  blank=False,
                                  verbose_name='Краткое наименование')
    full_name = models.CharField(max_length=255,
                                 blank=False,
                                 verbose_name='Полное наименование')
    alfa2 = models.CharField(max_length=2,
                             blank=False,
                             verbose_name='Двухсимвольный код')
    alfa3 = models.CharField(max_length=2,
                             blank=False,
                             verbose_name='Трехсимвольный код')

    class Meta:
        db_table = 'core_oksm'
        managed = False


class Bonus1CRawData(BaseModel):
    """
        Необработанные данные о бонусных балансах из 1С
    """
    seq_no = models.BigIntegerField(
        verbose_name='Порядковый номер в массиве запроса')
    data = JSONField()

    class Meta:
        db_table = 'core_1c_raw_data'


class SendedSMS(models.Model):
    """
    Отправленные клиентам SMS
    """
    CONFIRM = 0
    INFO = 1
    EDIT_PHONE = 2
    EDIT_PASSWORD = 3
    RESTORE_PASSWORD = 4

    SMS_TYPES = ((CONFIRM, 'SMS для подтверждения номер телефона'),
                 (INFO, 'Информационное SMS'),
                 (EDIT_PHONE, 'SMS для изменения номера телефона'),
                 (EDIT_PASSWORD, 'SMS для изменения пароля'),
                 (RESTORE_PASSWORD, 'Восстановление доступа'))

    msisdn = models.CharField(blank=True, max_length=20)
    message = models.CharField(blank=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(blank=True, max_length=255)
    sms_id = models.CharField(blank=True, max_length=255)
    sms_type = models.CharField(blank=True, max_length=20, choices=SMS_TYPES)

    class Meta:
        verbose_name = 'Отправленное SMS'
        verbose_name_plural = 'Отправленные SMS'
        db_table = 'core_sended_sms'


def get_service_params(service_name, param_names):
    """
    Получение параметров доступа к внешним сервисам
    :param service_name: наименование сервиса
    :param param_names: массив наименований параметров
    :return: словарь наименование_параметра: значение параметра
    """
    params = {}
    for param_name in param_names:
        try:
            params[param_name] = ServiceParam.objects.get(
                service_name=service_name, param_name=param_name).param_value
        except ObjectDoesNotExist:
            params[param_name] = None
            logger.error(
                f'Не найден параметр {param_name} для сервиса {service_name}!')
    return params


def get_token_1c():
    """
    Получение токена 1С
    """
    token_1c = get_service_params('1c', ('token', ))
    return token_1c.get('token', '')


def send_sms(msisdn, message):
    """
    Процедура отправки SMS
    :param msisdn: номер, на который отправляется SMS
    :param message: текст SMS
    :param sms_type: тип SMS
    :return: словарь {'message': message, 'status': code}
    """
    def get_error_code_message(err_type):
        code = SMS_SEND_STATES.get(err_type)['code']
        message = SMS_SEND_STATES.get(err_type)['message']
        return code, message

    def check_response(resp_json, msisdn):
        """
        Получение ID SMS из ответа SMS.RU или кода и описания ошибки
        :param resp_json: ответ на запрос отправки SMS в JSON
        :return: code (код ошибки), message (сообщение об ошибке), sms_id (id SMS)
        """
        sms_id = None
        code, message = get_error_code_message('unknown_error')

        status = resp_json.get('status')
        if status == 'ERROR':
            message = resp_json.get("status_text", message)
        else:
            sms = resp_json.get('sms')
            if sms and isinstance(sms, dict):
                msisdn = sms.get(msisdn)
                if msisdn and isinstance(msisdn, dict):
                    status = msisdn.get('status')
                    if status == 'ERROR':
                        message = msisdn.get('status_text', message)
                    else:
                        sms_id = msisdn.get('sms_id')
        if sms_id:
            code, message = get_error_code_message('sms_sent')
        return code, message, sms_id

    smsru_params = get_service_params(service_name='smsru',
                                      param_names=('api_id', ))
    api_id = smsru_params.get('api_id')
    if not api_id:
        code, message = get_error_code_message('auth_error')
        logger.error(message)
        return {'message': message, 'status_code': code}
    sms_url = f'https://sms.ru/sms/send?api_id={api_id}&to={msisdn}&msg={message}&json=1'
    try:
        resp = requests.get(url=sms_url, verify=False, timeout=(3, 3))
        if resp.status_code == 200:
            resp_json = resp.json()
            code, message, _ = check_response(resp_json, msisdn)
        else:
            code, message = get_error_code_message('unknown_error')
            logger.error(
                f'Ошибка отправки SMS: {resp.status_code} : {resp.text}')
    except (ConnectTimeout, ReadTimeout, ConnectionError, HTTPError):
        logger.exception(f'Ошибка соединения с SMS-сервисом!')
        code, message = get_error_code_message('connection_error')
    logger.info(f'send sms msisdn {msisdn}, message: {message}, code: {code}')
    return {'message': message, 'status': code}


class ImagePreviewModelMixin:
    """Mixin, содержащий метод отображения превью изображения в админке"""
    def image_tag(self):
        return mark_safe(
            f'<img src="{settings.MEDIA_URL}{self.image}" width="100" height="100" />'
        )
    image_tag.short_description = 'Превью'


class AutoIncHitCountModelMixin:
    """Mixin, содержащий метод автоувеличения количества
    просмотров страницы с описанием объекта"""
    def inc_hit_count(self):
        """Метод увеличения количества просмотров"""
        self.hit_count += 1
        self.save()
