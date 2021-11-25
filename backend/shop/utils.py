"""
Shop utils
"""
import copy
import uuid
import logging
from decimal import Decimal

from django.conf import settings

from core.utils import get_decimal

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


def calc_totals(order_products, order_kits, order_events):
    """
    Расчет общего веса, объема и стоимости набора товаров и программ
    :param order_products: массив товаров
                           [
        {
            "product_id": "88e0583b-e0d1-41b8-8b2b-6528f4a761cf",
            "quantity": 2,
            "price": 33,
            "amount": 66
        },
        {
            "product_id": "8c25aea8-d1c9-4c49-ad3e-f66a559aa163",
            "quantity": 1,
            "price": 470,
            "amount": 470
        }
    ]
    :param order_kits: массив программ
                            [
        {
            "kit_id": "92e0da3d-e993-4599-8b4d-d5732438e85c",
            "quantity": 1,
            "price": 500,
            "amount": 500
        }
    ]
    :param order_events: массив акций
                            [
        {
            "event_id": "8fef59c9-f76c-4190-b618-03922802b3e4",
            "order_event_products": [
                {
                    "product_id": "a841005e-0524-4505-a67c-cd24694d3ea5",
                    "is_gift": true,
                    "quantity": 3,
                    "price": 0,
                    "amount": 0
                },
                {
                    "product_id": "0c333082-3875-4744-aee2-4aff66803ad5",
                    "is_gift": false,
                    "quantity": 1,
                    "price": 595,
                    "amount": 595
                },
                {
                    "product_id": "45a7f77b-8eb3-474b-b087-3b05e22376d4",
                    "is_gift": false,
                    "quantity": 1,
                    "price": 1690,
                    "amount": 1690
                }
            ]
        }
    ]
    :return: вес, г; объем, см3; общая стоимость, руб
    """
    # TODO: рефакторинг [import-outside-toplevel]
    from .models import Product, Kit

    def to_uuid(x):  # pylint: disable=invalid-name
        """
        Convert object to uuid
        """
        if isinstance(x, str):
            return uuid.UUID(x)
        return x

    total_weight = int(0)
    total_volume = float(0)
    total_amount = Decimal('0')

    prod_ids = [p['product_id'] for p in order_products]
    kit_ids = [p['kit_id'] for p in order_kits]

    order_event_products = []
    if order_events and isinstance(order_events, list):
        for e in order_events:                   # pylint: disable=invalid-name
            for p in e['order_event_products']:  # pylint: disable=invalid-name
                prod_ids.append(p['product_id'])
                appended_product = copy.copy(p)
                appended_product['quantity'] = appended_product['quantity'] * e.get('quantity', 1)
                order_event_products.append(appended_product)

    order_products.extend(order_event_products)
    prods = dict()
    kits = dict()

    for p in Product.objects.filter(id__in=prod_ids,  # pylint: disable=invalid-name
                                    deleted__isnull=True).values(
                                        'id', 'gross_weight', 'packing_volume'):
        prods[p['id']] = (p['gross_weight'], p['packing_volume'])

    for k in Kit.objects.filter(id__in=kit_ids, deleted__isnull=True).values(  # pylint: disable=invalid-name
            'id', 'gross_weight', 'packing_volume'):
        kits[k['id']] = (k['gross_weight'], k['packing_volume'])

    for op in order_products:  # pylint: disable=invalid-name
        product = prods.get(to_uuid(op['product_id']))
        if product:
            total_weight += product[0] * op['quantity']
            total_volume += product[1] * op['quantity']
            total_amount += get_decimal(op['price'] * op['quantity'])

    for k in order_kits:  # pylint: disable=invalid-name
        kit = kits.get(to_uuid(k['kit_id']))
        if kit:
            total_weight += kit[0] * k['quantity']
            total_volume += kit[1] * k['quantity']
            total_amount += get_decimal(k['price'] * k['quantity'])
    return total_weight, total_volume, total_amount


def get_shipping_method_params(shipping_method_id):
    """
    Получение параметров способов доставки СДЭК и Почты России по Order.shipment_method_id
    :param shipping_method_id: id способа доставки модели Order
    :return: для СДЭК: наименование способа доставки, tarif_id - id тарифа СДЭК,
    mode_id - метод доставки (курьер, ПВЗ); для Почты России: наименование способа доставки,
    кодовое обозначение способа, признак курьерской доставки
    """
    params = []
    name = None
    param2 = None
    param3 = None
    ship_type = None
    if shipping_method_id in [i[0] for i in settings.CDEK_SHIPPING_METHODS]:
        params = [
            i for i in settings.CDEK_SHIPPING_METHODS
            if i[0] == shipping_method_id
        ][0]
        ship_type = 'cdek'
    elif shipping_method_id in [i[0] for i in settings.RP_SHIPPING_METHODS]:
        params = [
            i for i in settings.RP_SHIPPING_METHODS
            if i[0] == shipping_method_id
        ][0]
        ship_type = 'rp'
    if len(params) >= 4:
        name = params[1]
        param2 = params[2]
        param3 = params[3]
    return name, ship_type, param2, param3


def get_user_ref_id_from_promo(code):
    """
    Получение ID пользователя из промокода
    :param code: промокод
    :return:
    """
    user_id = None
    if code is not None and isinstance(code, str):
        ref_prefix = settings.REF_PROMO_PREFIX
        ref_prefix_len = len(ref_prefix)
        if code[0:ref_prefix_len] == ref_prefix:
            try:
                user_id = int(''.join([s for s in code if s.isdigit()]))
            except ValueError:
                pass
    return user_id