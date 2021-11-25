"""
Shop models
"""
import decimal
import json
import logging
import uuid
from datetime import timedelta

import requests
from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.db.models import signals
from django.utils import timezone as tz
from django.utils.safestring import mark_safe
from django_better_admin_arrayfield.models.fields import ArrayField
from djmoney.models.fields import MoneyField
from requests.exceptions import (ReadTimeout, ConnectTimeout,  # pylint: disable=redefined-builtin
                                 ConnectionError, HTTPError)

from appuser.models import Address
from appuser.models import AppUser
from core.models import AutoIncHitCountModelMixin, ImagePreviewModelMixin
from core.models import BaseModel, BaseImage, send_sms
from core.models import get_service_params
from core.tasks import send_plain_text_mail, send_mail
from core.utils import get_cdek_method_id
from core.utils import isnull
from core.validators import validate_slug
from .cdek import CDEKClient
from .iso_4217 import CODE_LIST
from .paykeeper import PaykeeperClient
from .rp import RPClient
from .utils import get_shipping_method_params

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


class Category(BaseModel, ImagePreviewModelMixin):
    """
    Категория товара
    """
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='category_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение категории')
    header_image = models.ImageField(
        upload_to='category_images/header_images/%Y/%m/%d/',
        blank=True,
        verbose_name='Изображение для заголовка')
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])
    SEO_title = models.CharField(
        max_length=70, default=None, null=True, blank=True, verbose_name='SEO_title')
    SEO_description = models.CharField(
        max_length=155, default=None, null=True, blank=True, verbose_name='SEO_description')

    def header_image_tag(self):
        """
        Функция отображения превью изображения в админке
        :return:
        """
        return mark_safe(
            f'<img src="{settings.MEDIA_URL}{self.header_image}" width="100" height="100" />'
        )
    header_image.short_description = 'Превью'

    class Meta:
        verbose_name = 'Категория товара/статьи'
        verbose_name_plural = 'Категории товаров/статей'
        ordering = ['name']
        db_table = 'shop_category'

    def __str__(self):
        return self.name


class SubCategory(BaseModel):
    """
    Подкатегория товара
    """
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование подкатегории')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Категория',
                                 related_name='subcats')
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])
    SEO_title = models.CharField(
        max_length=70, default=None, null=True, blank=True, verbose_name='SEO_title')
    SEO_description = models.CharField(
        max_length=155, default=None, null=True, blank=True, verbose_name='SEO_description')

    class Meta:
        verbose_name = 'Подкатегория товара'
        verbose_name_plural = 'Подкатегории товаров'
        ordering = ['name']
        db_table = 'shop_subcategory'

    def __str__(self):
        return '%s -> %s' % (self.category.name, self.name)


class ActiveComponent(BaseModel, ImagePreviewModelMixin):
    """
    Активный компонент товара
    """
    name = models.CharField(max_length=255,
                            blank=False,
                            verbose_name='Наименование компонента')
    short_description = models.CharField(
        blank=True,
        default=None,
        null=True,
        max_length=1000,
        verbose_name='Краткое описание компонента')
    description = RichTextField(verbose_name='Полное описание компонента',
                                blank=True,
                                max_length=5000)
    image = models.ImageField(upload_to='component_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение компонента')
    benefits = ArrayField(models.CharField(max_length=1000),
                          null=True,
                          verbose_name='Польза')
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])

    class Meta:
        verbose_name = 'Активный компонент'
        verbose_name_plural = 'Активные компоненты'
        db_table = 'shop_active_component'

    def __str__(self):
        return self.name


class Product(BaseModel, AutoIncHitCountModelMixin):
    """
    Товар
    """
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование товара')
    english_name = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        default=None,
        db_index=True,
        verbose_name='Наименование товара на английском')
    product_no = models.PositiveIntegerField(unique=True,
                                             editable=False,
                                             verbose_name='Порядковый номер')
    description = RichTextField(max_length=5000,
                                blank=True,
                                verbose_name='Описание')
    short_description = RichTextField(blank=True,
                                      null=True,
                                      default=None,
                                      verbose_name='Краткое описание')
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Розничная цена')
    is_available = models.BooleanField(verbose_name='В наличии', default=True)
    weight = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='Вес, г')
    gross_weight = models.IntegerField(default=0,
                                       null=True,
                                       blank=True,
                                       verbose_name='Вес брутто, г')
    volume = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='Объем, мл')
    packing_volume = models.FloatField(default=0.001,
                                       blank=False,
                                       verbose_name='Объем с упаковкой, м3')
    primary_image = models.ImageField(
        upload_to='product_images/%Y/%m/%d/',
        blank=True,
        verbose_name='Основное изображение товара',
        null=True)
    length = models.FloatField(verbose_name='Длина, см',
                               blank=False,
                               default=10)
    width = models.FloatField(verbose_name='Ширина, см',
                              blank=False,
                              default=10)
    height = models.FloatField(verbose_name='Высота, см',
                               blank=False,
                               default=10)
    sub_categories = models.ManyToManyField(SubCategory,
                                            through='SubCatProduct',
                                            verbose_name='Подкатегории',
                                            related_name='subcat_products')
    active_components = models.ManyToManyField(
        ActiveComponent,
        through='ProductComponent',
        related_name='product_components',
        verbose_name='Активные компоненты')
    linked_products = models.ManyToManyField(
        'self',
        through='LinkedProduct',
        symmetrical=False,
        blank=True,
        verbose_name='Товары, приобретаемые вместе')
    hit_count = models.PositiveIntegerField(
        default=0, verbose_name='Количество просмотров')
    result = RichTextField(max_length=5000,
                           null=True,
                           blank=True,
                           default=None,
                           verbose_name='Результат')
    usage = RichTextField(max_length=5000,
                          null=True,
                          blank=True,
                          default=None,
                          verbose_name='Применение')
    certificate = models.ImageField(upload_to='product_images/certs/%Y/%m/%d/',
                                    blank=True,
                                    verbose_name='Изображение сертификата')
    hit = models.BooleanField(verbose_name='Хит продаж', default=False)
    new = models.BooleanField(verbose_name='Новинка', default=False)
    discount = models.PositiveIntegerField(verbose_name='Скидка, %',
                                           blank=True,
                                           null=True,
                                           default=None)
    rating = models.FloatField(verbose_name='Средний рейтинг товара',
                               default=0,
                               blank=True)
    code = models.CharField(default='',
                            blank=True,
                            max_length=255,
                            verbose_name='Артикул')
    avatar = models.ImageField(
        upload_to='product_avatars/%Y/%m/%d/',
        blank=True,
        verbose_name='Аватар',
        null=True)
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])

    def image_tag(self):  # pylint: disable=missing-function-docstring
        return mark_safe(
            f'<img src="{settings.MEDIA_URL}{self.primary_image}" width="100" height="100" />'
        )
    image_tag.short_description = 'Превью'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['product_no']
        db_table = 'shop_product'

    def __str__(self):
        return '[%s] %s, вес: %s г, объем: %s мл' % (self.code, self.name,
                                                     self.weight, self.volume)


class SubCatProduct(BaseModel):
    """
    Подкатегория товара
    """
    subcategory = models.ForeignKey(SubCategory,
                                    on_delete=models.DO_NOTHING,
                                    verbose_name='Подкатегория')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')

    class Meta:
        verbose_name = 'Подкатегории товара'
        verbose_name_plural = 'Подкатегории товара'
        db_table = 'shop_subcat_product'

    def __str__(self):
        return '%s -> %s: %s' % (self.subcategory.category.name,
                                 self.subcategory.name, self.product.name)


class CatProduct(models.Model):
    """
    Связка категория <-> товар
    """
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Категория',
                                 related_name='prod_cat')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='category_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение категории')

    class Meta:
        verbose_name = 'Категории товара'
        verbose_name_plural = 'Категория товара'
        db_table = 'view_product_categories'
        managed = False

    def __str__(self):
        return '%s: %s' % (self.category.name, self.product.name)


class ProductComponent(BaseModel):
    """
    Связка товар <-> активный компонент
    """
    component = models.ForeignKey(ActiveComponent,
                                  on_delete=models.DO_NOTHING,
                                  verbose_name='Активный компонент',
                                  related_name='prod_comp')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')

    class Meta:
        verbose_name = 'Активный компонент товара'
        verbose_name_plural = 'Активные компоненты товара'
        db_table = 'shop_product_component'

    def __str__(self):
        return '%s: %s' % (self.product.name, self.component.name)


class ProductImage(BaseImage):
    """
    Дополнительное изображение товара
    """
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар',
                                related_name='product_images')
    image = models.ImageField(upload_to='product_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение')

    class Meta:
        verbose_name = 'Дополнительное изображение товара'
        verbose_name_plural = 'Дополнительные изображения товаров'
        db_table = 'shop_product_image'

    def __str__(self):
        return '%s: %s' % (self.product.name, self.image)


