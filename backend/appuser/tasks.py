"""
Appuser celery tasks
"""
from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone as tz

from appuser.models import AppUser
from shop.models import BonusParams

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('appuser')  # pylint: disable=invalid-name


@shared_task
def job_change_user_target():
    """
    Джоб изменения параметров расчета целевого показателя и самого целевого показателя на основании объема продаж
    и начислений на бонусный баланс за прошлый период
    """
    logger.info('Начало работы джоба расчета целевого показателя клиентов')
    with transaction.atomic():
        users = AppUser.objects.filter(
            partner_type_id=AppUser.DISTRIBUTOR).select_for_update()
        users_count = len(users)
        for user in users:
            logger.debug(
                f'user_id: {user.id}, new_last_period_sale_amount: {user.current_period_sale_amount.amount}, '
                f'new_last_period_bonus_payments: {user.current_period_bonus_payments.amount}'
            )

            new_current_period_payments = 0
            new_last_period_sale_amount = user.current_period_sale_amount.amount
            new_last_period_bonus_payments = user.current_period_bonus_payments.amount
            new_last_period_payments = user.current_period_payments.amount

            user.last_period_sale_amount.amount = new_last_period_sale_amount
            user.last_period_bonus_payments.amount = new_last_period_bonus_payments
            user.last_period_payments.amount = new_last_period_payments

            user.current_period_payments.amount = new_current_period_payments

            user.current_period_sale_amount.amount = 0
            user.current_period_bonus_payments.amount = 0
            user.current_period_payments.amount = 0

            new_current_target = new_current_period_payments + new_last_period_sale_amount - \
                new_last_period_bonus_payments

            user.current_target.amount = new_current_target
            user.save()

            try:
                bp = BonusParams.objects.filter(  # pylint: disable=invalid-name
                    started__lte=tz.now(),
                    ended__gte=tz.now(),
                    partner_type_id=user.partner_type_id,
                    target__lte=new_current_target).order_by(
                        '-target').first()
                user.current_discount = bp.discount
                user.current_bonus_share = bp.bonus_share
                user.save()
            except ObjectDoesNotExist:
                logger.error(
                    f'Не найден целевой показатель для параметров partner_type_id: {user.partner_type_id}, '
                    f'target: {new_current_target}!')
    logger.info(f'Обработано {users_count} аккаунтов')
    logger.info('Завершение работы джоба расчета целевого показателя клиентов')
