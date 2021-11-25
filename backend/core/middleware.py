"""
Self made middlewares
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

from .models import Options


class AutoLogout:
    """
    Автологаут по истечении периода времени
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_authenticated_user(request):
            user = None
            if not request.user.is_authenticated:
                token = request.META.get('HTTP_AUTHORIZATION',
                                         " ").split(' ')[1]
                data = {'token': token}
                try:
                    valid_data = VerifyJSONWebTokenSerializer().validate(data)
                    user = valid_data['user']
                except ValidationError:
                    pass
            else:
                user = request.user
            return user

        user = get_authenticated_user(request)
        option_name = 'auto_logout_delay'
        if user is not None:
            try:
                try:
                    o = Options.objects.get(name=option_name,  # pylint: disable=invalid-name
                                            deleted__isnull=True)
                    auto_logout_delay = o.get_option_val(option_name)
                except ObjectDoesNotExist:
                    auto_logout_delay = settings.OPTIONS_DEFAULT_VALUES.get(
                        option_name, None)
                if datetime.now() - datetime.strptime(request.session['last_action'], '%Y%m%d%H%M%S%f') > \
                        timedelta(0, auto_logout_delay * 60, ):
                    del request.session['last_action']
                    try:
                        user.auth_token.delete()
                    except (AttributeError, ObjectDoesNotExist):
                        pass
                    user.jwt_update_secret_key()
                    django_logout(request)
                else:
                    request.session['last_action'] = datetime.now().strftime(
                        '%Y%m%d%H%M%S%f')
            except KeyError:
                request.session['last_action'] = datetime.now().strftime(
                    '%Y%m%d%H%M%S%f')

        response = self.get_response(request)
        return response