class Kit(BaseModel, AutoIncHitCountModelMixin):
    """
    Программа (набор товаров)
    """
    name = models.CharField(max_length=255,
                            db_index=True,
                            verbose_name='Наименование программы')
    description = models.TextField(blank=True,
                                   verbose_name='Описание программы')
    kit_no = models.PositiveIntegerField(unique=True,
                                         editable=False,
                                         verbose_name='Артикул')
    products = models.ManyToManyField(Product,
                                      through='KitProduct',
                                      related_name='kit_products',
                                      verbose_name='Товары в программе')
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Розничная цена')
    primary_image = models.ImageField(
        upload_to='kit_images/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Основное изображение программы')
    is_available = models.BooleanField(verbose_name='В наличии', default=True)
    weight = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='Вес, г')
    gross_weight = models.IntegerField(default=0,
                                       null=True,
                                       blank=True,
                                       verbose_name='Вес брутто, г')
    packing_volume = models.FloatField(default=0.001,
                                       blank=False,
                                       verbose_name='Объем с упаковкой, м3')
    length = models.FloatField(verbose_name='Длина, см',
                               blank=False,
                               default=10)
    width = models.FloatField(verbose_name='Ширина, см',
                              blank=False,
                              default=10)
    height = models.FloatField(verbose_name='Высота, см',
                               blank=False,
                               default=10)
    problem = models.CharField(max_length=1000,
                               blank=True,
                               null=True,
                               default=None,
                               verbose_name='Проблема')
    target = models.CharField(max_length=1000,
                              blank=True,
                              null=True,
                              default=None,
                              verbose_name='Цель')
    preference = models.CharField(max_length=1000,
                                  blank=True,
                                  null=True,
                                  default=None,
                                  verbose_name='Преимущество')
    usage_period = models.CharField(max_length=1000,
                                    blank=True,
                                    null=True,
                                    default=None,
                                    verbose_name='Время использования')
    formula = models.CharField(max_length=1000,
                               blank=True,
                               null=True,
                               default=None,
                               verbose_name='Формулы')
    categories = models.ManyToManyField(Category,
                                        through='KitCategory',
                                        verbose_name='Категории',
                                        related_name='kit_cats')
    hit_count = models.PositiveIntegerField(
        default=0, verbose_name='Количество просмотров')
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])
    is_active = models.BooleanField(default=True,
                                    verbose_name='Отображать на сайте')

    def image_tag(self):  # pylint: disable=missing-function-docstring
        return mark_safe(
            f'<img src="{settings.MEDIA_URL}{self.primary_image}" width="100" height="100" />'
        )
    image_tag.short_description = 'Превью'

    class Meta:
        ordering = ['kit_no']
        verbose_name = 'Программа'
        verbose_name_plural = 'Программы'
        db_table = 'shop_kit'

    def __str__(self):
        return '[%s] %s, вес: %s г, объем: %s мл' % (
            self.kit_no, self.name, self.weight, self.packing_volume)


class KitPreference(BaseModel):
    """
    Преимущество программы
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа',
                            related_name='preferences')
    seq_no = models.PositiveIntegerField(verbose_name='Порядковый номер')
    description = models.CharField(max_length=1000,
                                   null=True,
                                   default=None,
                                   verbose_name='Описание')

    def clean(self):
        if KitPreference.objects.filter(
                kit_id=self.kit.id, seq_no=self.seq_no,
                deleted__isnull=True).exclude(id=self.id).exists():
            raise ValidationError(
                f'Для этой программы уже существует преимущество с порядковым номером {self.seq_no}!'
            )

    class Meta:
        verbose_name = 'Преимущество программы'
        verbose_name_plural = 'Преимущества программы'
        db_table = 'shop_kit_preference'

    def __str__(self):
        return '%s: %s' % (self.seq_no, self.description)


class KitAdvice(BaseModel):
    """
    Связка основной программы с рекомендуемыми
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа',
                            related_name='advices')
    seq_no = models.PositiveIntegerField(verbose_name='Порядковый номер')
    header = models.CharField(max_length=255,
                              blank=False,
                              verbose_name='Заголовок')
    description = models.CharField(max_length=1000,
                                   null=True,
                                   default=None,
                                   verbose_name='Описание')
    link_text = models.CharField(max_length=255,
                                 blank=True,
                                 null=True,
                                 default=None,
                                 verbose_name='Текст ссылки')
    advice_kit = models.ForeignKey(Kit,
                                   on_delete=models.DO_NOTHING,
                                   blank=True,
                                   null=True,
                                   related_name='advice_kit',
                                   verbose_name='Рекомендуемая программа')
    image = models.ImageField(upload_to='kit_advices/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Иконка рекомендации')

    def clean(self):
        """
        Проверка на существование рекомендуемой программы с тем же порядковым номером
        :return:
        """
        if KitAdvice.objects.filter(
                kit_id=self.kit.id, seq_no=self.seq_no,
                deleted__isnull=True).exclude(id=self.id).exists():
            raise ValidationError(
                f'Для этой программы уже существует рекомендация с порядковым номером {self.seq_no}!'
            )

    class Meta:
        verbose_name = 'Рекомендация программы'
        verbose_name_plural = 'Рекомендации программы'
        db_table = 'shop_kit_advice'

    def __str__(self):
        return '%s: %s' % (self.seq_no, self.description)


class KitProduct(BaseModel):
    """
    Связка программа <-> товар
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    products_count = models.PositiveIntegerField(
        default=1, verbose_name='Кол-во товаров в программе')

    class Meta:
        verbose_name = 'Товар программы'
        verbose_name_plural = 'Товары программы'
        db_table = 'shop_kit_products'

    def __str__(self):
        return '%s' % (self.product, )


class LinkedProduct(BaseModel):
    """
    Связка товар <-> покупаемые вместе с ним товары
    """
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    lnkd_product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        verbose_name='Вместе с этим товаром покупают',
        related_name='lp_linked_product')

    def __str__(self):
        return '%s <-> %s' % (self.product.name, self.lnkd_product.name)

    class Meta:
        verbose_name = 'Товар, приобретаемый вместе'
        verbose_name_plural = 'Товары, приобретаемые вместе с этим'
        db_table = 'shop_linked_product'


class KitImage(BaseImage):
    """
    Дополнительное изображение программы
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа',
                            related_name='kit_images')
    image = models.ImageField(upload_to='kit_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение')

    class Meta:
        verbose_name = 'Дополнительное изображение программы'
        verbose_name_plural = 'Дополнительные изображения программы'
        db_table = 'shop_kit_image'


