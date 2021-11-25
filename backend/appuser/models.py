"""
Appuser models
"""
import os
import uuid
from datetime import timedelta
from operator import attrgetter
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils import timezone as tz
from djmoney.models.fields import MoneyField

from core.models import OKSM, BaseModel
from core.utils import get_next_id, isnull


def avatar_path(instance, filename):
    """
    Функция, генерирующая путь для сохранения аватара пользователя
    :param instance: объект "Пользователь"
    :param filename: имя файла
    :return: путь к сохраняемому файлу
    """
    return os.path.join('avatars', f'{str(instance.id)}', filename)


class Address(BaseModel):
    """
    Адрес
    """
    name = models.CharField(max_length=255,
                            blank=True,
                            verbose_name='Краткое наименование адреса')
    postcode = models.CharField(max_length=10,
                                blank=True,
                                null=True,
                                default='',
                                verbose_name='Почтовый индекс')
    country = models.CharField(max_length=255,
                               blank=True,
                               null=True,
                               default='',
                               verbose_name='Страна')
    region = models.CharField(max_length=255,
                              blank=True,
                              null=True,
                              default='',
                              verbose_name='Область')
    district = models.CharField(max_length=255,
                                blank=True,
                                null=True,
                                default='',
                                verbose_name='Район')
    city = models.CharField(max_length=255,
                            blank=True,
                            null=True,
                            default='',
                            verbose_name='Город')
    settlement = models.CharField(max_length=255,
                                  blank=True,
                                  null=True,
                                  default='',
                                  verbose_name='Населенный пункт')
    street = models.CharField(max_length=255,
                              blank=True,
                              null=True,
                              default='',
                              verbose_name='Улица')
    house = models.CharField(max_length=64,
                             blank=True,
                             null=True,
                             default='',
                             verbose_name='Номер дома')
    building = models.CharField(max_length=64,
                                blank=True,
                                null=True,
                                default='',
                                verbose_name='Номер строения')
    flat = models.CharField(max_length=64,
                            blank=True,
                            null=True,
                            default='',
                            verbose_name='Номер квартиры')
    kladr_id = models.CharField(max_length=20,
                                blank=True,
                                null=True,
                                default=None,
                                verbose_name='Код КЛАДР',
                                db_index=True)
    oksm = models.ForeignKey(OKSM,
                             on_delete=models.DO_NOTHING,
                             blank=True,
                             null=True,
                             default=643,
                             verbose_name='Код ОКСМ')
    cdek_city_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Код города по базе СДЭК')

    def get_formatted_address(self):
        """
        Метод получения отформатированного адреса одной строкой
        :return:
        """
        address = []
        field_names = [
            f.name for f in Address._meta.get_fields(include_hidden=False,
                                                     include_parents=False)
            if f.name in ('postcode', 'country', 'region', 'district',
                          'settlement', 'city', 'street', 'house', 'building',
                          'flat')
        ]
        for field_name in field_names:
            f = attrgetter(field_name)  # pylint: disable=invalid-name
            field_value = f(self)
            if field_value is not None:
                address.append(f'{field_value}')
        return ', '.join(address)

    class Meta:
        verbose_name = 'Адрес клиента'
        verbose_name_plural = 'Адреса клиентов'
        db_table = 'appuser_address'

    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s' % (
            isnull(self.postcode, ''), isnull(self.region, ''),
            isnull(self.city, ''), isnull(self.settlement, ''),
            isnull(self.street, ''), isnull(self.house,
                                            ''), isnull(self.flat, ''))


