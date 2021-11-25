"""
Shop celery tasks
"""
from __future__ import absolute_import, unicode_literals

import logging
import uuid

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string

from amocrm.client import CRMClient
from amocrm.models import RequestsQueue, RequestStatus, RequestType
from appuser.models import Referral
from core.models import get_service_params
from .cdek import CDEKClient, City
from .messages import get_order_created_message, get_order_updated_message
from .models import AdviceType, ReferrerOrder

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


def check_contact_exists(phone, email, name, user_id):
    """
    Процедура проверки существования контакта с указанным номером телефона в amoCRM
    :param phone: телефон
    :param email: email
    :param name: ФИО контакта
    :param user_id: идентфикатор пользователя в AppUser
    :return: contact_id:       id контакта в amoCRM, если он существует или None, если не существует;
             child_request_id: id запроса к API amoCRM а создание контакта
    """
    params = {'query': phone}
    c = CRMClient()  # pylint: disable=invalid-name
    c.do_auth()
    result = c.process_request(RequestType.GET_CONTACT, params)
    if result['status'] == 'ok' and 'result' in result \
            and 'items' in result['result'] and len(result['result']['items']) > 0:
        # если контакты с указанным номером существуют, выбираем из них самый старый
        contact_id = sorted(result['result']['items'],
                            key=lambda d: d['created_at'])[0]['id']
        logger.debug(f'Найден контакт в amoCRM. contact_id: {contact_id}')
        child_request_id = None
    else:
        # если контакты с указанным номером телефона отсутствует в amoCRM, добавляем запрос на создание контакта
        params = {'phone': phone, 'email': email, 'name': name}
        logger.debug(
            f'Параметры запроса на создание контакта в amoCRM: {params}')
        req_add_contact = RequestsQueue.objects.create(
            user_id=user_id,
            req_type_id=RequestType.ADD_CONTACT,
            status_id=RequestStatus.PROCESSING,
            params=params)
        contact_id = None
        child_request_id = req_add_contact.id
    return contact_id, child_request_id


@shared_task
def send_email(subject, message, template, context, recipient_list):
    """
    Отправка email
    """
    django_send_mail(subject=subject,
                     message=message,
                     from_email=settings.EMAIL_HOST_USER,
                     recipient_list=recipient_list,
                     html_message=render_to_string(template, context=context))

    logger.info(f'Письмо отправлено {recipient_list}')