class Order(BaseModel):
    """
    Заказ
    """
    ACTIVE = 0
    PAYED = 1
    IN_DELIVERY = 2
    PAYED_PARTLY = 6
    """
    Состояния заказа
    """
    ORDER_STATES = (
        (ACTIVE, 'Активный'),
        (PAYED, 'Оплачен'),
        (IN_DELIVERY, 'Отправлен'),
        (PAYED_PARTLY, 'Оплачен частично')
        # (COMPLETED, 'Закрыт'),
        # в будущем возможна реализация периодического опроса служб доставки на предмет статусов отправленных посылок.
        # если посылка доставлена - статус заказа будет меняться на COMPLETED
    )
    """
    Типы заказа
    """
    PRODUCT_ORDER = 0
    BALANCE_ORDER = 1

    ORDER_TYPES = (
        (PRODUCT_ORDER, 'Заказ товара'),
        (BALANCE_ORDER, 'Пополнение депозита')
    )

    order_no = models.PositiveIntegerField(unique=True,
                                           editable=False,
                                           verbose_name='Номер заказа')
    user = models.ForeignKey(AppUser,
                             null=True,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь',
                             related_name='order_user')
    total_amount = MoneyField(max_digits=14,
                              decimal_places=2,
                              default_currency='RUB',
                              verbose_name='Сумма')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    is_payed = models.BooleanField(default=False, verbose_name='Оплачен')
    payed = models.DateTimeField(null=True,
                                 default=None,
                                 verbose_name='Дата оплаты')
    address = models.ForeignKey(Address,
                                null=True,
                                on_delete=models.DO_NOTHING,
                                related_name='order_address',
                                verbose_name='Адрес доставки')
    track_no = models.CharField(max_length=50,
                                verbose_name='Трек-номер',
                                blank=True,
                                null=True,
                                default=None)
    status = models.IntegerField(choices=ORDER_STATES,
                                 default=ACTIVE,
                                 verbose_name='Статуса заказа')
    own = models.BooleanField(default=True, verbose_name='Заказ для себя')
    phone = models.CharField(max_length=20,
                             blank=False,
                             verbose_name='Контактный телефон')
    email = models.EmailField(max_length=255,
                              blank=False,
                              verbose_name='Email')
    memo = models.CharField(blank=True,
                            null=True,
                            default=None,
                            max_length=1000,
                            verbose_name='Комментарий к заказу')
    order_type = models.IntegerField(choices=ORDER_TYPES,
                                     default=PRODUCT_ORDER,
                                     verbose_name='Тип заказа')
    shipping_method_id = models.IntegerField(default=0,
                                             blank=False,
                                             choices=settings.SHIPPING_METHODS,
                                             verbose_name='Cпособ доставки')
    delivery_point_id = models.CharField(max_length=255,
                                         null=True,
                                         default=None,
                                         verbose_name='ID ПВЗ')
    shipping_amount = MoneyField(max_digits=14,
                                 decimal_places=2,
                                 default=0,
                                 default_currency='RUB',
                                 verbose_name='Стоимость доставки')
    total_weight = models.IntegerField(default=0,
                                       blank=True,
                                       verbose_name='Общий вес заказа, г')
    total_volume = models.FloatField(
        default=0, blank=True, verbose_name='Общий объем товаров в заказе, м3')
    surname = models.CharField(max_length=255,
                               blank=False,
                               verbose_name='Фамилия получателя')
    name = models.CharField(max_length=255,
                            blank=False,
                            verbose_name='Имя получателя')
    patronymic = models.CharField(max_length=255,
                                  blank=True,
                                  null=True,
                                  default='',
                                  verbose_name='Отчество получателя')
    is_ready = models.BooleanField(default=False,
                                   verbose_name='Передан курьеру')
    is_track_created = models.BooleanField(default=False,
                                           verbose_name='Трек-номер создан')
    is_track_sended = models.BooleanField(
        default=False,
        null=True,
        verbose_name='Уведомление о присвоении трека выслано')
    create_shipment_result = models.CharField(
        max_length=1000,
        null=True,
        default=None,
        blank=True,
        verbose_name='Результат запроса на создание отправления')
    create_shipment_request_last_date = models.DateTimeField(
        null=True,
        default=None,
        verbose_name='Дата выполнения последнего запроса на создание отправления')
    shipment_id = models.CharField(max_length=255,
                                   null=True,
                                   blank=False,
                                   default=None,
                                   verbose_name='Номер отправления')
    promocode = models.CharField(max_length=255,
                                 blank=True,
                                 null=True,
                                 default=None,
                                 verbose_name='Промокод',)
    total_amount_wo_discount = MoneyField(max_digits=14,
                                          decimal_places=2,
                                          default_currency='RUB',
                                          default=0,
                                          verbose_name='Сумма без скидок')
    manager = models.ForeignKey(AppUser,
                                null=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Менеджер',
                                related_name='order_manager')
    promo_discount = models.DecimalField(max_digits=14,
                                         default=0,
                                         decimal_places=2,
                                         verbose_name='Значение скидки по промокоду')
    delivery_point_address = models.CharField(
        max_length=255, default=None, null=True, blank=True, verbose_name='Адрес ПВЗ')

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Генерация порядкового номера заказа при создании
        :param args:
        :param kwargs:
        :return:
        """
        if self._state.adding:
            self.order_no = self.get_next_seq_no()
        super(Order, self).save(*args, **kwargs)

    def get_items(self):
        """
        Получение сериализованного массива товаров и программ, входящих в заказ
        :return:
        """
        from .serializers import (OrderProductSendSzr,    # pylint: disable=import-outside-toplevel
                                  OrderKitSendSzr,
                                  OrderEventProductsSendSzr)
        items = []
        order_products = OrderProductSendSzr(self.order_products.filter(deleted__isnull=True), many=True).data
        order_kits = OrderKitSendSzr(self.order_kits.filter(deleted__isnull=True), many=True).data
        order_events_ids = self.order_events.filter(deleted__isnull=True).values_list('id', flat=True)
        order_event_products = OrderEventProductsSendSzr(
            OrderEventProduct.objects.filter(order_event_id__in=order_events_ids, deleted__isnull=True), many=True).data
        items.extend(order_products)
        items.extend(order_kits)
        items.extend(order_event_products)
        return items

    def get_recipient(self):
        """
        Получение ФИО и контактного телефона адресата
        :return:
        """
        return {
            'surname': isnull(self.surname, ''),
            'name': isnull(self.name, ''),
            'patronymic': isnull(self.patronymic, ''),
            'phone': self.phone
        }

    def get_address(self):
        """
        Получение сериализованного адреса
        :return:
        """
        return {
            'postcode': self.address.postcode,
            'country': self.address.country,
            'region': self.address.region,
            'district': self.address.district,
            'settlement': self.address.settlement,
            'building': self.address.building,
            'city': self.address.city,
            'street': self.address.street,
            'house': self.address.house,
            'flat': self.address.flat,
            'kladr_id': self.address.kladr_id,
            'oksm_id': self.address.oksm_id,
            'cdek_city_id': self.address.cdek_city_id,
            'raw_address': self.address.get_formatted_address()
        }

    def get_order_link(self):
        """
        Формирование ссылки на заказ
        :return: ссылка на заказ
        """
        return settings.ORDER_DETAIL_URL + str(self.id)

    def change_status_send_notice(self, track=None):
        """
        Отправка оповещения об изменении статуса заказа на email получателя
        """
        track_string = f' Трек-номер заказа: {self.track_no}.' if track else ''
        link = self.get_order_link()
        plain_text = f"""
        Добрый день!

        Статус заказа {self.order_no} изменен на {self.get_status_display()}.{track_string}
        Ссылка на заказ: {link}

        С уважением,
        Интернет-магазин dari-cosmetics.ru"""
        send_mail.delay(recipient_list=(self.email, ),
                        subject=f'Изменение статуса заказа {self.order_no}',
                        plain_text=plain_text,
                        template_name='order_status_change.html',
                        context={
                            'order_no': self.order_no,
                            'status': self.get_status_display(),
                            'track_string': track_string,
                            'link': link,
                            'memo': isnull(self.memo, '')
                        })

    def send_payment_notice_admin(self, payment_sum, from_admin=False):
        """
        Отправка сообщения об оплате заказа админам
        :param payment_sum: сумма поступившего платежа
        :param from_admin: признак оплаты заказа из админки
        """
        message = f'Email: {self.email}, телефон: {self.phone}, ФИО: {self.surname} {self.name} ' \
                  f'{isnull(self.patronymic, "")}\n'\
                  f'Адрес доставки: {self.address.get_formatted_address()}\n'\
                  f'Сумма заказа: {self.total_amount}\n'\
                  f'{isnull(self.memo, "")}\n'
        message = message + f'Ссылка на заказ: {self.get_order_link()}' + '\n'
        subject = f'Статус заказа {self.order_no} на сумму {payment_sum} руб. изменен на ' \
                  f'"Оплачен" в админке' if from_admin \
            else f'Поступил платеж по заказу {self.order_no} на сумму {payment_sum} руб.'
        send_plain_text_mail.delay(
            recipient_list=settings.PAYMENT_MAIL_LIST,
            subject=subject,
            message=message,
        )

    def change_status(self, new_status):
        """
        Изменение статуса заказа
        :param new_status: новый статус
        :return:
        """
        if new_status != self.status:
            if new_status == Order.PAYED:
                self.is_payed = True
            self.status = new_status
            self.save()

    def send_sms_notice_order_payed(self, track=None):
        """
        Отправка SMS-оповещения об изменении статуса заказа на "Оплачен"
        """
        if self.status == self.PAYED:
            track_string = f'. Трек-номер: {self.track_no}' if self.track_no and track \
                else '. Трек номер будет отправлен после отправки посылки'
            send_sms(
                self.phone,
                f'Заказ {self.order_no} оплачен{track_string}')
        else:
            logger.error(
                f'SMS об изменении статуса заказа {self.order_no} на "Оплачен" не отправлено'
            )

    def send_sms_notice_order_in_delivery(self):
        """
        Отправка SMS-оповещения об изменении статуса заказа на "Отправлен"
        """
        if self.status == self.IN_DELIVERY and self.track_no:
            send_sms(
                self.phone,
                f'Заказ {self.order_no} отправлен. Трек-номер: {self.track_no}'
            )
        else:
            logger.error(
                f'SMS об изменении статуса заказа {self.order_no} на "Отправлен" не отправлено'
            )

    def create_track(self):  # pylint: disable=too-many-branches
        """
        Создание посылки после оплаты заказа
        :return: результат выполнения запроса на создание посылки к партнеру (Почте России либо СДЕКу)
        """
        # TODO: рефакторинг [too-many-branches]
        address = self.get_address()
        order_items = self.get_items()
        recipient = self.get_recipient()
        package = {
            'products':     order_items,
            'weight':       self.total_weight,
            'order_no':     self.order_no,
            'height':       settings.BOX_DIMENSIONS['height'],
            'length':       settings.BOX_DIMENSIONS['length'],
            'width':        settings.BOX_DIMENSIONS['width'],
            'total_amount': float(self.total_amount.amount)
        }
        track_no = None
        if self.shipping_method_id in [i[0] for i in settings.RP_SHIPPING_METHODS]:
            rp_api = RPClient()
            _, _, param1, param2 = get_shipping_method_params(
                self.shipping_method_id)
            mail_type, courier = param1, param2
            for item in settings.RP_SHIPPING_METHODS:
                if item[0] == self.shipping_method_id:
                    courier = item[3]
                    mail_type = item[2]
                    break
            result = rp_api.create_shipment(address, mail_type, courier, recipient,
                                            package)
            if result['error'] is not None:
                self.create_shipment_result = result.get(
                    'message',
                    'Ошибка запроса на создание посылки к API Почты России!')
            else:
                self.create_shipment_result = result.get('message', '')
                shipment_id = result['data']['shipment_id']
                self.shipment_id = shipment_id
                shipment_data = rp_api.get_order(shipment_id, mail_type=mail_type)
                if shipment_data['error'] or 'data' not in shipment_data:
                    self.create_shipment_result = self.create_shipment_result + '|' + shipment_data[
                        'message']
                else:
                    if 'barcode' in shipment_data['data']:
                        track_no = shipment_data['data']['barcode']
            self.create_shipment_request_last_date = tz.now()
        elif self.shipping_method_id in [i[0] for i in settings.CDEK_SHIPPING_METHODS]:
            cdek_params = get_service_params('cdek', ('login', 'password'))
            api = CDEKClient(login=cdek_params.get('login'),
                             secure=cdek_params.get('password'))
            tarif_id = str(get_cdek_method_id(self.shipping_method_id))
            result = api.create_shipment(address=self.get_address(),
                                         recipient=self.get_recipient(),
                                         package=package,
                                         tarif_id=tarif_id,
                                         delivery_point_code=str(
                                             isnull(self.delivery_point_id, '')))
            if result['error'] is not None:
                self.create_shipment_result = result.get(
                    'message', 'Ошибка запроса на создание посылки к API СДЭК!')
            else:
                self.create_shipment_result = result.get('message', '')
                if 'shipment_id' in result['data']:
                    track_no = result['data']['shipment_id']
            self.create_shipment_request_last_date = tz.now()
        self.save()
        if track_no:
            self.track_no = track_no
            self.is_track_created = True
            self.save()
            logger.debug(f'Заказ {self.order_no}: создан трек {track_no}')

    def send(self):
        """
        Изменение статуса заказа после его сборки и актуализации трека, отправка оповещения клиенту
        """
        self.change_status(Order.IN_DELIVERY)
        self.change_status_send_notice(track=True)
        self.send_sms_notice_order_in_delivery()
        self.is_track_sended = True
        self.save()

    def process_payment(self, payment):
        """
        Обработка поступившего платежа
        :param payment: объект Payment
        :return:
        """
        order_id = self.id
        order_no = self.order_no
        # находим суммы всех оплат всех типов по заказу
        amounts = Payment.objects.filter(
            order_id=order_id,
            confirmation_date__isnull=False).aggregate(
                amount_sum=Sum('amount'),
                bonus_sum=Sum('bonus_amount'),
                deposit_sum=Sum('deposit_amount'))
        p_amount_sum = amounts['amount_sum']
        p_bonus_sum = amounts['bonus_sum']
        p_deposit_sum = amounts['deposit_sum']
        logger.debug(
            f'Сумма заказа: {self.total_amount.amount}, стоимость доставки: {self.shipping_amount.amount}'
            f'сумма платежа: {p_amount_sum}, '
            f'сумма оплаты бонусами: {p_bonus_sum}, сумма оплаты с депозита: {p_deposit_sum}'
        )

        # проверяем, достаточную ли сумму оплатил клиент
        if self.total_amount.amount + self.shipping_amount.amount <= p_amount_sum + p_bonus_sum + p_deposit_sum:
            is_balance_enough = False
            if p_bonus_sum + p_deposit_sum > 0:
                try:
                    with transaction.atomic():
                        order_creator = AppUser.objects.select_for_update(
                        ).get(id=self.user_id)
                        if order_creator.bonus_balance.amount >= p_bonus_sum \
                                and order_creator.balance.amount >= p_deposit_sum:
                            # если часть заказа оплачивается бонусного баланса или депозита,
                            # проверяем, достаточная ли сумма на данный момент на бонусном балансе
                            # и депозите клиента
                            # если да - уменьшаем ББ и депозит
                            is_balance_enough = True
                            order_creator.change_balance(
                                -payment.bonus_amount.amount,
                                -payment.deposit_amount.amount)
                except ObjectDoesNotExist:
                    pass
            else:
                is_balance_enough = True
            if is_balance_enough:
                self.change_status(Order.PAYED)
                # все действия по начислению бонусов и/или депозита
                # производятся в триггере order_before_update
                logger.info(f'Заказ {order_no} оплачен полностью')
                self.create_track()
                track = self.shipping_method_id in (settings.RUSSIAN_POST, settings.EMS_RUSSIA)
                self.change_status_send_notice(track=track)
                self.send_payment_notice_admin(payment.amount.amount)
                self.send_sms_notice_order_payed(track=track)
                if track:
                    self.change_status(Order.IN_DELIVERY)
            else:
                send_plain_text_mail.delay(
                    recipient_list=settings.ADMIN_MAIL_LIST,
                    subject=f'Заказ {order_no} оплачен частично! ',
                    message=f'Сумма заказа: {self.total_amount.amount}, '
                            f'стоимость доставки: {self.shipping_amount.amount}'
                            f'сумма платежа: {p_amount_sum}, '
                            f'сумма оплаты бонусами: {p_bonus_sum}, сумма оплаты с депозита: {p_deposit_sum}'
                )
        else:
            self.change_status(Order.PAYED_PARTLY)
            self.change_status_send_notice()
            logger.info(f'Заказ {order_no} оплачен частично!')
            send_plain_text_mail.delay(
                recipient_list=settings.ADMIN_MAIL_LIST,
                subject=f'Заказ {order_no} оплачен частично! ',
                message=f'Сумма заказа: {self.total_amount.amount}, сумма платежа: {p_amount_sum}', )
        self.save()

    def get_pay_link(self, bonus_amount, deposit_amount):
        """
        Формирование ссылки на оплату заказа
        :return: словарь: {
            'error': True | False,
            'message': сообщение о результате,
            'data': ссылка на оплату}
        """
        if self.status == Order.PAYED:
            return {'error': True, 'message': 'Заказ уже оплачен!', 'data': None}
        shipping_amount = self.shipping_amount.amount
        order_amount = self.total_amount.amount + shipping_amount
        payment_amount = order_amount - bonus_amount - deposit_amount
        order_user = self.user
        if getattr(order_user, 'partner_type_id', None) == AppUser.MANAGER and settings.USE_SBERBANK_ONLINE:
            # если создатель заказа - менеджер, генерируем ссылку Сбербанк-Онлайн
            user_id = order_user.id
            p = Payment.objects.create(amount=payment_amount,  # pylint: disable=invalid-name
                                       bonus_amount=bonus_amount,
                                       deposit_amount=deposit_amount,
                                       confirmation_date=None,
                                       payment_source=Payment.SBER_ONLINE,
                                       order_id=self.id,
                                       order_no=self.order_no)
            currency = 'RUB'
            expiration_date = tz.now() + timedelta(
                days=settings.SBERBANK_LINK_EXPIRATION_PERIOD)
            sbr, _ = SBRequest.objects.update_or_create(
                order_id=self.id,
                defaults={
                    'amount':          payment_amount,
                    'user_id':         user_id,
                    'expired':         expiration_date,
                    'amount_currency': currency,
                    'payment_id':      p.id,
                })
            result = sbr.get_pay_link()
            logger.debug(
                f'Получение ссылки на оплату - ответ Сбербанк: {result}')
        else:
            # получение ссылки на оплату Paykeeper
            Payment.objects.create(amount=payment_amount,
                                   bonus_amount=bonus_amount,
                                   deposit_amount=deposit_amount,
                                   confirmation_date=None,
                                   payment_source=Payment.PAYKEEPER,
                                   order_id=self.id,
                                   order_no=self.order_no)
            p = PaykeeperClient()  # pylint: disable=invalid-name
            recipient = self.get_recipient()
            params = {
                'pay_amount':   float(payment_amount),
                'clientid':     f'{recipient["surname"]} {recipient["name"]} {recipient["patronymic"]}',
                'orderid':      str(self.order_no),
                'client_email': self.email,
                'service_name': '',
                'client_phone': self.phone
            }
            logger.debug(
                f'Получение ссылки на оплату - параметры запроса к Paykeeper: {params}'
            )
            result = p.get_pay_link(params)
            logger.debug(
                f'Получение ссылки на оплату - ответ Paykeeper: {result}')
        return result

    def get_manager_name(self):
        """Получение ФИО менеджера, создавшего заказ"""
        manager_name = self.manager.get_full_name() if self.manager else None
        return manager_name

    def get_payment_bonus_amount(self):
        """Получение суммы бонусов, потраченных на оплату заказа"""
        return isnull(Payment.objects.filter(
            order_id=self.id,
            confirmation_date__isnull=False).aggregate(
                bonus_sum=Sum('bonus_amount'))['bonus_sum'], 0)

    class Meta:
        ordering = ['order_no']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'shop_order'

    def __str__(self):
        return '%s: %s' % (self.order_no,
                           isnull(self.user, 'Незарег. пользователь'))


class ReferrerOrder(BaseModel):
    """
    Заказ реферрера (созданный реферралом)
    """
    order = models.OneToOneField(Order,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Заказа',
                                 related_name='ref_order')
    referrer = models.ForeignKey(AppUser,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='',
                                 related_name='user_ref_orders')
    bonus = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Сумма бонуса')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Заказ реферера'
        verbose_name_plural = 'Заказы реферера'
        db_table = 'shop_referrer_order'

    def __str__(self):
        return '%s %s' % (self.referrer.username, self.order.order_no)


class OrderProduct(BaseModel):
    """
    Связка заказ <-> товары
    """
    order = models.ForeignKey(Order,
                              on_delete=models.DO_NOTHING,
                              verbose_name='Заказ',
                              related_name='order_products')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество',
                                           default=0)
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Цена')
    amount = MoneyField(max_digits=14,
                        decimal_places=2,
                        default=1,
                        default_currency='RUB',
                        verbose_name='Сумма')

    class Meta:
        ordering = ['product']
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'
        db_table = 'shop_order_product'

    def __str__(self):
        return '%s: , кол-во: %s, цена: %s, сумма %s' % (
            self.product, self.quantity, self.price, self.amount)


class OrderKit(BaseModel):
    """
    Связка заказ <-> программы
    """
    order = models.ForeignKey(Order,
                              on_delete=models.DO_NOTHING,
                              verbose_name='Заказ',
                              related_name='order_kits')
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Цена')
    amount = MoneyField(max_digits=14,
                        decimal_places=2,
                        default=1,
                        default_currency='RUB',
                        verbose_name='Сумма')

    class Meta:
        ordering = ['kit']
        verbose_name = 'Программа заказа'
        verbose_name_plural = 'Программы заказа'
        db_table = 'shop_order_kit'

    def __str__(self):
        return '%s: %s %s %s' % (self.kit, self.quantity, self.price,
                                 self.amount)


class ProductPriceHistory(BaseModel):
    """
    Лог изменения цен на товары
    """
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                related_name='product_price_history',
                                verbose_name='Товар')
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default_currency='RUB',
                       verbose_name='Цена')
    started = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата начала действия')
    ended = models.DateTimeField(null=True,
                                 default=None,
                                 verbose_name='Дата завершения действия')

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'
        db_table = 'shop_product_price_history'

    def __str__(self):
        return '%s %s %s %s' % (self.product, self.price, self.started,
                                self.ended)


class Payment(BaseModel):
    """
    Платеж (онлайн и безналичный)
    """
    PAYKEEPER = 0
    CASHLESS = 1
    PAYPAL = 2
    USER_BALANCE = 3
    SBER_ONLINE = 4

    PAYMENT_SOURCES = (
        (PAYKEEPER, 'Paykeeper'),
        (CASHLESS, 'Безналичный перевод'),
        (PAYPAL, 'Paypal'),
        (USER_BALANCE, 'С баланса пользователя'),
        (SBER_ONLINE, 'Сбербанк-Онлайн'),
    )

    amount = MoneyField(max_digits=14,
                        decimal_places=2,
                        default_currency='RUB',
                        verbose_name='Сумма')
    bonus_amount = MoneyField(default=0,
                              max_digits=14,
                              decimal_places=2,
                              default_currency='RUB',
                              verbose_name='Сумма оплаты бонусами')
    deposit_amount = MoneyField(default=0,
                                max_digits=14,
                                decimal_places=2,
                                default_currency='RUB',
                                verbose_name='Сумма оплаты с депозита')
    confirmation_date = models.DateTimeField(default=None,
                                             null=True,
                                             verbose_name='Дата подтверждения')
    comment = models.CharField(blank=True,
                               null=True,
                               max_length=255,
                               default=None,
                               verbose_name='Комментарий')
    payment_source = models.IntegerField(choices=PAYMENT_SOURCES,
                                         default=PAYKEEPER,
                                         verbose_name='Источник платежа')
    order = models.ForeignKey(Order,
                              on_delete=models.DO_NOTHING,
                              null=True,
                              related_name='payment_order',
                              verbose_name='ID заказа')
    order_no = models.PositiveIntegerField(verbose_name='Номер заказа')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        db_table = 'shop_payment'

    def __str__(self):
        return '%s %s %s %s' % (self.payment_source, self.created, self.order, self.amount)


class Feedback(BaseModel):
    """
    Отзыв о товаре/программе
    """
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             default=None,
                             blank=True,
                             verbose_name='Пользователь')
    text = models.TextField(max_length=8000,
                            blank=True,
                            null=True,
                            default='',
                            verbose_name='Текст отзыва')
    approved = models.BooleanField(default=False,
                                   verbose_name='Отображать на сайте')
    show_on_main_page = models.BooleanField(
        default=False, verbose_name='Отображать на главной')
    video_link = models.CharField(null=True,
                                  default=None,
                                  blank=True,
                                  max_length=1000,
                                  verbose_name='Ссылка на обзор Youtube')
    with_text = models.BooleanField(default=True, verbose_name='С текстом до/после')
    order_no = models.PositiveIntegerField(verbose_name='Порядковый номер',
                                           null=True,
                                           default=None,
                                           blank=True)

    class Meta:
        abstract = True


class FeedbackAll(Feedback):
    """Все одобренные отзывы о программах и товарах (вьюха)"""
    image = models.ImageField(blank=True,
                              verbose_name='Изображение отзыва')
    rating = models.PositiveIntegerField(verbose_name='Рейтинг')
    show_on_main_page = models.BooleanField(
        verbose_name='Признак отображения отзыва на главной')

    class Meta:
        db_table = 'view_feedbacks'
        managed = False


class ProductFeedback(Feedback):
    """
    Связка товар <-> отзыв
    """
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                related_name='product_feedbacks',
                                verbose_name='Товар')
    rating = models.PositiveIntegerField(verbose_name='Рейтинг товара',
                                         default=0,
                                         null=True,
                                         blank=True)

    class Meta:
        verbose_name = 'Отзыв о товаре'
        verbose_name_plural = 'Отзывы о товарах'
        db_table = 'shop_product_feedback'


    def __str__(self):
        return '%s: %s' % (
            getattr(self.user, 'username', 'Анонимный пользователь'),
            self.product)


class KitFeedback(Feedback):
    """
        Связка программа <-> отзыв
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            related_name='kit_feedbacks',
                            verbose_name='Программа')
    rating = models.PositiveIntegerField(verbose_name='Рейтинг Программы',
                                         default=0,
                                         null=True,
                                         blank=True)

    class Meta:
        verbose_name = 'Отзыв о программе'
        verbose_name_plural = 'Отзывы о программах'
        db_table = 'shop_kit_feedback'

    def __str__(self):
        return '%s: %s' % (
            getattr(self.user, 'username', 'Анонимный пользователь'),
            self.kit)


