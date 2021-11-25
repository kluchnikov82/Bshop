"""
Support models
"""
from django.db import models

from appuser.models import AppUser
from core.models import BaseModel


class RequestType(BaseModel):
    """
    Тип обращения в техподдержку
    """
    description = models.CharField(max_length=255,
                                   verbose_name='Наименование типа обращения')

    class Meta:
        verbose_name = 'Тип обращения в техподдержку'
        verbose_name_plural = 'Типы обращений в техподдержку'
        ordering = ['description']
        db_table = 'support_request_type'

    def __str__(self):
        return self.description


class RequestStatus(BaseModel):
    """
    Статус обращения в техподдержку
    """
    IN_PROGRESS = 0
    INFO = 1
    CLOSED = 2

    REQUEST_STATES = (
        (IN_PROGRESS, 'На рассмотрении'),
        (INFO, 'Запрос информации у пользователя'),
        (CLOSED, 'Закрыто'),
    )

    status = models.PositiveIntegerField(choices=REQUEST_STATES,
                                         default=IN_PROGRESS,
                                         verbose_name='Код статуса',
                                         unique=True)
    description = models.CharField(
        max_length=255, verbose_name='Наименование статуса обращения')

    class Meta:
        verbose_name = 'Статус обращения в техподдержку'
        verbose_name_plural = 'Статусы обращений в техподдержку'
        ordering = ['description']
        db_table = 'support_request_status'

    def __str__(self):
        return self.description


class Request(BaseModel):
    """
    Обращение в техподдержку
    """
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь')
    request_type = models.ForeignKey(RequestType,
                                     on_delete=models.DO_NOTHING,
                                     verbose_name='Тип обращения')
    request_status = models.ForeignKey(RequestStatus,
                                       on_delete=models.DO_NOTHING,
                                       verbose_name='Статус обращения')
    text = models.TextField(max_length=255, verbose_name='Текст обращения')

    class Meta:
        verbose_name = 'Обращение в техподдержку'
        verbose_name_plural = 'Обращения в техподдержку'
        ordering = ['-created']
        db_table = 'support_request'

    def __str__(self):
        return '%s : %s %s %s' % (self.created, self.request_type, self.user,
                                  self.text)