@shared_task
def post_create_order(order, referrer, user_id, created=True):  # pylint: disable=too-many-locals
    """
    Создание привязки заказа к реферреру, создание сделки в amoCRM
    :param order: словарь, содержащий параметры заказа
    :param referrer: id реферрера
    :param user_id: id пользователя, создавшего заказ
    :return:
    """
    order_id = order.get('order_id')
    order_no = order.get('order_no')
    total_amount = order.get('total_amount')
    phone = order.get('phone')
    email = order.get('email')
    address = order.get('address')
    name = order.get('name')
    memo = order.get('memo')
    order_link = order.get('order_link')
    shipping_amount = order.get('shipping_amount')

    ReferrerOrder.objects.filter(order_id=order_id).delete()
    if referrer:
        referrer_id = uuid.UUID(referrer) if isinstance(referrer, str) else referrer
        # если заказ создан после перехода по реферральной ссылке, создаем привязку заказа к реферреру
        logger.debug(f'Реферальный заказ {order_no}, referrer_id: {referrer}')
        ReferrerOrder.objects.create(order_id=order_id,
                                     referrer_id=referrer_id)
        logger.debug(
            f'Добавлена запись в ReferrerOrder. order_id: {order_id}, referrer_id: {referrer}'
        )
        if user_id:
            # если заказ создан после перехода по реферральной ссылке зарегистрированным пользователем,
            # создаем привязку пользователя к реферреру, и за все последующие его заказы начисляем реферреру бонус
            if not Referral.objects.filter(referral_id=user_id).exists():
                r = Referral.objects.create(referrer_id=referrer_id,  # pylint: disable=invalid-name
                                            referral_id=user_id)
                logger.debug(
                    f'Создана привязка реферала к пользователю ID {r.id}')
    else:
        if user_id:
            # если заказ создан зарегистрированным пользователем без реферральной ссылки, проверяем, привязан
            # ли он к реферреру, и если да - создаем привязку заказа к реферреру
            try:
                r = Referral.objects.get(referral_id=user_id)  # pylint: disable=invalid-name
                ReferrerOrder.objects.create(order_id=order_id,
                                             referrer_id=r.referrer_id)
                logger.debug(
                    f'Добавлена запись в ReferrerOrder. order_id: {order_id}, referrer_id: {r.referrer_id}'
                )
            except ObjectDoesNotExist:
                pass

    # проверяем, существует ли контакт с номером телефона, на который оформлен заказ, в amoCRM
    contact_id, child_request_id = check_contact_exists(
        phone, email, name, user_id)

    # создание запроса на добавление сделки в amoCRM
    params = {
        'contact_id': contact_id,
        'lead_name': order_no,
        'sale': str(total_amount),
        'address': address,
        'href': order_link,
        'memo': memo,
        'tags': 'заказнасайте'
    }
    logger.debug(f'Параметры запроса на создание сделки в amoCRM: {params}')
    RequestsQueue.objects.create(user_id=user_id,
                                 req_type_id=RequestType.ADD_LEAD,
                                 status_id=RequestStatus.PROCESSING,
                                 params=params,
                                 comment=order_no,
                                 child_request_id=child_request_id)
    logger.debug(f'Запрос на создание сделки создан')

    # отправка email со ссылкой на заказ
    context = {
        'order_no': order_no,
        'total_amount': total_amount,
        'order_link': order_link
    }
    order_sum = total_amount + shipping_amount
    if created:
        message = get_order_created_message(
            order_no,
            order_sum,
            order_link)
        template_name = 'order_created.html'
        subject = f'Новый заказ {order_no} на dari-cosmetics.ru'
    else:
        message = get_order_updated_message(
            order_no,
            order_sum,
            order_link)
        template_name = 'order_updated.html'
        subject = f'Изменение заказа {order_no} на dari-cosmetics.ru'
    send_email(subject=subject,
               message=message,
               template=template_name,
               context=context,
               recipient_list=(email, ))
    logger.debug(f'Отправлен email со ссылкой на заказ {order_no} на {email}')


@shared_task
def post_create_advice(advice, user_id):
    """
    Создание сделки в amoCRM после создания запроса на консультацию
    :param advice: словарь, содержащий параметры сделки
    :param user_id: d пользователя
    :return:
    """
    advice_type_id = advice['advice_type_id']
    phone = advice['phone']
    email = advice['email']
    name = advice['name']
    text = advice['feedback']

    try:
        advice_type = AdviceType.objects.get(id=advice_type_id)
        advice_type_name = advice_type.type_name
        advice_tag = advice_type.tag
    except KeyError:
        advice_type_name = ''
        advice_tag = 'сайт'

    contact_id, child_request_id = check_contact_exists(
        phone, email, name, user_id)

    # создание запроса на добавление сделки в amoCRM
    params = {
        'contact_id': contact_id,
        'lead_name': f'Консультация на тему {advice_type_name}',
        'feedback': text,
        'tags': advice_tag
    }
    logger.debug(f'Параметры запроса на создание сделки в amoCRM: {params}')
    RequestsQueue.objects.create(user_id=user_id,
                                 req_type_id=RequestType.ADD_LEAD,
                                 status_id=RequestStatus.PROCESSING,
                                 params=params,
                                 child_request_id=child_request_id)
    logger.debug(f'Запрос на создание сделки создан')


@shared_task
def get_cdek_cities_list():
    """
        Процедура получения/обновления списка городов в ИС СДЭК
    """
    cdek_params = get_service_params('cdek', ('login', 'password'))
    c = CDEKClient(login=cdek_params.get('login'),  # pylint: disable=invalid-name
                   secure=cdek_params.get('password'))
    data = c.get_city('')
    for item in data:
        city_code = item.pop('cityCode')
        City.objects.update_or_create(cityCode=city_code, defaults={**item})
    logger.info(f'Список городов СДЭК обновлен')