class AdviceType(BaseModel):
    """
    Тип обращения в техподдержку
    """
    type_name = models.TextField(max_length=255,
                                 blank=False,
                                 verbose_name='Наименование типа обращения')
    tag = models.CharField(max_length=255,
                           null=True,
                           blank=True,
                           default='сайт',
                           verbose_name='Тэг для AmoCRM')

    class Meta:
        verbose_name = 'Тип обращение'
        verbose_name_plural = 'Типы обращений'
        db_table = 'shop_advice_type'

    def __str__(self):
        return '%s' % self.type_name


class Advice(BaseModel):
    """
    Обращение в техподдержку
    """
    name = models.CharField(max_length=255,
                            blank=False,
                            verbose_name='Имя клиента')
    phone = models.CharField(max_length=20,
                             blank=False,
                             verbose_name='Номер телефона')
    email = models.CharField(max_length=255, blank=False, verbose_name='Email')
    text = models.TextField(max_length=8000,
                            blank=False,
                            verbose_name='Текст обращения')
    advice_type = models.ForeignKey(AdviceType,
                                    on_delete=models.DO_NOTHING,
                                    verbose_name='Тип обращения')
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             default=None,
                             verbose_name='Пользователь')
    age = models.CharField(blank=True,
                           null=True,
                           default=None,
                           max_length=50,
                           verbose_name='Возраст')

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        db_table = 'shop_advice'

    def __str__(self):
        return '%s : %s %s' % (self.name, self.phone, self.text)


