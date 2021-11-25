"""
Shop views
"""
import datetime
import hashlib
import hmac
import logging
from collections import OrderedDict
from datetime import timedelta

from cdek.api import CDEKClient as FS_CDEK_Client
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone as tz
from djmoney.models.fields import Money
from rest_framework import filters
from rest_framework import status, generics
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser, Bonus1CChangeHistory
from appuser.models import Referral
from core.models import OKSM, ServiceParam, Bonus1CRawData
from core.models import get_service_params, get_token_1c
from core.serializers import OKSMSzr
from core.utils import get_decimal, normalize_phone, normalize_float
from core.views import ListView, LCView, RetrieveHitCountAPIView
from core.views import MultipleFieldLookupMixin
from .cdek import CDEKClient
from .models import ActiveComponent, BonusParams
from .models import AdviceType, Advice
from .models import PayKeeperNotice, Slide, Event
from .models import Payment, PromoCode, FeedbackAll
from .models import Product, Order, Category, SubCategory
from .models import ProductFeedback, KitFeedback, Kit
from .models import SBRequest, SBNotice, DefaultDeliveryPrice
from .paykeeper import PaykeeperClient
from .rp import RPClient
from .serializers import ActiveComponentSzr, SlideSzr, EventSzr
from .serializers import AdviceTypeSzr, AdviceSzr
from .serializers import AllFeedbacksListSzr
from .serializers import CategoryShortSzr
from .serializers import KitFeedbackListSzr, ProductFeedbackListSzr
from .serializers import KitShortSzr, KitDetailSzr
from .serializers import Order1CSzr, PromoCodeSzr
from .serializers import OrderListShortSzr, ProductFeedbackFullSzr
from .serializers import ProductFeedbackSzr, KitFeedbackSzr
from .serializers import ProductSzr, OrderListSzr, CategorySzr
from .serializers import SBNoticeSzr, SubCategorySzr
from .tasks import post_create_advice
from .utils import calc_totals, get_shipping_method_params, get_user_ref_id_from_promo

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


class ViewGetCDEKObjectsList(APIView):
    """Получение списка объектов из базы СДЭК"""
    permission_classes = (AllowAny, )
    cdek_method = ''
    params = []

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument,missing-function-docstring
        fail_resp_text = 'Ошибка выполнения запроса к СДЭК!'
        cdek_client_params = get_service_params('cdek', ('login', 'password'))
        cdek_client = CDEKClient(
            login=cdek_client_params.get('login'),  # pylint: disable=invalid-name
            secure=cdek_client_params.get('password'))
        cdek_client.get_token()
        cdek_query_params = dict()
        for param_name in self.params:
            param_value = request.query_params.get(param_name)
            cdek_query_params[param_name] = param_value
        cdek_method = getattr(cdek_client, self.cdek_method, None)
        if cdek_method:
            data = cdek_method(**cdek_query_params)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=fail_resp_text)
        if not isinstance(data, list):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=fail_resp_text)
        return Response(status=status.HTTP_200_OK, data=data)


class ViewProductList(ListView):
    """Получение списка товаров с паджинацией"""
    serializer_class = ProductSzr
    permission_classes = (AllowAny,)
    paginate = True
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )

    def get_queryset(self):  # pylint: missing-function-docstring
        args = {'deleted__isnull': True}

        ids = self.request.query_params.getlist('id')
        if isinstance(ids, list) and len(ids) > 0:
            args['id__in'] = ids
            self.paginate = False
        if self.request.query_params.get('discount'):
            args['discount__gt'] = 0
        queryset = Product.objects.filter(**args)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class ViewProductListAll(ListView):
    """Получение списка всех товаров без паджинации (по требованию фронта)"""
    serializer_class = ProductSzr
    permission_classes = (AllowAny, )
    queryset = Product.objects.filter(deleted__isnull=True)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class ViewProductDetail(MultipleFieldLookupMixin, RetrieveHitCountAPIView):
    """Получение атрибутов товара"""
    permission_classes = (AllowAny, )
    serializer_class = ProductSzr
    lookup_field = 'id'
    multiple_lookup_fields = ('id', 'slug',)

    def get_queryset(self):
        queryset = Product.objects.filter(deleted__isnull=True)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class ViewOrders(LCView):
    """Создание заказа/просмотр списка заказов"""
    permission_classes = (AllowAny, )
    paginate = True
    serializer_class = OrderListSzr
    szrs = (OrderListSzr, OrderListSzr, OrderListShortSzr)

    def get_queryset(self):  # pylint: missing-function-docstring
        user_id = self.request.user.id
        if user_id:
            queryset1 = Order.objects.filter(user_id=user_id,
                                             status=Order.PAYED,
                                             deleted__isnull=True)
            queryset2 = Order.objects.filter(manager_id=user_id,
                                             deleted__isnull=True)
            queryset = (queryset1 | queryset2).distinct().order_by('-created')
            queryset = self.get_serializer_class().setup_eager_loading(
                queryset)
        else:
            queryset = Order.objects.none()
        return queryset

    def perform_create(self, serializer):  # pylint: missing-function-docstring
        serializer.save(context={'request': self.request})