class AppUser(AbstractUser):
    """
        Пользователь
    """
    RETAIL = 1
    WHOLESALE = 2
    DISTRIBUTOR = 3
    MANAGER = 4

    PARTNER_TYPES = ((RETAIL, 'Партнер 1 уровня (розница)'),
                     (WHOLESALE, 'Партнер 2 уровня (опт)'),
                     (DISTRIBUTOR, 'Партнер 3 уровня (дистрибьютор)'),
                     (MANAGER, 'Менеджер'))

    NATIVE = 0
    FACEBOOK = 1
    VKONTAKTE = 2

    USER_TYPES = ((NATIVE, 'Site'), (FACEBOOK, 'FB'), (VKONTAKTE, 'VK'))

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name='ID пользователя')
    memo = models.CharField(max_length=255,
                            blank=True,
                            null=True,
                            verbose_name='Примечание')
    username = models.CharField(
        max_length=150,
        unique=True,
        default=str(uuid.uuid4()).replace('-', ''),
        error_messages={
            'unique': "Пользователь с таким логином уже существует!",
        },
        verbose_name='Логин')
    is_active = models.BooleanField(verbose_name='Активный', default=True)
    is_jur = models.BooleanField(default=False, verbose_name='Юрлицо')
    email = models.EmailField(verbose_name='Email',
                              max_length=255,
                              blank=False,
                              unique=True,
                              default=str(uuid.uuid4()).replace('-', ''))
    phone = models.CharField(verbose_name='Номер телефона',
                             blank=False,
                             max_length=255,
                             unique=True,
                             default=str(uuid.uuid4()).replace('-', ''))
    jwt_secret = models.UUIDField(default=uuid4)
    first_name = models.CharField(max_length=255,
                                  verbose_name='Имя',
                                  blank=False)
    last_name = models.CharField(max_length=255,
                                 blank=False,
                                 verbose_name='Фамилия')
    patronymic = models.CharField(max_length=255,
                                  blank=True,
                                  null=True,
                                  default='',
                                  verbose_name='Отчество')
    contact_id = models.IntegerField(null=True,
                                     default=None,
                                     verbose_name='ID контакта в amoCRM')
    sms_notice = models.BooleanField(
        default=False, verbose_name='Получение оповещений по SMS')
    email_notice = models.BooleanField(
        default=False, verbose_name='Получение оповещений по email')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True,
                                   verbose_name='Дата последнего изменения')
    deleted = models.DateTimeField(default=None,
                                   null=True,
                                   verbose_name='Дата удаления')
    balance = MoneyField(default=0,
                         max_digits=14,
                         decimal_places=2,
                         default_currency='RUB',
                         verbose_name='Депозит')
    bonus_balance = MoneyField(default=0,
                               max_digits=14,
                               decimal_places=2,
                               default_currency='RUB',
                               verbose_name='Бонусный баланс')
    current_discount = models.DecimalField(max_digits=10,
                                           decimal_places=2,
                                           default=0,
                                           verbose_name='Текущая скидка')
    current_bonus_share = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Текущий процент бонуса')
    total_amount = MoneyField(default=0,
                              max_digits=14,
                              decimal_places=2,
                              default_currency='RUB',
                              verbose_name='Общая сумма собственных заказов')
    addresses = models.ManyToManyField(Address,
                                       through='UserAddress',
                                       related_name='user_addresses',
                                       verbose_name='Адреса пользователя')
    partner_type_id = models.IntegerField(choices=PARTNER_TYPES,
                                          verbose_name='Тип партнера',
                                          default=RETAIL)
    ref_id = models.PositiveIntegerField(unique=True,
                                         editable=False,
                                         verbose_name='Код партнера')
    total_sale_amount = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Общая сумма продаж реферралов')
    current_period_sale_amount = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма продаж реферралов за текущий период')
    last_period_sale_amount = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма продаж реферралов за предыдущий период')
    total_payments = MoneyField(default=0,
                                max_digits=14,
                                decimal_places=2,
                                default_currency='RUB',
                                verbose_name='Общая сумма пополнений депозита')
    current_period_payments = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма пополнений депозита за текущий период')
    last_period_payments = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма пополнений депозита за предыдущий период')
    total_bonus_payments = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Общая сумма пополнений бонусного баланса')
    current_period_bonus_payments = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма пополнений бонусного баланса за текущий период')
    last_period_bonus_payments = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Сумма пополнений бонусного баланса за предыдущий период')
    user_type = models.PositiveIntegerField(choices=USER_TYPES,
                                            default=NATIVE,
                                            verbose_name='Тип пользователя')
    avatar = models.ImageField(upload_to=avatar_path,
                               blank=True,
                               null=True,
                               default=None,
                               verbose_name='Аватар')
    current_target = MoneyField(
        default=0,
        max_digits=14,
        decimal_places=2,
        default_currency='RUB',
        verbose_name='Текущее значение целевого показателя')
    is_old = models.BooleanField(
        default=False,
        verbose_name='Признак пользователя со старого сайта')

    def get_next_seq_no(self):
        """
        Генератор порядковых номеров пользователей для использования в реферральной ссылке
        :return:
        """
        params = dict(app_label=self._meta.app_label,
                      model_name=self._meta.label_lower.split('.')[1],
                      min_val=0,
                      max_val=0,
                      step=1)
        new_id = get_next_id(params)
        return new_id

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.ref_id = self.get_next_seq_no()
        super(AppUser, self).save(*args, **kwargs)

    def get_ref_link(self):
        """
        Формирование реферральной ссылки
        :return:
        """
        return f'{settings.BASE_URL}ref/{self.ref_id}'

    def get_full_name(self):
        """
        Формирование полного имени пользователя
        :return:
        """
        return f'{isnull(self.last_name, "")} ' \
            f'{isnull(self.first_name, "")} ' \
            f'{isnull(self.patronymic, "")}'.strip()

    def jwt_update_secret_key(self):
        """
        Изменение секретного ключа пользователя (для функционала автологаута)
        :return:
        """
        self.jwt_secret = uuid.uuid4()
        self.save()

    def get_next_target_value(self):
        """
        Получение следующего целевого показателя для увеличения бонусной ставки
        """
        from shop.models import BonusParams  # pylint: disable=import-outside-toplevel
        b = BonusParams.objects.filter(      # pylint: disable=invalid-name
            started__lte=tz.now(),
            ended__gte=tz.now(),
            partner_type_id=self.partner_type_id,
            target__gt=self.current_target.amount).order_by('target').first()
        if b:
            next_target_value = b.target
        else:
            next_target_value = None
        return next_target_value

    def get_available_bonus_amount(self):
        """
        Получение суммы бонусов, доступных для расходования
        :return:
        """
        # в bonus_amount_plus - начисления бонусов с датой большей, чем now() - settings.BONUS_PERIOD
        bonus_amount_plus = BonusChangeHistory.objects.filter(
            user_id=self.id,
            amount__gte=0,
            created__lte=tz.now().date() -
            timedelta(days=settings.BONUS_PERIOD)).aggregate(Sum('amount'))
        # в bonus_amount_minus - списания бонусов за всю историю жизни пользователя
        bonus_amount_minus = BonusChangeHistory.objects.filter(
            user_id=self.id, amount__lt=0).aggregate(Sum('amount'))
        available_bonus_amount = isnull(
            bonus_amount_plus['amount__sum'], 0) + isnull(
                bonus_amount_minus['amount__sum'], 0)
        if available_bonus_amount < 0:
            return 0
        return available_bonus_amount

    def change_balance(self, bonus_amount, deposit_amount):
        """
        Изменение бонусного баланса и депозита
        :return:
        """
        self.bonus_balance.amount = self.bonus_balance.amount + bonus_amount
        self.balance.amount = self.balance.amount + deposit_amount
        self.save()

    def __str__(self):
        return '%s: %s %s %s' % (self.username or '', self.last_name or '',
                                 self.first_name or '', self.patronymic or '')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'appuser_user'