class OrderPayHistory(BaseModel):
    """
    История оплат заказов. Здесь создается запись при перовм изменении поля is_payed заказа на True
    """
    order = models.OneToOneField(Order,
                                 verbose_name='Заказ',
                                 on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Оплаченный заказ'
        verbose_name_plural = 'Оплаченные заказы'
        db_table = 'shop_order_pay_history'


class BonusParams(BaseModel):
    """
    Параметры партнерских программ
    """
    started = models.DateTimeField(blank=False,
                                   verbose_name='Дата начала действия')
    ended = models.DateTimeField(blank=False,
                                 verbose_name='Дата завершения действия')
    partner_type_id = models.IntegerField(choices=AppUser.PARTNER_TYPES,
                                          verbose_name='Тип партнера')
    discount = models.DecimalField(default=0,
                                   max_digits=14,
                                   decimal_places=2,
                                   verbose_name='Процент скидки (от 0 до 1)')
    bonus_share = models.DecimalField(
        default=0,
        max_digits=14,
        decimal_places=2,
        verbose_name='Процент реферральной бонусной выплаты (от 0 до 1)')
    target = models.DecimalField(default=0,
                                 max_digits=14,
                                 decimal_places=2,
                                 verbose_name='Значение целевого показателя')
    own_bonus_share = models.DecimalField(
        default=0,
        max_digits=14,
        decimal_places=2,
        verbose_name='Процент бонусной выплаты за заказы для себя (от 0 до 1)')

    def clean(self):
        """
        Валидация дат начала и завершения действия, значения поля "Скидка", наличия активных программ для партнера
        :return:
        """
        if self.started is None or self.ended is None:
            raise ValidationError(
                'Пожалуйста, укажите дату и время начала и завершения действия программы!'
            )
        if self.bonus_share < 0 or self.bonus_share > 1:
            raise ValidationError(
                'Значение поля "Доля бонусной выплаты" должно находиться в интервале '
                'от 0 до 1!')
        if self.discount < 0 or self.discount > 1:
            raise ValidationError(
                'Значение поля "Скидка" должно находиться в интервале от 0 до 1!'
            )
        if BonusParams.objects.filter(
                partner_type_id=self.partner_type_id,
                started__lte=self.ended,
                ended__gte=self.started,
                target=self.target).exclude(id=self.id).exists():
            raise ValidationError(
                'В указанном временном интервале уже существует '
                'программа расчета для этого типа партнера и целевого показателя'
            )

    def __str__(self):
        return '%s: %s, %s' % (self.get_partner_type_id_display(),
                               f'ЦП: {self.target}',
                               f'скидка: {self.discount}')

    class Meta:
        verbose_name = 'Бонусная программа'
        verbose_name_plural = 'Бонусные программы'
        db_table = 'shop_reward_params'


class ExchangeRate(BaseModel):
    """
    Курсы валют по отношению к рублю
    """
    started = models.DateTimeField(blank=False,
                                   verbose_name='Дата начала действия')
    ended = models.DateTimeField(null=True,
                                 default=None,
                                 verbose_name='Дата завершения действия')
    currency_code = models.CharField(max_length=3,
                                     blank=False,
                                     verbose_name='ISO-код валюты')

    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'
        db_table = 'shop_exchange_rate'


class PayKeeperNotice(BaseModel):
    """
    Оповещения от PayKeeper
    """
    paykeeper_id = models.CharField(max_length=255,
                                    blank=False,
                                    verbose_name='Номер платежа')
    payment_sum = MoneyField(max_digits=14,
                             decimal_places=2,
                             default=0,
                             default_currency='RUB',
                             verbose_name='Сумма платежа')
    client_data = models.CharField(max_length=255,
                                   null=True,
                                   default=None,
                                   verbose_name='ФИО клиента')
    payment = models.ForeignKey(Payment,
                                on_delete=models.DO_NOTHING,
                                verbose_name='ID платежа')
    key = models.CharField(max_length=255,
                           blank=False,
                           verbose_name='Цифровая подпись')
    ps_id = models.CharField(max_length=255,
                             blank=False,
                             verbose_name='Идентификатор платежной системы')
    batch_date = models.DateTimeField(
        null=True,
        default=None,
        verbose_name='Дата списания авторизованного платежа')
    fop_receipt_key = models.CharField(null=True,
                                       default=None,
                                       max_length=255,
                                       verbose_name='Код страницы чека 54-ФЗ')
    bank_id = models.CharField(null=True,
                               default=None,
                               max_length=255,
                               verbose_name='Идентификатор привязки карты')
    card_number = models.CharField(null=True,
                                   default=None,
                                   max_length=255,
                                   verbose_name='Маскированный номер карты')
    card_holder = models.CharField(null=True,
                                   default=None,
                                   max_length=255,
                                   verbose_name='Держатель карты')
    card_expiry = models.CharField(null=True,
                                   default=None,
                                   max_length=255,
                                   verbose_name='Срок действия карты')

    class Meta:
        verbose_name = 'Оповещение от PayKeeper'
        verbose_name_plural = 'Оповещения от PayKeeper'
        db_table = 'shop_paykeeper_notice'


class KitCategory(BaseModel):
    """
    Категория программы
    """
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа')
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'Категория программы'
        verbose_name_plural = 'Категории программы'
        db_table = 'shop_kit_category'

    def __str__(self):
        return '%s' % self.category.name


class KitStage(BaseModel):
    """
    Интервал использования программы (утро, день, вечер)
    """
    MORNING = 0
    DAY = 1
    EVENING = 2

    PERIODS = ((MORNING, 'Утро'), (DAY, 'День'), (EVENING, 'Вечер'))
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            verbose_name='Программа',
                            related_name='stages')
    interval = models.CharField(max_length=255,
                                blank=False,
                                verbose_name='Временной интервал')
    period = models.PositiveIntegerField(choices=PERIODS,
                                         verbose_name='Время суток')
    seq_no = models.PositiveIntegerField(verbose_name='Порядковый номер')
    description = models.CharField(max_length=1000,
                                   blank=False,
                                   verbose_name='Описание')
    link_text = models.CharField(max_length=255,
                                 blank=False,
                                 verbose_name='Текст ссылки')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')

    def clean(self):
        if KitStage.objects.filter(
                kit_id=self.kit_id,
                seq_no=self.seq_no,
                interval=self.interval,
                period=self.period,
                deleted__isnull=True,
        ).exclude(id=self.id).exists():
            raise ValidationError(
                f'Для этого интервала и периода уже существует стадия с порядковым номером '
                f'{self.seq_no}!')

    class Meta:
        verbose_name = 'Стадия программы'
        verbose_name_plural = 'Стадии программы'
        db_table = 'shop_kit_stage'

    def __str__(self):
        return '[%s: %s] %s : %s' % (self.interval, self.get_period_display(),
                                     self.seq_no,
                                     self.description + ' ' + self.link_text)


