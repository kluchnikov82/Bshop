"""
Common Celery tasks
"""
from __future__ import absolute_import, unicode_literals

import logging
import os
import subprocess

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('core')  # pylint: disable=invalid-name


@shared_task
def send_mail(recipient_list, subject, plain_text, template_name, context):
    """
        Процедура отправки email
    """
    html_message = render_to_string(template_name, context)

    django_send_mail(subject=subject,
                     message=plain_text,
                     from_email=settings.DEFAULT_FROM_EMAIL,
                     recipient_list=recipient_list,
                     html_message=html_message)
    logger.info(
        f'Email sent: recipient_list: {recipient_list}, subject: {subject}')


@shared_task
def send_plain_text_mail(recipient_list, subject, message, attachments=None):
    """
        Процедура отправки email с вложениями
    """
    email = EmailMessage(subject=subject,
                         body=message,
                         from_email=settings.EMAIL_HOST_USER,
                         to=recipient_list)
    if attachments:
        for file_name in attachments:
            if os.path.isfile(settings.MEDIA_ROOT + file_name):
                email.attach_file(settings.MEDIA_ROOT + file_name)
            else:
                logger.error(
                    f'При попытке вложения в email не найден файл {file_name}!'
                )
    email.send()
    logger.info(
        f'Email sent: {recipient_list}: recipient_list, subject: {subject}')


@shared_task
def sitemap_generate(filename):
    """
    Генерация sitemap и копирование в папку сайта
    :return:
    """
    script_name = settings.SITEMAP_GENERATE_PATH
    args = ['node', script_name]
    sitemap_generate_process = subprocess.run(args)
    if sitemap_generate_process.returncode == 0:
        logger.info('sitemap сгенерирован успешно')
        args = ['sudo', 'cp', 'sitemap.xml', settings.SITE_DIR]
        copy_sitemap_process = subprocess.run(args)
        if copy_sitemap_process.returncode == 0:
            logger.info('sitemap скопирован успешно')
        else:
            logger.error(f'Ошибка копирования sitemap, код {copy_sitemap_process.returncode}')
            logger.error(copy_sitemap_process.stdout)
    else:
        logger.error(f'Ошибка генерации sitemap, код {sitemap_generate_process.returncode}')
        logger.error(sitemap_generate_process.stdout)
