"""
Appuser serializers
"""
import uuid
from datetime import timedelta

from django.conf import settings
from django.db.models import DateTimeField, ExpressionWrapper, F
from django.utils import timezone as tz
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.serializers import EagerLoadingMixin, FilteredListSerializer
from core.utils import normalize_phone
from shop.models import BonusParams
from .models import (Address, AppUser, BonusChangeHistory, JurProfile,
                     PhysProfile, Referral, ReferrerOrder, UserAddress)
from .validators import PhoneUniqueValidator


class AddressSzr(serializers.ModelSerializer):
    """
        Сериализатор адреса клиента
    """
    class Meta:
        model = Address
        list_serializer_class = FilteredListSerializer
        fields = ('id', 'postcode', 'country', 'region', 'district',
                  'building', 'city', 'settlement', 'street', 'house', 'flat',
                  'kladr_id', 'oksm_id', 'cdek_city_id')


class PhysProfileSzr(serializers.ModelSerializer):
    """
        Сериализатор данных физлица
    """
    class Meta:
        model = PhysProfile
        fields = ('id', 'phone_number', 'birth_date', 'doc_type', 'doc_number',
                  'doc_issue_date', 'doc_authority')


class JurProfileSzr(serializers.ModelSerializer):
    """
        Сериализатор данных юрлица
    """
    class Meta:
        model = JurProfile
        fields = ('id', 'phone_number', 'inn', 'org_name', 'manager_name',
                  'agent_name')


class UserAddrSzr(serializers.HyperlinkedModelSerializer):
    """
        Сериализатор связки пользователь-адрес
    """
    address_id = serializers.ReadOnlyField(source='address.id')
    postcode = serializers.ReadOnlyField(source='address.postcode')
    country = serializers.ReadOnlyField(source='address.country')
    region = serializers.ReadOnlyField(source='address.region')
    district = serializers.ReadOnlyField(source='address.district')
    building = serializers.ReadOnlyField(source='address.building')
    city = serializers.ReadOnlyField(source='address.city')
    settlement = serializers.ReadOnlyField(source='address.settlement')
    street = serializers.ReadOnlyField(source='address.street')
    house = serializers.ReadOnlyField(source='address.house')
    flat = serializers.ReadOnlyField(source='address.flat')
    kladr_id = serializers.ReadOnlyField(source='address.kladr_id')

    class Meta:
        model = UserAddress
        fields = ('id', 'address_id', 'is_primary', 'postcode', 'country',
                  'region', 'district', 'building', 'city', 'settlement',
                  'street', 'house', 'flat', 'kladr_id')


class UserGetSzr(serializers.ModelSerializer):
    """
        Сериализатор просмотра профиля пользователя
    """
    addresses = UserAddrSzr(source='useraddress_set', many=True)
    phys_profile = PhysProfileSzr()
    jur_profile = JurProfileSzr()
    ref_link = serializers.SerializerMethodField()
    partner_type = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    next_target = serializers.SerializerMethodField()
    available_bonus_amount = serializers.SerializerMethodField()
    promo = serializers.SerializerMethodField()

    def get_next_target(self, obj):  # pylint: disable=no-self-use
        """
        Получение значения следующего целевого показателя
        """
        return obj.get_next_target_value()

    def get_user_type(self, obj):  # pylint: disable=no-self-use
        """
        Получение текстового представления типа пользователя (AppUser.USER_TYPES)
        """
        return obj.get_user_type_display()

    def get_ref_link(self, obj):  # pylint: disable=no-self-use
        """
        Получение реферральной ссылки
        """
        return obj.get_ref_link()

    def get_partner_type(self, obj):  # pylint: disable=no-self-use
        """
        Получение текстового представления типа партнера (AppUser.PARTNER_TYPES)
        :param obj:
        :return:
        """
        return obj.get_partner_type_id_display()

    def get_available_bonus_amount(self, obj):  # pylint: disable=no-self-use
        """
        Получение бонусного баланса, доступного для использования
        """
        return obj.get_available_bonus_amount()

    def get_promo(self, obj):  # pylint: disable=no-self-use
        """
        Получение реферрального промокода
        """
        return settings.REF_PROMO_PREFIX + str(obj.ref_id)

    class Meta:
        model = AppUser
        fields = (
            'id',
            'username',
            'email',
            'phone',
            'last_name',
            'first_name',
            'patronymic',
            'ref_link',
            'sms_notice',
            'email_notice',
            'balance',
            'bonus_balance',
            'total_amount',
            'is_jur',
            'partner_type',
            'user_type',
            'ref_id',
            'current_discount',
            'total_sale_amount',
            'current_period_sale_amount',
            'last_period_sale_amount',
            'total_payments',
            'current_period_payments',
            'last_period_payments',
            'total_bonus_payments',
            'current_period_bonus_payments',
            'last_period_bonus_payments',
            'current_target',
            'next_target',
            'available_bonus_amount',
            'avatar',
            'promo',
            'is_old',
            'addresses',
            'phys_profile',
            'jur_profile',
        )
        read_only_fields = fields