class Event(BaseModel, ImagePreviewModelMixin):
    """
    Маркетологическая акция
    """
    GIFT_FOR_SOME_THE_SAME = 0
    GIFT_FOR_TWO_ANY = 1
    DISCOUNT = 2
    GIFT_FOR_N_FROM_M = 3
    DISCOUNT_FOR_N = 4
    BUNDLE = 5

    EVENT_TYPES = (
        (GIFT_FOR_SOME_THE_SAME, 'Подарок за несколько одинаковых'),
        (GIFT_FOR_TWO_ANY, 'Подарок за n любых'),
        (GIFT_FOR_N_FROM_M, 'Подарок за n из m групп'),
        (DISCOUNT, 'Скидка на товар'),
        (DISCOUNT_FOR_N, 'Скидка на n товаров'),
        (BUNDLE, 'Скидка на комплект'),
    )
    name = models.CharField(max_length=250,
                            db_index=True,
                            blank=False,
                            verbose_name='Наименование акции')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='event_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение')
    event_products_some_the_same = models.ManyToManyField(
        Product,
        through='EventProductSomeTheSame',
        verbose_name='Товары-участники типа "Подарок за несколько одинаковых"',
        related_name='event_products_some_the_same')
    event_products_for2any = models.ManyToManyField(
        Product,
        through='EventProductFor2Any',
        verbose_name='Товары-участники типа "Подарок за n любых"',
        related_name='event_products_for2any')
    event_products_bundle = models.ManyToManyField(
        Product,
        through='EventProductBundle',
        verbose_name='Товары-участники типа "Скидка за комплект"',
        related_name='event_products_bundle')
    started = models.DateTimeField(blank=False,
                                   verbose_name='Дата начала действия')
    ended = models.DateTimeField(blank=False,
                                 verbose_name='Дата завершения действия')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    event_type = models.PositiveIntegerField(choices=EVENT_TYPES,
                                             verbose_name='Тип акции')
    gift = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        default=None,
        on_delete=models.DO_NOTHING,
        verbose_name='Подарок по акции "Подарок за n любых"'
    )
    gift_count = models.PositiveIntegerField(
        blank=True, null=True, default=None,
        verbose_name='Кол-во подарочных товаров, шт')
    for_n_any_quantity = models.PositiveIntegerField(
        blank=True, null=True, default=None,
        verbose_name='Кол-во приобретаемых товаров '
                     'для получения подарка по акции "Подарок за n любых", шт')
    seq_no = models.IntegerField(
        null=True,
        default=None,
        blank=True,
        verbose_name='Порядковый номер')
    discount_product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        default=None,
        on_delete=models.DO_NOTHING,
        verbose_name='Товар со скидкой',
        related_name='discount_product')
    discount = models.PositiveIntegerField(verbose_name='Скидка на товар, %',
                                           blank=True,
                                           null=True,
                                           default=None)
    discount_product_for_n = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        default=None,
        on_delete=models.DO_NOTHING,
        verbose_name='Товар по акции "Скидка за n товаров"',
        related_name='discount_product_for_n')
    discount_for_n = models.PositiveIntegerField(
        verbose_name='Скидка на товар по акции "Скидка за n товаров", %',
        blank=True,
        null=True,
        default=None)
    half_screen = models.BooleanField(
        default=False,
        verbose_name='Карточка акции на половину экрана')
    discount_product_count = models.PositiveIntegerField(
        verbose_name='Кол-во товаров в акции "Скидка за n товаров", шт',
        blank=True,
        null=True,
        default=None)
    bundle_price = models.DecimalField(max_digits=14,
                                       null=True,
                                       blank=True,
                                       default=None,
                                       decimal_places=2,
                                       verbose_name='Цена акции "Скидка за комплект", руб')
    price = models.DecimalField(max_digits=14,
                                blank=False,
                                default=0,
                                decimal_places=2,
                                verbose_name='Цена акции')
    dont_apply_promo = models.BooleanField(
        default=False,
        verbose_name='Промокоды недействительны')
    code = models.CharField(default='',
                            blank=True,
                            max_length=255,
                            verbose_name='Артикул')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['name']
        db_table = 'shop_event'

    def __str__(self):
        return self.name