class UserAddress(BaseModel):
    """
    Связка пользователь <-> адрес
    """
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь')
    address = models.ForeignKey(Address,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Адрес')
    is_primary = models.BooleanField(default=False,
                                     verbose_name='Основной адрес')

    class Meta:
        verbose_name = 'Адрес пользователя'
        verbose_name_plural = 'Адреса пользователей'
        db_table = 'appuser_user_addresses'


class PhysProfile(BaseModel):
    """
    Профиль пользователя-физлица
    """
    RUSSIAN_PASSPORT = 0
    FOREIGN_PASSPORT = 1
    ANOTHER_DOC = 2

    DOC_TYPES = ((RUSSIAN_PASSPORT, 'Паспорт РФ'),
                 (FOREIGN_PASSPORT, 'Загранпаспорт'), (ANOTHER_DOC,
                                                       'Другой документ'))

    user = models.OneToOneField(AppUser,
                                on_delete=models.DO_NOTHING,
                                verbose_name='ID пользователя',
                                related_name='phys_profile')
    phone_number = models.CharField(max_length=20,
                                    blank=True,
                                    null=True,
                                    verbose_name='Номер телефона')
    birth_date = models.DateField(null=True,
                                  blank=True,
                                  verbose_name='Дата рождения')
    doc_type = models.IntegerField(choices=DOC_TYPES,
                                   blank=True,
                                   null=True,
                                   verbose_name='Тип документа')
    doc_number = models.CharField(max_length=64,
                                  blank=True,
                                  null=True,
                                  verbose_name='Серия/номер документа')
    doc_issue_date = models.DateField(blank=True,
                                      null=True,
                                      verbose_name='Дата выдачи документа')
    doc_authority = models.CharField(max_length=255,
                                     blank=True,
                                     null=True,
                                     verbose_name='Кем выдан документ')

    def __str__(self):
        return '%s: %s %s' % (self.user.username, self.first_name,
                              self.last_name)

    class Meta:
        verbose_name = 'Данные физического лица'
        verbose_name_plural = 'Данные физических лиц'
        db_table = 'appuser_phys_profile'


class JurProfile(BaseModel):
    """
    Профиль пользователя-юрлица
    """
    user = models.OneToOneField(AppUser,
                                on_delete=models.DO_NOTHING,
                                verbose_name='ID пользователя',
                                related_name='jur_profile')
    phone_number = models.CharField(max_length=20,
                                    blank=True,
                                    null=True,
                                    verbose_name='Номер телефона')
    inn = models.CharField(max_length=64,
                           blank=True,
                           null=True,
                           verbose_name='ИНН')
    org_name = models.CharField(max_length=255,
                                blank=True,
                                null=True,
                                verbose_name='Наименование организации')
    manager_name = models.CharField(max_length=255,
                                    blank=True,
                                    null=True,
                                    verbose_name='ФИО руководителя')
    agent_name = models.CharField(max_length=255,
                                  blank=True,
                                  null=True,
                                  verbose_name='ФИО доверенного лица')

    def __str__(self):
        return '%s: %s' % (self.inn, self.org_name)

    class Meta:
        verbose_name = 'Данные юридического лица'
        verbose_name_plural = 'Данные юридических лиц'
        db_table = 'appuser_jur_profile'


class Referral(BaseModel):
    """
    Связка реферрер <-> реферралы
    """
    referrer = models.ForeignKey(AppUser,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Пользователь',
                                 related_name='referrer')
    referral = models.OneToOneField(AppUser,
                                    on_delete=models.DO_NOTHING,
                                    verbose_name='Реферрал',
                                    related_name='referral')

    def __str__(self):
        return '%s: %s' % (self.referrer.username, self.referral.username)

    class Meta:
        verbose_name = 'Реферал'
        verbose_name_plural = 'Рефералы'
        db_table = 'appuser_referral'


class ReferrerOrder(models.Model):
    """
    Заказы реферралов
    """
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name='ID')
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Пользователь')
    created = models.DateTimeField(verbose_name='Дата создания заказа')
    payed = models.DateTimeField(verbose_name='Дата оплаты заказа')
    order_no = models.PositiveIntegerField(verbose_name='Номер заказа')
    total_amount = models.DecimalField(max_digits=14,
                                       decimal_places=2,
                                       verbose_name='Сумма заказа')
    bonus = models.DecimalField(max_digits=14,
                                decimal_places=2,
                                verbose_name='Сумма бонуса')
    referral = models.ForeignKey(AppUser,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Пользователь',
                                 related_name='order_referral')

    class Meta:
        db_table = 'view_referrer_orders'
        managed = False
        verbose_name = 'Реферральный заказ пользователя'
        verbose_name_plural = 'Реферральные заказы пользователя'