class UserEditSzr(serializers.ModelSerializer):
    """
        Сериализатор редактирования профиля пользователя
    """
    addresses = AddressSzr(many=True, required=False)
    phys_profile = PhysProfileSzr(required=False)
    jur_profile = JurProfileSzr(required=False)
    phone = serializers.CharField(
        required=False,
        validators=[
            PhoneUniqueValidator(
                queryset=AppUser.objects.all(),
                message='Пользователь с этим номером телефона уже зарегистрирован!')],)
    email = serializers.EmailField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=AppUser.objects.all(),
                message='Пользователь с этим email уже зарегистрирован!')], )

    def update(self, instance, validated_data):  # pylint: disable=no-self-use
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.patronymic = validated_data.get('patronymic',
                                                 instance.patronymic)
        instance.email = validated_data.get('email', instance.email)
        phone = normalize_phone(validated_data.get('phone'))
        instance.phone = phone
        instance.is_jur = validated_data.get('is_jur', instance.is_jur)
        instance.sms_notice = validated_data.get('sms_notice',
                                                 instance.sms_notice)
        instance.email_notice = validated_data.get('email_notice',
                                                   instance.email_notice)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        user_id = instance.id
        try:
            addresses = self.initial_data.pop('addresses')
            user_addr_ids = [a.get('id', None) for a in addresses]
            user_addr_ids = [a for a in user_addr_ids if a is not None]
            UserAddress.objects.filter(user_id=user_id).exclude(
                id__in=user_addr_ids).delete()
            for a in addresses:  # pylint: disable=invalid-name
                is_primary = a.pop('is_primary', False)
                address_id = a.pop('address_id', None)
                user_address_id = a.pop('id', None)
                adr, _ = Address.objects.update_or_create(
                    id=address_id, kladr_id=a['kladr_id'], defaults=a)
                UserAddress.objects.update_or_create(id=user_address_id,
                                                     defaults={
                                                         'user_id': user_id,
                                                         'address_id': adr.id,
                                                         'is_primary':
                                                         is_primary
                                                     })
        except KeyError:
            pass
        try:
            phys_profile = self.initial_data.pop('phys_profile')
            phys_profile_id = phys_profile.get('id', None)
            if not phys_profile_id:
                PhysProfile.objects.filter(user_id=user_id).delete()
            if phys_profile != dict():
                PhysProfile.objects.update_or_create(id=phys_profile_id,
                                                     user_id=user_id,
                                                     defaults=phys_profile)
        except KeyError:
            pass

        try:
            jur_profile = self.initial_data.pop('jur_profile')
            jur_profile_id = jur_profile.get('id', None)
            if not jur_profile_id:
                JurProfile.objects.filter(user_id=user_id).delete()
            if jur_profile != dict():
                JurProfile.objects.update_or_create(id=jur_profile_id,
                                                    user_id=user_id,
                                                    defaults=jur_profile)
        except KeyError:
            pass
        return instance

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'first_name', 'last_name', 'patronymic',
                  'email', 'phone', 'is_jur', 'addresses', 'phys_profile',
                  'jur_profile')
        extra_kwargs = {
            'phone': {
                'error_messages': {
                    'unique': 'Пользователь с этим номером телефона уже зарегистрирован!'}
            },
            'email': {
                'error_messages': {
                    'unique': 'Пользователь с этим email уже зарегистрирован!'}
            }
        }


