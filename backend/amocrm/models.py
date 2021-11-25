"""Amocrm models"""
from django.contrib.postgres.fields import JSONField
from django.db import models

from appuser.models import AppUser
from core.models import BaseModel


class RequestType(models.Model):
    """
    Тип запроса к AmoCRM
    """
    ADD_CONTACT = 0
    EDIT_CONTACT = 1
    ADD_LEAD = 2
    EDIT_LEAD = 3
    AUTH = 4
    GET_ACCOUNT_INFO = 5
    ADD_PRODUCT = 6
    EDIT_PRODUCT = 7
    GET_CONTACT = 8

    REQ_TYPES = (
        (ADD_CONTACT, 'Добавление контакта'),
        (EDIT_CONTACT, 'Редактирование контакта'),
        (ADD_LEAD, 'Добавление сделки'),
        (EDIT_LEAD, 'Редактирование сделки'),
        (AUTH, 'Аутентификация'),
        (GET_ACCOUNT_INFO, 'Получение данных аккаунта'),
        (GET_CONTACT, 'Получение ID контакта'),
    )

    req_type = models.IntegerField(choices=REQ_TYPES,
                                   verbose_name='Код типа запроса')
    description = models.CharField(max_length=255,
                                   blank=False,
                                   verbose_name='Описание типа запроса')

    class Meta:
        verbose_name = 'Тип запроса к amoCRM'
        verbose_name_plural = 'Типы запросов к amoCRM'
        db_table = 'crm_request_type'


class RequestStatus(models.Model):
    """
    Статус запроса к AmoCRM
    """
    PROCESSING = 0
    COMPLETED_SUCCESSFULLY = 1
    COMPLETED_WITH_ERROR = 2

    REQ_STATES = ((PROCESSING, 'В обработке'), (COMPLETED_SUCCESSFULLY,
                                                'Выполнен успешно'),
                  (COMPLETED_WITH_ERROR, 'Выполнен с ошибкой'))

    req_status = models.IntegerField(choices=REQ_STATES,
                                     verbose_name='Код статуса запроса')
    description = models.CharField(max_length=255,
                                   blank=False,
                                   verbose_name='Описание статуса запроса')

    class Meta:
        verbose_name = 'Статус запроса к amoCRM'
        verbose_name_plural = 'Статусы запросов к amoCRM'
        db_table = 'crm_request_status'


class RequestsQueue(BaseModel):
    """
    Очередь запросов к AmoCRM
    """
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    updated = models.DateTimeField(default=None,
                                   null=True,
                                   verbose_name='Дата выполнения')
    user = models.ForeignKey(AppUser,
                             null=True,
                             on_delete=models.DO_NOTHING,
                             verbose_name='ID пользователя')
    req_type = models.ForeignKey(RequestType,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Тип запроса')
    status = models.ForeignKey(RequestStatus,
                               on_delete=models.DO_NOTHING,
                               verbose_name='Статус запроса')
    params = JSONField(verbose_name='Параметры запроса',
                       null=True,
                       default=None)
    error_code = models.IntegerField(default=None,
                                     null=True,
                                     verbose_name='Код ошибки')
    error_desc = models.CharField(max_length=255,
                                  default=None,
                                  null=True,
                                  verbose_name='Описание ошибки')
    comment = models.CharField(max_length=255,
                               default=None,
                               null=True,
                               verbose_name='Примечание')
    in_progress = models.BooleanField(
        default=False,
        verbose_name='Признак нахождения запроса в обработке на данный момент')
    restart_count = models.IntegerField(
        default=0, verbose_name='Количество попыток выполнения')
    child_request = models.ForeignKey('self',
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      verbose_name='Предшествующий апрос')
    response = JSONField(verbose_name='Параметры ответа на запрос',
                         null=True,
                         default=None)

    class Meta:
        verbose_name = 'Запрос к amoCRM'
        verbose_name_plural = 'Запросы к amoCRM'
        db_table = 'crm_requests_queue'


class Contact(BaseModel):
    """
    Контакт AmoCRM
    """
    crm_id = models.BigIntegerField(verbose_name='ID контакта в amoCRM')
    user = models.ForeignKey(AppUser,
                             null=True,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Контакт amoCRM'
        verbose_name_plural = 'Контакты amoCRM'
        db_table = 'crm_contact'


class Lead(BaseModel):
    """
    Сделка AmoCRM
    """
    crm_id = models.BigIntegerField(verbose_name='ID сделки в amoCRM')
    contact = models.ForeignKey(Contact,
                                null=True,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Контакт в amoCRM')

    class Meta:
        verbose_name = 'Сделка amoCRM'
        verbose_name_plural = 'Сделки amoCRM'
        db_table = 'crm_lead'
