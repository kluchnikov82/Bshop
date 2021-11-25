"""
Сохранение аватара из Facebook в профиле пользователя
"""
import os
import uuid

import requests
from django.core.files import File


def get_fb_user_avatar(backend, details, response, uid, user, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Pipeline сохранения аватара FB
    """
    url = None
    if getattr(backend, 'name', None) == 'facebook':
        url = 'http://graph.facebook.com/%s/picture?type=large' % response['id']

    if url:
        tmp_file_name = f'/tmp/{uuid.uuid4()}.jpg'
        result = requests.get(url)
        with open(tmp_file_name, 'wb') as f:  # pylint: disable=invalid-name
            f.write(result.content)
        reopen = open(tmp_file_name, 'rb')
        file = File(reopen)
        user.avatar.save('avatar.jpg', file, save=True)
        reopen.close()
        os.remove(tmp_file_name)
