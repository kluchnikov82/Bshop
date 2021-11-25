"""
Amocrm celery tasks
"""
from __future__ import absolute_import, unicode_literals

import logging
import time

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone as tz

from appuser.models import AppUser

from .client import CRMClient
from .models import Contact, RequestsQueue, RequestStatus, RequestType

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('amocrm')  # pylint: disable=invalid-name


@shared_task
def job_process_requests():  # pylint: disable=too-many-branches
    """
        Джоб celery, выполняющий запросы из очереди к API amoCRM
    """
    # TODO: рефакторинг [too-many-branches]
    started = time.time()
    logger.info('Начало работы джоба выполнения запросов к amoCRM')
    requests = RequestsQueue.objects.filter(
        status_id__in=(RequestStatus.PROCESSING,
                       RequestStatus.COMPLETED_WITH_ERROR),
        restart_count__lte=60).order_by('-created')
    requests_count = len(requests)
    if requests_count > 0:
        c = CRMClient()  # pylint: disable=invalid-name
        c.do_auth()
        logger.info('Создан CRM клиент')
        for r in requests:  # pylint: disable=invalid-name
            logger.debug(
                f'Тип запроса: {r.req_type_id}, параметры запроса: {r.params}')
            child_request_status_id = RequestStatus.COMPLETED_SUCCESSFULLY
            child_request_id = 0

            if r.child_request is not None:
                try:
                    child_request = RequestsQueue.objects.get(
                        id=r.child_request.id)
                    child_request_status_id = child_request.status.id
                    child_request_id = child_request.id
                except ObjectDoesNotExist:
                    pass

            if child_request_status_id == RequestStatus.COMPLETED_SUCCESSFULLY:
                # если в параметрах запроса на редактирование контакта отсутствует contact_id,
                # пытаемся добыть его из запроса на добавление контакта
                if r.req_type_id == RequestType.EDIT_CONTACT:
                    contact_id = r.params.get('contact_id', None)
                    if contact_id is None:
                        add_contact_request = RequestsQueue.objects.filter(
                            user_id=r.user_id,
                            req_type_id=RequestType.ADD_CONTACT,
                            status_id=RequestStatus.COMPLETED_SUCCESSFULLY
                        ).order_by('updated').last()
                        if hasattr(add_contact_request, 'response'):
                            contact_id = add_contact_request.response.get(
                                'contact_id', None)
                            r.params['contact_id'] = contact_id
                            r.save()

                result = c.process_request(r.req_type_id, params=r.params)

                logger.debug(f'result: {result}')

                if result['status'] == 'ok':
                    r.response = result['result']
                    if r.req_type_id == RequestType.ADD_CONTACT:
                        contact_id = result['result']['contact_id']
                        user_id = getattr(r, 'user_id', None)
                        Contact.objects.update_or_create(
                            crm_id=contact_id, defaults={'user_id': user_id})
                        if user_id:
                            AppUser.objects.filter(id=user_id).update(
                                contact_id=contact_id)

                        parent_requests = RequestsQueue.objects.filter(child_request=r.id) | \
                            RequestsQueue.objects.filter(user_id=r.user_id, req_type_id=RequestType.EDIT_CONTACT)

                        for p in parent_requests:  # pylint: disable=invalid-name
                            if 'contact_id' in p.params:
                                p.params['contact_id'] = contact_id
                                p.save()

                    if r.req_type_id == RequestType.ADD_LEAD:
                        pass

                    r.status_id = RequestStatus.COMPLETED_SUCCESSFULLY
                    r.error_code = None
                    r.error_desc = None
                else:
                    r.status_id = RequestStatus.COMPLETED_WITH_ERROR
                    r.error_code = result['result']['err_code']
                    r.error_desc = result['result']['err_desc']
                    r.restart_count += 1
                r.updated = tz.now()
                r.save()
            else:
                logger.warning(
                    f'Дочерний запрос {child_request_id} еще не выполнен!')
    requests_time = time.time() - started
    logger.info(
        f'Завершение работы джоба выполнения запросов к amoCRM. Обработано {requests_count} '
        f'запросов за {requests_time:.2f} секунд\n\n')
