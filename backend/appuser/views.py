"""
Appuser views
"""
import logging
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone as tz
from djmoney.models.fields import Money
from requests.exceptions import (ConnectionError, ConnectTimeout, HTTPError,  # pylint: disable=redefined-builtin
                                 ReadTimeout)
from rest_auth.app_settings import PasswordChangeSerializer
from rest_auth.utils import jwt_encode
from rest_auth.views import LogoutView, PasswordChangeView
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.views import ObtainJSONWebToken
from social_core.exceptions import AuthTokenError, AuthTokenRevoked
from social_django.utils import psa

from core.models import get_token_1c
from core.utils import (get_decimal, normalize_float,
                        send_mail, normalize_phone,
                        send_mail_after_user_register)
from core.views import ListView, RUDView
from shop.models import BonusParams
from .models import (AppUser, Bonus1CChangeHistory, PasswordResetReqeust,
                     ReferrerOrder, Referral, BonusChangeHistory)



from .serializers import (AppUserRegisterSerializer, ReferrerOrderSzr,
                          User1CSzr, UserEditSzr, UserGetSzr,
                          ReferralSzr, BonusChangeHistorySzr)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('appuser')  # pylint: disable=invalid-name


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Формирование ответа на запрос аутентификации по JWT-токену
    :param token: JWT-токен
    :param user: объект AppUser
    :param request: запрос
    """
    return {'token': token, 'user': UserGetSzr(user).data}


class MyObtainJSONWebToken(ObtainJSONWebToken):
    """
    Login, генерация токена
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            request.session['last_action'] = datetime.now().strftime(
                '%Y%m%d%H%M%S%f')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyLogoutView(LogoutView):
    """
    Logout, декативация токена
    """
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if request.user.id is not None:
            request.user.jwt_update_secret_key()
        django_logout(request)
        return Response(data={'message': 'Выход из системы выполнен успешно!'},
                        status=status.HTTP_200_OK)


class AppUserView(RUDView):
    """
    Профиль пользователя - retrieve, update
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = UserGetSzr
    queryset = AppUser.objects.all()
    lookup_field = 'id'
    szrs = (UserGetSzr, UserEditSzr, UserGetSzr)

    def update(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.szrs[1](instance,
                                  data=request.data,
                                  partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}  # pylint: disable=protected-access
        resp = UserGetSzr(instance).data
        return Response(resp)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id != instance.id:
            return Response(data={
                'message':
                'Отсутствуют права на просмотр профиля пользователя!'
            },
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyPasswordChangeView(PasswordChangeView):
    """
    Изменение пароля
    """
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={'message': 'Пароль изменен успешно!'},
                        status=status.HTTP_200_OK)


class AppUserCreateView(generics.CreateAPIView):
    """
    Создание пользователя
    """
    permission_classes = (AllowAny, )
    serializer_class = UserGetSzr
    queryset = AppUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = AppUserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(self.request)
        password = request.data.get('password1')
        send_mail_after_user_register(user.email, user.username, password)
        token = jwt_encode(user)
        data = jwt_response_payload_handler(token, user, self.request)
        return Response(data=data, status=status.HTTP_201_CREATED)


