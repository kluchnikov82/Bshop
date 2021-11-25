# Generated by Django 2.1.7 on 2020-05-30 06:55

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import re
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackAll',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')),
                ('deleted', models.DateTimeField(default=None, null=True, verbose_name='Дата удаления')),
                ('text', models.TextField(blank=True, default='', max_length=8000, null=True, verbose_name='Текст отзыва')),
                ('approved', models.BooleanField(default=False, verbose_name='Отображать на сайте')),
                ('video_link', models.CharField(blank=True, default=None, max_length=1000, null=True, verbose_name='Ссылка на обзор Youtube')),
                ('with_text', models.BooleanField(default=True, verbose_name='С текстом до/после')),
                ('order_no', models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Порядковый номер')),
                ('image', models.ImageField(blank=True, upload_to='', verbose_name='Изображение отзыва')),
                ('rating', models.PositiveIntegerField(verbose_name='Рейтинг')),
                ('show_on_main_page', models.BooleanField(verbose_name='Признак отображения отзыва на главной')),
            ],
            options={
                'db_table': 'view_feedbacks',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DefaultDeliveryPrice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')),
                ('deleted', models.DateTimeField(default=None, null=True, verbose_name='Дата удаления')),
                ('delivery_type', models.IntegerField(choices=[(0, 'Почта России'), (1, 'EMS по России'), (4, 'EMS международная доставка'), (3, 'Пункт самовывоза СДЭК'), (2, 'СДЭК курьер'), (5, 'СДЭК международная доставка до двери'), (8, 'Курьером по Оренбургу'), (9, 'СДЭК международная доставка до ПВЗ')], unique=True, verbose_name='Способ доставки')),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('XUA', 'ADB Unit of Account'), ('AFN', 'Afghani'), ('DZD', 'Algerian Dinar'), ('ARS', 'Argentine Peso'), ('AMD', 'Armenian Dram'), ('AWG', 'Aruban Guilder'), ('AUD', 'Australian Dollar'), ('AZN', 'Azerbaijanian Manat'), ('BSD', 'Bahamian Dollar'), ('BHD', 'Bahraini Dinar'), ('THB', 'Baht'), ('PAB', 'Balboa'), ('BBD', 'Barbados Dollar'), ('BYN', 'Belarussian Ruble'), ('BYR', 'Belarussian Ruble'), ('BZD', 'Belize Dollar'), ('BMD', 'Bermudian Dollar (customarily known as Bermuda Dollar)'), ('BTN', 'Bhutanese ngultrum'), ('VEF', 'Bolivar Fuerte'), ('BOB', 'Boliviano'), ('XBA', 'Bond Markets Units European Composite Unit (EURCO)'), ('BRL', 'Brazilian Real'), ('BND', 'Brunei Dollar'), ('BGN', 'Bulgarian Lev'), ('BIF', 'Burundi Franc'), ('XOF', 'CFA Franc BCEAO'), ('XAF', 'CFA franc BEAC'), ('XPF', 'CFP Franc'), ('CAD', 'Canadian Dollar'), ('CVE', 'Cape Verde Escudo'), ('KYD', 'Cayman Islands Dollar'), ('CLP', 'Chilean peso'), ('XTS', 'Codes specifically reserved for testing purposes'), ('COP', 'Colombian peso'), ('KMF', 'Comoro Franc'), ('CDF', 'Congolese franc'), ('BAM', 'Convertible Marks'), ('NIO', 'Cordoba Oro'), ('CRC', 'Costa Rican Colon'), ('HRK', 'Croatian Kuna'), ('CUP', 'Cuban Peso'), ('CUC', 'Cuban convertible peso'), ('CZK', 'Czech Koruna'), ('GMD', 'Dalasi'), ('DKK', 'Danish Krone'), ('MKD', 'Denar'), ('DJF', 'Djibouti Franc'), ('STD', 'Dobra'), ('DOP', 'Dominican Peso'), ('VND', 'Dong'), ('XCD', 'East Caribbean Dollar'), ('EGP', 'Egyptian Pound'), ('SVC', 'El Salvador Colon'), ('ETB', 'Ethiopian Birr'), ('EUR', 'Euro'), ('XBB', 'European Monetary Unit (E.M.U.-6)'), ('XBD', 'European Unit of Account 17(E.U.A.-17)'), ('XBC', 'European Unit of Account 9(E.U.A.-9)'), ('FKP', 'Falkland Islands Pound'), ('FJD', 'Fiji Dollar'), ('HUF', 'Forint'), ('GHS', 'Ghana Cedi'), ('GIP', 'Gibraltar Pound'), ('XAU', 'Gold'), ('XFO', 'Gold-Franc'), ('PYG', 'Guarani'), ('GNF', 'Guinea Franc'), ('GYD', 'Guyana Dollar'), ('HTG', 'Haitian gourde'), ('HKD', 'Hong Kong Dollar'), ('UAH', 'Hryvnia'), ('ISK', 'Iceland Krona'), ('INR', 'Indian Rupee'), ('IRR', 'Iranian Rial'), ('IQD', 'Iraqi Dinar'), ('IMP', 'Isle of Man Pound'), ('JMD', 'Jamaican Dollar'), ('JOD', 'Jordanian Dinar'), ('KES', 'Kenyan Shilling'), ('PGK', 'Kina'), ('LAK', 'Kip'), ('KWD', 'Kuwaiti Dinar'), ('AOA', 'Kwanza'), ('MMK', 'Kyat'), ('GEL', 'Lari'), ('LVL', 'Latvian Lats'), ('LBP', 'Lebanese Pound'), ('ALL', 'Lek'), ('HNL', 'Lempira'), ('SLL', 'Leone'), ('LSL', 'Lesotho loti'), ('LRD', 'Liberian Dollar'), ('LYD', 'Libyan Dinar'), ('SZL', 'Lilangeni'), ('LTL', 'Lithuanian Litas'), ('MGA', 'Malagasy Ariary'), ('MWK', 'Malawian Kwacha'), ('MYR', 'Malaysian Ringgit'), ('TMM', 'Manat'), ('MUR', 'Mauritius Rupee'), ('MZN', 'Metical'), ('MXV', 'Mexican Unidad de Inversion (UDI)'), ('MXN', 'Mexican peso'), ('MDL', 'Moldovan Leu'), ('MAD', 'Moroccan Dirham'), ('BOV', 'Mvdol'), ('NGN', 'Naira'), ('ERN', 'Nakfa'), ('NAD', 'Namibian Dollar'), ('NPR', 'Nepalese Rupee'), ('ANG', 'Netherlands Antillian Guilder'), ('ILS', 'New Israeli Sheqel'), ('RON', 'New Leu'), ('TWD', 'New Taiwan Dollar'), ('NZD', 'New Zealand Dollar'), ('KPW', 'North Korean Won'), ('NOK', 'Norwegian Krone'), ('PEN', 'Nuevo Sol'), ('MRO', 'Ouguiya'), ('TOP', 'Paanga'), ('PKR', 'Pakistan Rupee'), ('XPD', 'Palladium'), ('MOP', 'Pataca'), ('PHP', 'Philippine Peso'), ('XPT', 'Platinum'), ('GBP', 'Pound Sterling'), ('BWP', 'Pula'), ('QAR', 'Qatari Rial'), ('GTQ', 'Quetzal'), ('ZAR', 'Rand'), ('OMR', 'Rial Omani'), ('KHR', 'Riel'), ('MVR', 'Rufiyaa'), ('IDR', 'Rupiah'), ('RUB', 'Russian Ruble'), ('RUR', 'Russian Ruble'), ('RWF', 'Rwanda Franc'), ('XDR', 'SDR'), ('SHP', 'Saint Helena Pound'), ('SAR', 'Saudi Riyal'), ('RSD', 'Serbian Dinar'), ('SCR', 'Seychelles Rupee'), ('XAG', 'Silver'), ('SGD', 'Singapore Dollar'), ('SBD', 'Solomon Islands Dollar'), ('KGS', 'Som'), ('SOS', 'Somali Shilling'), ('TJS', 'Somoni'), ('SSP', 'South Sudanese Pound'), ('LKR', 'Sri Lanka Rupee'), ('XSU', 'Sucre'), ('SDG', 'Sudanese Pound'), ('SRD', 'Surinam Dollar'), ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('SYP', 'Syrian Pound'), ('BDT', 'Taka'), ('WST', 'Tala'), ('TZS', 'Tanzanian Shilling'), ('KZT', 'Tenge'), ('XXX', 'The codes assigned for transactions where no currency is involved'), ('TTD', 'Trinidad and Tobago Dollar'), ('MNT', 'Tugrik'), ('TND', 'Tunisian Dinar'), ('TRY', 'Turkish Lira'), ('TMT', 'Turkmenistan New Manat'), ('TVD', 'Tuvalu dollar'), ('AED', 'UAE Dirham'), ('XFU', 'UIC-Franc'), ('USD', 'US Dollar'), ('USN', 'US Dollar (Next day)'), ('UGX', 'Uganda Shilling'), ('CLF', 'Unidad de Fomento'), ('COU', 'Unidad de Valor Real'), ('UYI', 'Uruguay Peso en Unidades Indexadas (URUIURUI)'), ('UYU', 'Uruguayan peso'), ('UZS', 'Uzbekistan Sum'), ('VUV', 'Vatu'), ('CHE', 'WIR Euro'), ('CHW', 'WIR Franc'), ('KRW', 'Won'), ('YER', 'Yemeni Rial'), ('JPY', 'Yen'), ('CNY', 'Yuan Renminbi'), ('ZMK', 'Zambian Kwacha'), ('ZMW', 'Zambian Kwacha'), ('ZWD', 'Zimbabwe Dollar A/06'), ('ZWN', 'Zimbabwe dollar A/08'), ('ZWL', 'Zimbabwe dollar A/09'), ('PLN', 'Zloty')], default='RUB', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('200'), default_currency='RUB', max_digits=14, verbose_name='Стоимость доставки')),
            ],
            options={
                'verbose_name': 'Стоимость способа доставки по умолчанию',
                'verbose_name_plural': 'Стоимости способов доставки по умолчанию',
                'db_table': 'shop_delivery_price',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='code',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Артикул'),
        ),
        migrations.AddField(
            model_name='kitfeedback',
            name='order_no',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Порядковый номер'),
        ),
        migrations.AddField(
            model_name='kitfeedback',
            name='rating',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Рейтинг Программы'),
        ),
        migrations.AddField(
            model_name='productfeedback',
            name='order_no',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Порядковый номер'),
        ),
        migrations.AlterField(
            model_name='activecomponent',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='kit',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='kitfeedback',
            name='text',
            field=models.TextField(blank=True, default='', max_length=8000, null=True, verbose_name='Текст отзыва'),
        ),
        migrations.AlterField(
            model_name='kitfeedback',
            name='user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='kitfeedback',
            name='with_text',
            field=models.BooleanField(default=True, verbose_name='С текстом до/после'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_method_id',
            field=models.IntegerField(choices=[(0, 'Почта России'), (1, 'EMS по России'), (4, 'EMS международная доставка'), (6, 'Мелкий пакет МН'), (3, 'Пункт самовывоза СДЭК'), (2, 'СДЭК курьер'), (5, 'СДЭК международная доставка до двери'), (7, 'Самовывоз (ТК Успех, ул. Ленинская 39)'), (8, 'Курьером по Оренбургу'), (9, 'СДЭК международная доставка до ПВЗ')], default=0, verbose_name='Cпособ доставки'),
        ),
        migrations.AlterField(
            model_name='product',
            name='linked_products',
            field=models.ManyToManyField(blank=True, through='shop.LinkedProduct', to='shop.Product', verbose_name='Товары, приобретаемые вместе'),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='productfeedback',
            name='rating',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Рейтинг товара'),
        ),
        migrations.AlterField(
            model_name='productfeedback',
            name='text',
            field=models.TextField(blank=True, default='', max_length=8000, null=True, verbose_name='Текст отзыва'),
        ),
        migrations.AlterField(
            model_name='productfeedback',
            name='user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='productfeedback',
            name='with_text',
            field=models.BooleanField(default=True, verbose_name='С текстом до/после'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
    ]
