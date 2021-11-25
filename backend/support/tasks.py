"""
Support celery tasks
"""
from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from django.conf import settings

from amocrm.models import RequestsQueue, RequestStatus
from amocrm.models import RequestType as amoRequestType
from appuser.models import AppUser
from shop.tasks import check_contact_exists

from .models import RequestType

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


@shared_task
def post_create_request(request, user_id):
    """
    Создание записи в очереди на создание сделки в amoCRM после сохранения обращения в support
    :param request: запрос
    :param user_id: id пользователя
    """
    request_type_id = request['request_type_id']
    text = request['text']

    try:
        request_type = RequestType.objects.get(id=request_type_id).description
    except KeyError:
        request_type = ''

    user = AppUser.objects.get(id=user_id)
    if user.contact_id is None:
        contact_id, child_request_id = check_contact_exists(
            user.phone, user.email, user.name, user_id)
    else:
        contact_id = user.contact_id
        child_request_id = None

    # создание запроса на добавление сделки в amoCRM
    params = {
        'contact_id': contact_id,
        'lead_name': f'Обращение в техподдержку "{request_type}"',
        'feedback': text,
        'tags': 'обращение в техподдержку'
    }
    logger.debug(f'Параметры запроса на создание сделки в amoCRM: {params}')
    RequestsQueue.objects.create(user_id=user_id,
                                 req_type_id=amoRequestType.ADD_LEAD,
                                 status_id=RequestStatus.PROCESSING,
                                 params=params,
                                 child_request_id=child_request_id)
    logger.debug(f'Запрос на создание сделки создан')
