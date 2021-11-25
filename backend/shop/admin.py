"""
Shop admin
"""
import logging

import nested_admin
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Sum
from django.utils import timezone as tz
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from djmoney.models.fields import Money

from core.admin import BaseModelAdmin
from core.tasks import sitemap_generate
from core.utils import isnull
from .models import (ActiveComponent, Advice, AdviceType, BonusParams,
                     Category, Event, EventProductFor2Any, LinkedEvent,
                     EventProductSomeTheSame, Kit, KitAdvice, KitCategory,
                     KitFeedback, KitImage, KitPreference, KitProduct,
                     KitStage, LinkedProduct, Order, OrderKit, OrderProduct,
                     Product, ProductComponent, ProductFeedback, ProductImage,
                     PromoCode, Slide, SubCategory, SubCatProduct, OrderEvent,
                     OrderEventProduct, EventGroup, EventGroupProduct, Payment,
                     FeedbackProductImage, FeedbackKitImage, EventProductBundle,
                     DefaultDeliveryPrice)

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


def process_order(obj):
    """Обработка заказа после сохранения"""
    paid_amounts = Payment.objects.filter(
        order_id=obj.id,
        confirmation_date__isnull=False).aggregate(
            amount_sum=Sum('amount'),
            bonus_sum=Sum('bonus_amount'),
            deposit_sum=Sum('deposit_amount'))
    total_paid_amount = Money(isnull(paid_amounts['amount_sum'], 0) +
                              isnull(paid_amounts['bonus_sum'], 0) +
                              isnull(paid_amounts['deposit_sum'], 0), 'RUB')
    if total_paid_amount < obj.total_amount + obj.shipping_amount:
        Payment.objects.create(amount=obj.total_amount + obj.shipping_amount,
                               bonus_amount=0,
                               deposit_amount=0,
                               confirmation_date=tz.now(),
                               payment_source=Payment.CASHLESS,
                               order_id=obj.id,
                               order_no=obj.order_no)
    if not obj.is_track_created and obj.is_payed:
        obj.change_status(Order.PAYED)
        obj.create_track()
        track = obj.shipping_method_id == settings.RUSSIAN_POST
        obj.change_status_send_notice(track=track)
        obj.send_sms_notice_order_payed(track=track)
        obj.send_payment_notice_admin(obj.total_amount + obj.shipping_amount, from_admin=True)
        if track:
            obj.is_track_sended = True
            obj.save()
    if obj.is_payed and obj.is_ready:
        obj.send()


class FormfieldForProductFKMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product':
            kwargs['queryset'] = Product.objects.filter(
                deleted__isnull=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductComponentsInline(admin.TabularInline):
    model = ProductComponent
    fields = ('component', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'component':
            kwargs['queryset'] = ActiveComponent.objects.filter(
                deleted__isnull=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(ProductComponentsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class ProductImagesInline(admin.TabularInline):
    model = ProductImage
    fields = ('image', 'image_tag', 'created')
    readonly_fields = ('created', 'image_tag')
    extra = 0
    can_delete = True

    def get_queryset(self, request):
        qs = super(ProductImagesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class ProductSubCategoryInline(admin.TabularInline):
    model = SubCatProduct
    readonly_fields = ('created', )
    fields = ('subcategory', 'created')
    extra = 1
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'subcategory':
            kwargs['queryset'] = SubCategory.objects.filter(
                deleted__isnull=True).order_by('category', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(ProductSubCategoryInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class LinkedProductsInline(admin.TabularInline):
    model = LinkedProduct
    fk_name = 'product'
    readonly_fields = ('product', )
    fields = ('product', 'lnkd_product')
    extra = 1
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lnkd_product':
            kwargs['queryset'] = Product.objects.filter(
                deleted__isnull=True).order_by('product_no')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(LinkedProductsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class LinkedEventsInLine(admin.TabularInline):
    model = LinkedEvent
    readonly_fields = ('product',)
    fields = ('product', 'event')
    extra = 1
    can_delete = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'event':
            kwargs['queryset'] = Event.objects.filter(
                deleted__isnull=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(LinkedEventsInLine, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class ProductAdmin(BaseModelAdmin):
    list_display = ('product_no', 'code', 'name', 'description', 'price',
                    'is_available', 'weight', 'volume', 'created', 'updated',
                    'image_tag')
    list_editable = ('name', 'code', 'description', 'price', 'is_available',
                     'weight', 'volume')
    fields = ('product_no', 'slug', 'code', 'name', 'english_name', 'description',
              'short_description', 'price', 'is_available', 'hit_count',
              'weight', 'gross_weight', 'volume', 'length', 'width', 'height',
              'packing_volume', 'primary_image', 'image_tag', 'result',
              'usage', 'certificate', 'hit', 'new', 'discount', 'rating',
              'avatar')
    search_fields = ('name', 'description', 'code')
    ordering = ('product_no', )
    readonly_fields = ('product_no', 'created', 'updated', 'image_tag')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.product_no = obj.get_next_seq_no()
        obj.save()
        sitemap_generate.delay(settings.SITEMAP_GENERATE_PATH)

    inlines = [
        ProductImagesInline,
        ProductComponentsInline,
        ProductSubCategoryInline,
        LinkedProductsInline,
        LinkedEventsInLine
    ]


class KitImagesInline(admin.TabularInline):
    model = KitImage
    fields = ('created', 'image', 'image_tag')
    readonly_fields = ('created', 'image_tag')
    extra = 0
    can_delete = True

    def get_queryset(self, request):
        qs = super(KitImagesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitProductsInline(FormfieldForProductFKMixin, admin.TabularInline):
    model = KitProduct
    fields = ('product', 'products_count', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('product', )

    def get_queryset(self, request):
        qs = super(KitProductsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitCategoriesInline(admin.TabularInline):
    model = KitCategory
    fields = ('category', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('category', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(
                deleted__isnull=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(KitCategoriesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitPreferencesInline(admin.TabularInline):
    model = KitPreference
    fields = ('seq_no', 'description', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('seq_no', )

    def get_queryset(self, request):
        qs = super(KitPreferencesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitAdvicesInline(admin.TabularInline):
    model = KitAdvice
    fk_name = 'kit'
    fields = ('seq_no', 'header', 'description', 'link_text', 'advice_kit',
              'image', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('seq_no', )

    def get_queryset(self, request):
        qs = super(KitAdvicesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitStagesInline(FormfieldForProductFKMixin, admin.TabularInline):
    model = KitStage
    fields = ('interval', 'period', 'seq_no', 'description', 'link_text',
              'product', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = (
        'interval',
        'period',
        'seq_no',
    )

    def get_queryset(self, request):
        qs = super(KitStagesInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class KitAdmin(BaseModelAdmin):
    list_display = ('kit_no', 'name', 'description', 'price', 'created',
                    'updated', 'image_tag')
    list_editable = ('name', 'description')
    fields = ('kit_no', 'slug', 'name', 'hit_count', 'description', 'price',
              'primary_image', 'image_tag', 'length', 'width', 'height',
              'weight', 'gross_weight', 'packing_volume', 'problem',
              'target', 'preference', 'usage_period', 'formula',
              'is_active')
    search_fields = ('name', 'description')
    ordering = ('kit_no', )
    readonly_fields = ('kit_no', 'created', 'updated', 'image_tag')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.kit_no = obj.get_next_seq_no()
        obj.save()
        sitemap_generate.delay(settings.SITEMAP_GENERATE_PATH)

    inlines = [
        KitImagesInline, KitProductsInline, KitCategoriesInline,
        KitPreferencesInline, KitAdvicesInline, KitStagesInline
    ]


class CategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'description', 'image_tag')
    list_editable = ('description', )
    fields = ('name', 'description', 'image', 'header_image',
              'slug', 'SEO_title', 'SEO_description')
    search_fields = ('name', 'description')
    ordering = ('name', )
    readonly_fields = ('created', 'updated')

    def save_model(self, request, obj, form, change):
        obj.save()
        sitemap_generate.delay(settings.SITEMAP_GENERATE_PATH)


class KitFeedbackImageInline(admin.TabularInline):
    model = FeedbackKitImage
    fields = ('image', 'image_tag',)
    readonly_fields = ('image_tag', )
    extra = 0
    can_delete = True


class KitFeedbackAdmin(BaseModelAdmin):
    list_display = ('created', 'order_no', 'approved',
                    'show_on_main_page', 'kit', 'user', 'text')
    list_editable = ('order_no', 'approved', 'show_on_main_page')
    fields = ('created', 'order_no', 'approved', 'show_on_main_page',
              'kit', 'user', 'text', 'video_link', 'with_text')
    search_fields = ('text', 'user__username', 'kit__name')
    ordering = ('-created', )
    readonly_fields = ('created', 'updated')
    raw_id_fields = ('user',)
    inlines = (KitFeedbackImageInline, )


class ProductFeedbackImageInline(admin.TabularInline):
    model = FeedbackProductImage
    fields = ('image', 'image_tag',)
    readonly_fields = ('image_tag',)
    extra = 0
    can_delete = True

    def get_queryset(self, request):
        qs = super(ProductFeedbackImageInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class FeedbackImageInline(admin.TabularInline):
    model = FeedbackProductImage
    exclude = ('deleted',)
    extra = 0


class ProductFeedbackAdmin(BaseModelAdmin):
    list_display = ('created', 'order_no', 'approved', 'show_on_main_page',
                    'product', 'user', 'text', 'rating')
    list_editable = ('order_no', 'approved', 'show_on_main_page')
    fields = ('approved', 'order_no', 'show_on_main_page', 'product', 'user',
              'text', 'video_link', 'rating', 'with_text')
    search_fields = ('text', 'user__username', 'product__name')
    ordering = ('-created', )
    readonly_fields = ('created', 'updated')
    raw_id_fields = ('user',)
    inlines = (ProductFeedbackImageInline, )


class ComponentAdmin(BaseModelAdmin, DynamicArrayMixin):
    list_display = ('created', 'name', 'short_description', 'description',
                    'image_tag')
    list_editable = (
        'name',
        'short_description',
        'description',
    )
    fields = ('name', 'slug', 'short_description', 'description', 'image',
              'image_tag', 'benefits')
    search_fields = ('name', )
    ordering = ('-created', )
    readonly_fields = ('created', 'image_tag')


class SubCategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'category', 'description', 'slug')
    list_editable = ('description', 'slug')
    fields = ('category', 'created', 'name', 'description', 'slug',
              'SEO_title', 'SEO_description')
    search_fields = ('name', 'description')
    ordering = (
        'category',
        'name',
    )
    readonly_fields = ('created', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(
                deleted__isnull=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        sitemap_generate.delay(settings.SITEMAP_GENERATE_PATH)


class OrderProductsInline(nested_admin.NestedTabularInline):
    model = OrderProduct
    fields = ('product', 'quantity', 'price', 'amount')
    ordering = ('product', )
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        qs = super(OrderProductsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class OrderKitsInline(nested_admin.NestedTabularInline):
    model = OrderKit
    fields = ('kit', 'quantity', 'price', 'amount')
    ordering = ('kit', )
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        qs = super(OrderKitsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class OrderEventProductsInline(nested_admin.NestedTabularInline):
    model = OrderEventProduct
    fields = ('product', 'is_gift', 'quantity', 'price', 'amount')
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'is_gift', 'quantity', 'price', 'amount')

    def get_queryset(self, request):
        qs = super(OrderEventProductsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class OrderEventsInline(nested_admin.NestedTabularInline):
    model = OrderEvent
    fields = ('event', 'quantity')
    extra = 0
    can_delete = False
    inlines = [OrderEventProductsInline, ]

    def get_queryset(self, request):
        qs = super(OrderEventsInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class OrderAdmin(BaseModelAdmin, nested_admin.NestedModelAdmin):
    list_display = ('order_no', 'user', 'manager', 'total_amount',
                    'created', 'payed', 'status', 'track_no',
                    'shipping_method_id', 'is_ready', 'is_payed')
    list_editable = ('track_no', 'is_ready', 'is_payed')
    fields = (
        'order_no',
        'user',
        'phone',
        'manager',
        'email',
        'order_type',
        'total_amount',
        'created',
        'payed',
        'status',
        'track_no',
        'shipping_method_id',
        'delivery_point_id',
        'delivery_point_address',
        'address',
        'total_weight',
        'total_volume',
        'is_ready',
        'is_payed',
        'is_track_sended',
        'create_shipment_result',
        'create_shipment_request_last_date',
        'memo',
        'promocode',
        'payment_bonus_amount'
    )
    search_fields = (
        'order_no',
        'user__username',
        'user__email',
        'track_no',
        'manager__username',
        'manager__email')
    ordering = ('-order_no', )
    readonly_fields = ['order_no', 'user', 'total_amount',
                       'created', 'payed', 'manager',
                       'address', 'status', 'order_type',
                       'total_weight', 'total_volume',
                       'create_shipment_result', 'is_track_sended',
                       'create_shipment_request_last_date',
                       'shipping_method_id', 'delivery_point_id',
                       'memo', 'email', 'phone', 'promocode',
                       'delivery_point_address', 'payment_bonus_amount']
    list_filter = ('status', )
    list_per_page = 25

    def payment_bonus_amount(self, obj):
        return obj.get_payment_bonus_amount()
    payment_bonus_amount.allow_tags = True
    payment_bonus_amount.short_description = 'Сумма бонусов, потраченных на оплату заказа'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.order_no = obj.get_next_seq_no()
        if obj.is_payed \
                and obj.is_ready \
                and isnull(obj.track_no, '') == '' \
                and obj.shipping_method_id != settings.PICKUP:
            messages.error(request, f'Заказ {obj.order_no}: не заполнен номер трека!')
        obj.save()
        process_order(obj)

    def get_readonly_fields(self, request, obj=None):
        """Метод формирования маассива полей readonly"""
        if request.user.is_superuser:
            return self.readonly_fields
        self.readonly_fields.append('is_payed')
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if not settings.DEBUG:
            qs = qs.exclude(user_id__in=settings.TEST_USER_IDS)
        return qs

    inlines = [
        OrderProductsInline,
        OrderKitsInline,
        OrderEventsInline
    ]


class AdviceTypeAdmin(BaseModelAdmin):
    list_display = ('type_name', 'tag', 'created')
    fields = (
        'type_name',
        'tag',
        'created',
    )
    search_fields = ('type_name', 'tag')
    ordering = ('type_name', )
    readonly_fields = ('created', )


class AdviceAdmin(BaseModelAdmin):
    list_display = ('advice_type', 'name', 'phone', 'email', 'text')
    fields = ('advice_type', 'name', 'phone', 'email', 'text')
    search_fields = ('name', 'phone', 'email', 'advice_type')
    ordering = ('-created', )
    readonly_fields = ('created', )


class BonusParamsAdmin(BaseModelAdmin):
    model = BonusParams
    list_display = ('partner_type_id', 'target', 'bonus_share',
                    'own_bonus_share', 'discount', 'started', 'ended')
    list_editable = ('target', 'bonus_share', 'own_bonus_share', 'discount',
                     'started', 'ended')
    fields = ('partner_type_id', 'target', 'bonus_share', 'own_bonus_share',
              'discount', 'started', 'ended')
    ordering = ('partner_type_id', 'target')


class SlideAdmin(BaseModelAdmin):
    model = Slide
    list_display = (
        'created',
        'name',
        'header',
        'description',
        'image_tag',
    )
    list_editable = (
        'name',
        'header',
        'description',
    )
    fields = ('name', 'header', 'description', 'image', 'product', 'kit',
              'category', 'event')
    readonly_fields = ('created', 'image_tag')
    ordering = ('name', )


class EventProductFor2AnyInline(FormfieldForProductFKMixin,
                                nested_admin.NestedTabularInline):
    model = EventProductFor2Any
    fields = ('product', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('product', )

    def get_queryset(self, request):
        qs = super(EventProductFor2AnyInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class EventProductBundleInline(FormfieldForProductFKMixin,
                               nested_admin.NestedTabularInline):
    model = EventProductBundle
    fields = ('product', 'quantity', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('product', )

    def get_queryset(self, request):
        qs = super(EventProductBundleInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class EventProductSomeTheSameInline(FormfieldForProductFKMixin,
                                    nested_admin.NestedTabularInline):
    model = EventProductSomeTheSame
    fields = ('product', 'quantity', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True
    ordering = ('product', )

    def get_queryset(self, request):
        qs = super(EventProductSomeTheSameInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class EventGroupProductInline(FormfieldForProductFKMixin,
                              nested_admin.NestedTabularInline):
    model = EventGroupProduct
    fields = ('product', )
    extra = 0
    can_delete = True
    ordering = ('product', )

    def get_queryset(self, request):
        qs = super(EventGroupProductInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class EventGroupInline(nested_admin.NestedTabularInline):
    model = EventGroup
    fields = ('seq_no', )
    extra = 0
    can_delete = True
    ordering = ('seq_no', )
    inlines = [EventGroupProductInline, ]

    def get_queryset(self, request):
        qs = super(EventGroupInline, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)


class EventAdmin(BaseModelAdmin, nested_admin.NestedModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):  # pylint: disable=arguments-differ
        context['adminform'].form.fields['discount_product'].queryset = \
            Product.objects.filter(deleted__isnull=True, discount__gt=0).order_by('name')
        context['adminform'].form.fields['discount_product_for_n'].queryset = \
            Product.objects.filter(deleted__isnull=True).order_by('name')
        return super(EventAdmin, self).render_change_form(request, context, *args, **kwargs)

    model = Event
    list_display = (
        'name',
        'seq_no',
        'code',
        'event_type',
        'description',
        'started',
        'ended',
        'is_active',
        'image_tag',
    )
    list_editable = (
        'seq_no',
        'code',
        'event_type',
        'description',
        'started',
        'ended',
        'is_active',
    )
    fields = ('name', 'seq_no', 'code', 'price', 'event_type', 'description',
              'image', 'started', 'ended', 'is_active', 'gift',
              'gift_count', 'for_n_any_quantity', 'discount_product',
              'discount', 'discount_product_for_n', 'discount_product_count',
              'discount_for_n', 'bundle_price', 'half_screen',
              'dont_apply_promo')
    readonly_fields = ('created', 'image_tag', 'discount')
    list_filter = ('event_type', )
    ordering = ('name', )
    inlines = [
        EventProductFor2AnyInline,
        EventProductSomeTheSameInline,
        EventProductBundleInline,
        EventGroupInline
    ]


class PromoCodeAdmin(BaseModelAdmin):
    model = PromoCode
    list_display = ('code', 'description', 'code_type', 'started', 'ended')
    list_editable = ('started', 'ended')
    fields = ('code', 'code_type', 'description', 'started', 'ended',
              'discount', 'gift')
    ordering = ('-started', )


class DefaultDeliveryPriceAdmin(admin.ModelAdmin):
    model = DefaultDeliveryPrice
    list_display = ('delivery_type', 'price')
    list_editable = ('price', )
    fields = ('delivery_type', 'price')
    ordering = ('delivery_type',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Kit, KitAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(KitFeedback, KitFeedbackAdmin)
admin.site.register(ProductFeedback, ProductFeedbackAdmin)
admin.site.register(ActiveComponent, ComponentAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(AdviceType, AdviceTypeAdmin)
admin.site.register(Advice, AdviceAdmin)
admin.site.register(BonusParams, BonusParamsAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(DefaultDeliveryPrice, DefaultDeliveryPriceAdmin)
