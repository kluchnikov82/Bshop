"""
Shop serializers
"""
import json
import logging
import uuid
from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.urls import NoReverseMatch, reverse
from django.utils import timezone as tz
from rest_framework import serializers

from appuser.models import Address, AppUser
from appuser.serializers import (AddressSzr, AppUserRegisterSerializer,
                                 UserFeedbackSzr, UserShortSzr)
from core.serializers import EagerLoadingMixin, FilteredListSerializer
from core.tasks import send_plain_text_mail
from core.utils import (get_decimal, get_list_item_by_key, isnull,
                        normalize_phone, send_mail_after_user_register)
from core.utils import get_random_email
from shop.tasks import post_create_order
from .models import (ActiveComponent, Advice, AdviceType, Category, CatProduct,
                     Event, EventProductFor2Any, EventProductSomeTheSame, Kit,
                     KitAdvice, KitCategory, KitFeedback, KitImage,
                     KitPreference, KitProduct, KitStage, LinkedProduct,
                     Order, OrderBonusHistory, OrderKit,
                     OrderProduct, Payment, Product, LinkedEvent,
                     ProductComponent, ProductFeedback, ProductImage,
                     PromoCode, Slide, SubCategory, SubCatProduct, OrderEvent,
                     OrderEventProduct, SBNotice, EventGroup, EventGroupProduct,
                     ProductEvents, FeedbackProductImage, FeedbackKitImage,
                     EventProductBundle, FeedbackAll)
from .utils import get_user_ref_id_from_promo

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


class ActiveKitListSerializer(serializers.ListSerializer):  # pylint: disable=abstract-method
    """
    Метод фильтрации только активных программ в сериализаторе программ товаров
    """
    def to_representation(self, data):
        active_kit_ids = Kit.objects.filter(
            deleted__isnull=True,
            is_active=True).values_list('id', flat=True)
        data = data.filter(deleted__isnull=True, kit_id__in=active_kit_ids)
        return super(ActiveKitListSerializer, self).to_representation(data)


class ProductImageSzr(serializers.ModelSerializer):
    """
        Сериализатор дополнительных изображений товара
    """
    class Meta:
        model = ProductImage
        fields = ('image', )
        read_only_fields = fields


class FeedbackProductImageSzr(serializers.ModelSerializer):
    """
        Сериализатор изображений отзыва о товаре
    """
    class Meta:
        model = FeedbackProductImage
        fields = ('image',)
        read_only_fields = fields


class FeedbackKitImageSzr(serializers.ModelSerializer):
    """
        Сериализатор изображений отзыва о программе
    """
    class Meta:
        model = FeedbackKitImage
        fields = ('image',)


class LinkedProductSzr(serializers.HyperlinkedModelSerializer):
    """
        Сериализатор товаров, покупаемых вместе
    """
    product_id = serializers.ReadOnlyField(source='lnkd_product.id')
    product_name = serializers.ReadOnlyField(source='lnkd_product.name')
    price = serializers.ReadOnlyField(source='lnkd_product.price.amount')
    price_currency = serializers.ReadOnlyField(
        source='lnkd_product.price_currency')
    primary_image = serializers.ImageField(source='lnkd_product.primary_image')
    code = serializers.ImageField(source='lnkd_product.code')
    english_name = serializers.ReadOnlyField(
        source='lnkd_product.english_name')
    hit = serializers.ReadOnlyField(source='lnkd_product.hit')
    new = serializers.ReadOnlyField(source='lnkd_product.new')
    product_images = ProductImageSzr(many=True,
                                     read_only=True,
                                     source='lnkd_product.product_images')
    slug = serializers.ReadOnlyField(source='lnkd_product.slug')

    class Meta:
        model = LinkedProduct
        fields = ('product_id', 'product_name', 'price', 'price_currency',
                  'primary_image', 'code', 'english_name', 'hit', 'new',
                  'product_images', 'slug')
        read_only_fields = fields


