"""
AmoCRM signals
"""
from django.db.models import signals

from amocrm.models import RequestType, RequestsQueue, RequestStatus
from .models import AppUser


def user_post_save(sender, instance, created, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Создание контакта в amoCRM после регистрации пользователя
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    name = f'{getattr(instance, "last_name", "")} {getattr(instance, "first_name", "")} ' \
        f'{getattr(instance, "patronymic", "")}'
    phone = instance.phone
    email = instance.email
    if created:
        RequestsQueue.objects.create(user_id=instance.id,
                                     req_type_id=RequestType.ADD_CONTACT,
                                     status_id=RequestStatus.PROCESSING,
                                     params={
                                         'name': name,
                                         'phone': phone,
                                         'email': email,
                                         'tags': ''
                                     })
    else:
        params = {
            'contact_id': instance.contact_id,
            'name': name,
            'phone': phone,
            'email': email,
            'tags': '',
        }
        if not RequestsQueue.objects.filter(
                user_id=instance.id,
                req_type_id=RequestType.EDIT_CONTACT,
                params=params).exists():
            RequestsQueue.objects.create(user_id=instance.id,
                                         req_type_id=RequestType.EDIT_CONTACT,
                                         status_id=RequestStatus.PROCESSING,
                                         params=params)


signals.post_save.connect(user_post_save, sender=AppUser)