class EventGroup(BaseModel):
    """
    Группа товаров для акции "Подарок за n товаров из m групп"
    """
    event = models.ForeignKey(
        Event, on_delete=models.DO_NOTHING, verbose_name='Акция', related_name='event_groups')
    seq_no = models.IntegerField(
        verbose_name='Порядковый номер', blank=False, default=1)

    class Meta:
        verbose_name = 'Группа товаров'
        verbose_name_plural = 'Группы товаров'
        ordering = ['seq_no']
        db_table = 'shop_event_group'

    def __str__(self):
        return '%s : %s' % (self.event.name, self.seq_no)


class EventGroupProduct(BaseModel):
    """
    Товары группы акции "Подарок за n товаров из m групп"
    """
    group = models.ForeignKey(
        EventGroup, on_delete=models.DO_NOTHING, verbose_name='Группа', related_name='group_products')
    product = models.ForeignKey(
        Product, verbose_name='Товар', on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Товар группы'
        verbose_name_plural = 'Товары группы'
        ordering = ['product_id']
        db_table = 'shop_event_group_product'

    def __str__(self):
        return '%s : %s' % (self.group.seq_no, self.product.name)


class EventProductSomeTheSame(BaseModel):
    """
    Товар, принимающий участие в акции типа "Подарок за несколько одинаковых"
    """
    event = models.ForeignKey(Event,
                              on_delete=models.DO_NOTHING,
                              verbose_name='Акция')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Кол-во для получения подарка')

    class Meta:
        verbose_name = 'Товар-участник акции "Подарок за несколько одинаковых"'
        verbose_name_plural = 'Товары-участники акции "Подарок за несколько одинаковых"'
        db_table = 'shop_event_product_some_the_same'

    def __str__(self):
        return '%s: %s (%s)' % (self.event.name, self.product.name,
                                self.quantity)


class EventProductFor2Any(BaseModel):
    """
    Товар, принимающий участие в акции типа "Подарок за n любых"
    """
    event = models.ForeignKey(Event,
                              on_delete=models.DO_NOTHING,
                              verbose_name='Акция')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')

    class Meta:
        verbose_name = 'Товар-участник акции "Подарок за n любых"'
        verbose_name_plural = 'Товары-участники акции "Подарок за n любых"'
        db_table = 'shop_event_product_2any'

    def __str__(self):
        return '%s: %s' % (self.event.name, self.product.name)


class EventProductBundle(BaseModel):
    """
    Товар, принимающий участие в акции типа "Скидка за комплект"
    """
    event = models.ForeignKey(Event,
                              on_delete=models.DO_NOTHING,
                              verbose_name='Акция')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Товар')
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Кол-во товаров')

    class Meta:
        verbose_name = 'Товар-участник акции "Скидка за комплект"'
        verbose_name_plural = 'Товары-участники акции "Скидка за комплект"'
        db_table = 'shop_event_product_bundle'

    def __str__(self):
        return '%s: %s' % (self.event.name, self.product.name)


class Slide(BaseModel, ImagePreviewModelMixin):
    """
    Изображение акции
    """
    name = models.CharField(max_length=250,
                            db_index=True,
                            blank=False,
                            verbose_name='Наименование слайда')
    header = models.CharField(max_length=255,
                              verbose_name='Заголовок',
                              blank=False)
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True,
                                    verbose_name='Отображать на сайте')
    seq_no = models.PositiveIntegerField(default=0,
                                         verbose_name='Порядковый номер')
    image = models.ImageField(upload_to='slides/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                null=True,
                                blank=True,
                                verbose_name='Товар')
    kit = models.ForeignKey(Kit,
                            on_delete=models.DO_NOTHING,
                            null=True,
                            blank=True,
                            verbose_name='Программа')
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 null=True,
                                 blank=True,
                                 verbose_name='Категория')
    event = models.ForeignKey(Event,
                              on_delete=models.DO_NOTHING,
                              null=True,
                              blank=True,
                              verbose_name='Акция')
    link = models.CharField(null=True,
                            default=None,
                            blank=True,
                            max_length=500,
                            verbose_name='Ссылка')

    def clean(self):
        not_null_fk_count = 0
        if self.product_id:
            not_null_fk_count += 1
        if self.kit_id:
            not_null_fk_count += 1
        if self.category_id:
            not_null_fk_count += 1
        if self.event_id:
            not_null_fk_count += 1
        if not_null_fk_count > 1:
            raise ValidationError(f'Возможна ссылка только на один объект!')
        if not_null_fk_count == 0 and not self.link:
            raise ValidationError(
                f'Добавьте ссылку хотя бы на один объект или заполните текстовое поле "Ссылка"!'
            )
        if not_null_fk_count == 1 and self.link:
            raise ValidationError(
                f'Удалите ссылку на объект или текстовое поле "Ссылка"!')

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайды'
        ordering = ['name']
        db_table = 'shop_slide'

    def __str__(self):
        return self.name


class OrderBonusHistory(BaseModel):
    """
    История начислений бонусов по заказам
    """
    user = models.ForeignKey(AppUser,
                             verbose_name='Пользователь',
                             on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              on_delete=models.DO_NOTHING,
                              related_name='bonus_history')
    amount = MoneyField(default=0,
                        max_digits=14,
                        decimal_places=2,
                        default_currency='RUB',
                        verbose_name='Сумма начисления')

    class Meta:
        verbose_name = 'Начисления бонусного баланса'
        verbose_name_plural = 'Начисления бонусного баланса'
        db_table = 'shop_order_bonus_change_history'


class OrderGift(BaseModel):
    """
    Подарки по акциям. id = order_id
    """
    gift_description = models.CharField(max_length=1000,
                                        verbose_name='Описание подарка')

    class Meta:
        verbose_name = 'Описание подарка по акции'
        verbose_name_plural = 'Описания подарков по акции'
        db_table = 'view_order_gift'
        managed = False