class BonusChangeHistory(BaseModel):
    """
    История пополнений и списаний бонусных балансов для получения суммы бонусов, доступных для трат
    Списания с ББ - в триггере appuser_before_update()
    Начсиления на ББ - в триггере order_before_update, процедура increase_bonus_balance
    """
    user = models.ForeignKey(AppUser,
                             verbose_name='Пользователь',
                             on_delete=models.DO_NOTHING)
    amount = MoneyField(default=0,
                        max_digits=14,
                        decimal_places=2,
                        default_currency='RUB',
                        verbose_name='Сумма пополнения')

    class Meta:
        verbose_name = 'Пополнение/списание бонусного баланса'
        verbose_name_plural = 'Пополнения/списания бонусного баланса'
        db_table = 'appuser_bonus_change_history'


class PasswordResetReqeust(BaseModel):
    """
    Запросы на сброс пароля
    """
    user = models.ForeignKey(AppUser,
                             verbose_name='Пользователь',
                             on_delete=models.DO_NOTHING)
    processed = models.NullBooleanField(
        default=None, verbose_name='Признак обработки заявки на сброс пароля')

    class Meta:
        verbose_name = 'Запрос на сброс пароля'
        verbose_name_plural = 'Запросы на сброс пароля'
        db_table = 'appuser_password_reset_request'


class Bonus1CChangeHistory(BaseModel):
    """
        История иземнений бонусных балансов, инициируемых 1С
    """
    user = models.ForeignKey(AppUser,
                             on_delete=models.DO_NOTHING,
                             related_name='bb_changes_1c')
    bonus_amount = MoneyField(default=0,
                              max_digits=14,
                              decimal_places=2,
                              default_currency='RUB',
                              verbose_name='Изменение ББ')

    class Meta:
        db_table = 'appuser_1c_bb_history'


class OldUser(models.Model):
    """Пользователи старого сайта для заведения, начисления кэшбека и SMS-рассылки"""
    phone = models.CharField(max_length=50, verbose_name='Телефон')
    fio = models.CharField(max_length=255, verbose_name='ФИО')
    cashback = models.DecimalField(max_digits=10,
                                   decimal_places=2,
                                   verbose_name='Кэшбек')

    class Meta:
        db_table = 'view_old_users'
        managed = False


class OldUserLog(models.Model):
    """Лог отправок SMS пользователям старого сайта"""
    old_user = models.OneToOneField(AppUser, on_delete=models.DO_NOTHING)
    is_sms_sent = models.BooleanField(default=False, verbose_name='Признак отправки SMS')
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'appuser_old_user_log'