class PromoCode(BaseModel):
    """
    Действующие промокоды
    """
    GIFT = 0
    DISCOUNT = 1
    REFERRER = 2

    CODE_TYPES = (
        (GIFT, 'Подарок при любом заказе'),
        (DISCOUNT, 'Скидка на весь товар'),
    )

    description = models.CharField(max_length=1000,
                                   verbose_name='Описание',
                                   blank=True,
                                   null=True,
                                   default=None)
    code = models.CharField(max_length=255,
                            blank=False,
                            verbose_name='Код',
                            unique=True)
    started = models.DateTimeField(
        default=tz.now, verbose_name='Дата начала действия промокода')
    ended = models.DateTimeField(
        blank=False, verbose_name='Дата завершения действия промокода')
    code_type = models.PositiveIntegerField(choices=CODE_TYPES,
                                            verbose_name='Тип промокода')
    discount = models.DecimalField(max_digits=10,
                                   decimal_places=2,
                                   blank=True,
                                   null=True,
                                   default=None,
                                   validators=[MinValueValidator(0), MaxValueValidator(1)],
                                   verbose_name='Значение скидки [0..1]')
    gift = models.ForeignKey(Product,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=True,
                             default=None,
                             verbose_name='Подарок')

    def __str__(self):
        return '%s: %s' % (self.code, self.description)

    class Meta:
        db_table = 'shop_promocode'
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class SBRequest(BaseModel):
    """
        Запросы на оплату в Сбербанк
    """
    amount = MoneyField(verbose_name='Сумма платежа',
                        max_digits=14,
                        decimal_places=2,
                        default_currency='RUB',
                        default=0)
    description = models.CharField(verbose_name='Назначение платежа',
                                   max_length=500,
                                   blank=True)
    sb_order_id = models.CharField(
        max_length=50,
        verbose_name='Номер заказа в системе Cбербанка',
        default=None,
        null=True)
    link = models.CharField(max_length=150,
                            verbose_name='Ссылка на заказ в системе Cбербанка',
                            default=None,
                            null=True)
    expired = models.DateTimeField(null=True,
                                   default=None,
                                   verbose_name='Дата окончания действия')
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь')
    order = models.ForeignKey(Order,
                              verbose_name='ID заказа на сайте',
                              on_delete=models.DO_NOTHING)
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, verbose_name='Платеж')

    def get_pay_link(self):
        """
        Получение ссылки на оплату заказа (API Сбербанк-Онлайн)
        :return:
        """
        if self.link and self.expired >= tz.now():
            logger.debug(f'Обнаружена действующая ссылка на оплату заказа {self.order.order_no}')
            return {
                'error': False,
                'message': 'Ссылка на оплату заказа сгенерирована успешно!',
                'data':  self.link
                }
        amount = self.amount.amount
        order_no = self.order.order_no
        currency = self.amount.currency
        currency_code = CODE_LIST.get(currency, '643')

        service_params = get_service_params(service_name='sberbank',
                                            param_names=('api_login',
                                                         'api_password'))
        account_id = service_params.get('api_login')
        password = service_params.get('api_password')
        ref_url = settings.SBERBANK_REF_URL

        description = f'Оплата заказа №{order_no}'
        amount = int(decimal.Decimal(amount) * 100)
        expiration_date_str = self.expired.strftime('%Y-%m-%dT%H:%M:%S')

        href_chunks = list()
        href_chunks.append(
            f'{ref_url}/payment/rest/register.do?userName={account_id}')
        href_chunks.append(f'&amount={amount}')
        href_chunks.append(f'&password={password}')
        href_chunks.append(f'&description="{description}"')
        href_chunks.append(f'&orderNumber={order_no}')
        href_chunks.append(f'&returnUrl={settings.BASE_URL}successful_payment')
        href_chunks.append(f'&expirationDate={expiration_date_str}')
        href_chunks.append(f'&failUrl={settings.BASE_URL}fail_payment')
        href_chunks.append(f'&currency={currency_code}')
        href = ''.join(href_chunks)

        try:
            response = json.loads(requests.post(href).text)
            logger.debug(href)
            logger.debug(response)
            logger.debug(settings.BASE_URL)
            error_message = response.get('errorMessage')
            link = response.get('formUrl')
            if not error_message and link:
                sb_order_id = response.get('orderId')
                logger.info(
                    f'Ссылка на оплату заказа №{order_no} успешно создана. ID транзакции: {sb_order_id}'
                )
                self.sb_order_id = sb_order_id
                self.link = link
                self.save()
                data = {
                    'error': False,
                    'message': 'Ссылка на оплату заказа сгенерирована успешно!',
                    'data':  link
                }
            else:
                logger.error(
                    f'Ошибка получения ссылки на оплату Сбербанка: {response}')
                data = {
                    'error':   True,
                    'message': f'Ошибка получения ссылки: {error_message}',
                    'data':    None
                }
        except (ReadTimeout, ConnectTimeout, ConnectionError, HTTPError) as e:  # pylint: disable=invalid-name
            logger.error(f'Ошибка получения ссылки на оплату Сбербанка: %s', e)
            data = {
                'error':   True,
                'message': 'API Сбербанк Онлайн временно недоступно!',
                'data':    None
            }
        return data

    class Meta:
        verbose_name = 'Запрос на оплату в Сбербанк'
        verbose_name_plural = 'Запросы на оплату в Сбербанк'
        db_table = 'shop_sb_request'
        indexes = [
            models.Index(fields=['sb_order_id']),
        ]


class OrderEvent(BaseModel):
    """
    Акция заказа
    """
    order = models.ForeignKey(
        Order, on_delete=models.DO_NOTHING, verbose_name='Заказ', related_name='order_events')
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING, verbose_name='Акция')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)

    def __str__(self):
        return self.event.name

    class Meta:
        verbose_name = 'Акция заказа'
        verbose_name_plural = 'Акции заказа'
        db_table = 'shop_order_event'
        unique_together = ['order', 'event']


class OrderEventProduct(BaseModel):
    """
    Товары акции заказа
    """
    order_event = models.ForeignKey(
        OrderEvent, on_delete=models.DO_NOTHING, verbose_name='Акция заказа', related_name='order_event_products')
    product = models.ForeignKey(
        Product, on_delete=models.DO_NOTHING, verbose_name='Акционный товар заказа')
    is_gift = models.BooleanField(default=False, verbose_name='Подарок')
    quantity = models.PositiveIntegerField(verbose_name='Количество',
                                           default=0)
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=0,
                       default_currency='RUB',
                       verbose_name='Цена')
    amount = MoneyField(max_digits=14,
                        decimal_places=2,
                        default=1,
                        default_currency='RUB',
                        verbose_name='Сумма')

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = 'Акционный товар заказа'
        verbose_name_plural = 'Акционные товары заказа'
        db_table = 'shop_order_event_products'


class SBNotice(BaseModel):
    """
    Оповещение о состоявшемся платеже от Сбербанк-Онлайн
    """
    request = models.ForeignKey(
        SBRequest,
        verbose_name='ID запроса на получение ссылки',
        on_delete=models.DO_NOTHING,
    )
    status = models.IntegerField(verbose_name='Статус операции в Сбербанк-Онлайн')
    operation = models.CharField(
        verbose_name='Тип операции в сбербанк',
        null=True,
        default=None,
        max_length=255)
    md_order = models.CharField(
        blank=True,
        verbose_name='Идентификатор заказа платежной системы',
        max_length=50,
        default=None)

    class Meta:
        verbose_name = 'Уведомление об оплате от Сбербанк-Онлайн'
        verbose_name_plural = 'Уведомления об оплате от Сбербанк-Онлайн'
        db_table = 'shop_sb_notice'


class ProductEvents(models.Model):
    """
    Вьюха связок товар-акция для отображения акций, в которые входит товар,
    в сериализаторе товара
    """
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name='ID')
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING, verbose_name='Акция')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name='Товар')

    class Meta:
        verbose_name = 'Связка товар-акция'
        verbose_name_plural = 'Связки товар-акция'
        db_table = 'view_event_product'
        managed = False


class LinkedEvent(BaseModel):
    """
    Связка товар <-> рекомендуемые акции
    """
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                related_name='linked_events',
                                verbose_name='Товар')
    event = models.ForeignKey(
        Event,
        related_name='linked_event',
        on_delete=models.DO_NOTHING,
        verbose_name='Акция')

    def __str__(self):
        return '%s <-> %s' % (self.product.name, self.event.name)

    class Meta:
        verbose_name = 'Рекомендуемая акция'
        verbose_name_plural = 'Рекомендуемые акции'
        db_table = 'shop_linked_event'


class FeedbackProductImage(BaseModel, ImagePreviewModelMixin):
    """
    Изображения отзыва о товаре
    """
    feedback = models.ForeignKey(ProductFeedback, on_delete=models.DO_NOTHING,
                                 verbose_name='Отзыв о товаре',
                                 related_name='prod_feedback_images')
    image = models.ImageField(upload_to='feedback_images/%Y/%m/%d/',
                              blank=False,
                              verbose_name='Изображение отзыва')

    class Meta:
        verbose_name = 'Изображение отзыва о товаре'
        verbose_name_plural = 'Изображения отзыва о товаре'
        db_table = 'shop_product_feedback_image'

    def __str__(self):
        return '%s: %s' % (self.feedback.product.name, self.image)


class FeedbackKitImage(BaseModel, ImagePreviewModelMixin):
    """
    Изображения отзыва о программе
    """
    feedback = models.ForeignKey(KitFeedback, on_delete=models.DO_NOTHING,
                                 verbose_name='Отзыв о программе',
                                 related_name='kit_feedback_images')
    image = models.ImageField(upload_to='feedback_images/%Y/%m/%d/',
                              blank=False,
                              verbose_name='Изображение отзыва')

    class Meta:
        verbose_name = 'Изображение отзыва о программе'
        verbose_name_plural = 'Изображения отзыва о программе'
        db_table = 'shop_kit_feedback_image'

    def __str__(self):
        return '%s: %s' % (self.feedback.kit.name, self.image)


class DefaultDeliveryPrice(BaseModel):
    CHOICES = [
        item for item in settings.SHIPPING_METHODS
        if item[0] not in (
            settings.SMALL_PACKET,
            settings.PICKUP)
    ]

    delivery_type = models.IntegerField(choices=CHOICES,
                                        unique=True,
                                        verbose_name='Способ доставки')
    price = MoneyField(max_digits=14,
                       decimal_places=2,
                       default=200,
                       blank=False,
                       default_currency='RUB',
                       verbose_name='Стоимость доставки')

    class Meta:
        verbose_name = 'Стоимость способа доставки по умолчанию'
        verbose_name_plural = 'Стоимости способов доставки по умолчанию'
        db_table = 'shop_delivery_price'

    def __str__(self):
        return '%s: %s' % (self.get_delivery_type_display(), self.price)


def order_pre_save(sender, instance, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Изменение статуса заказа после оплаты
    :param sender:
    :param instance:
    :param args:
    :param kwargs:
    :return:
    """
    if instance.is_payed:
        if instance.payed is None:
            instance.payed = tz.now()
        if instance.status == Order.ACTIVE:
            instance.status = Order.PAYED


signals.pre_save.connect(order_pre_save, sender=Order)
