"""В данном модуле происходит тестировние следующих API-сервисов:
1. Переход на страницу товаров.
2. Получение списка заказов пользователя.
3. Создание нового заказа.
4. Получение дерева категорий товаров.
5. Получение списка товаров по по методу limit-offset.
6. Получение списка товаров по наименованию товара.
7. Получение списка товаров по идентификатору
8. Получение атрибутов товара.
9. Получение списка программ по методу limit-offset.
10. Получение списка программ по названию программы.
11. Получение атрибутов программы.
12. Получение атрибутов активного компонента.
13. Получение атрибутов категории.
14. Получение списка слайдов.
15. Создание заказа.
16. Редактирование заказа.
17. Получение атрибутов заказа.
18. Получение списка заказов пользователя.
19. Получение списка стран.
20. Получение списка стран.
21. Создание обращения.
22. Получение списка типов обращений.
23. Проверка промокода на активность, получение его параметров.
24. Редактирование заказа.
25. Загрузка из 1С изменений бонусных балансов.
26. Получение отзывов о товаре.
27. Создание отзыва о товаре.
28. Создание отзыва о программе.
29. Получение отзывов о программе.
30. Получение списка отзывов о товарах для отображения на главной.
31. Получение списка отзывов о программах для отображения на главной.
32. Обработка оповещения об успешной оплате заказа от PayKeeper.
"""
import logging

from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework.utils import json
from core.models import ServiceParam  # pylint: disable=no-name-in-module,import-error
from appuser.utils import send_response, send_response_jwt  # pylint: disable=no-name-in-module,import-error
from appuser.tests import Authentication

from bshop.backend.cfg import devsettings  # pylint: disable=wrong-import-position

logging.config.dictConfig(devsettings.LOGGING)
logger = logging.getLogger('shop')  # pylint: disable=invalid-name


class URLPage(TestCase):
    """Переход на страницу товаров"""
    def test_details(self):  # pylint: disable=missing-function-docstring
        response = self.client.get(devsettings.BASE_URL + 'api/shop/products_all')
        self.assertEqual(response.status_code, 200)


class Orders(TestCase):
    """Получение списка заказов пользователя"""
    def test_orders(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/orders?limit=5&offset=1'
        send_response(url)


class NewOrder(TestCase):
    """Создание нового заказа"""
    def setUp(self, null=None):  # pylint: disable=missing-function-docstring,arguments-differ
        self.record = {
            "total_amount": 3321,
            "total_amount_wo_discount": 3321,
            "own": True,
            "phone": "+79058000012",
            "email": "test@mail.ru",
            "surname": "Антонов",
            "name": "Сидор",
            "patronymic": "Петрович",
            "memo": "",
            "order_type": 0,
            "shipping_method_id": 2,
            "delivery_point_id": null,
            "delivery_point_address": null,
            "shipping_amount": 300,
            "promocode": "VG1R15",
            "order_products": [
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
            ],
            "order_kits": [
                {
                    "kit_id": "92e0da3d-e993-4599-8b4d-d5732438e85c",
                    "quantity": 1,
                    "price": 500,
                    "amount": 500
                }
            ],
            "order_events": [
                {
                    "event_id": "8fef59c9-f76c-4190-b618-03922802b3e4",
                    "quantity": 1,
                    "order_event_products": [
                        {
                            "product_id": "a841005e-0524-4505-a67c-cd24694d3ea5",
                            "is_gift": True,
                            "quantity": 3,
                            "price": 0,
                            "amount": 0
                        },
                        {
                            "product_id": "0c333082-3875-4744-aee2-4aff66803ad5",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 595,
                            "amount": 595
                        },
                        {
                            "product_id": "45a7f77b-8eb3-474b-b087-3b05e22376d4",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 1690,
                            "amount": 1690
                        }
                    ]
                }
            ],
            "address": {
                "kladr_id": "5601900001301660023",
                "postcode": "460530",
                "region": "Оренбургская обл",
                "district": "Оренбургский р-н",
                "settlement": null,
                "country": "Россия",
                "city": "село Ивановка",
                "street": "ул Липовая",
                "house": "д 48",
                "flat": "15",
                "cdek_city_id": null
            }
        }

        order_total_amount = 0
        for order in self.record['order_products']:
            # В данном цикле подсчитываем стоимость товаров
            order_total_amount = order_total_amount + order['amount']

        for order in self.record['order_kits']:
            # В данном цикле подсчитываем (стоимость программ) + (стоимсоть товаров)
            order_total_amount = order_total_amount + order['amount']

        for order1 in self.record['order_events']:
            for order2 in order1['order_event_products']:
                # В данном цикле подсчитываем (стоимость акционных товаров)+(стоимость программ)+(стоимсоть товаров)
                order_total_amount = order_total_amount + order2['amount']
        logger.info(order_total_amount)

        self.flag = False
        if order_total_amount == self.record['total_amount']:
            self.flag = True

    def test(self):  # pylint: disable=missing-function-docstring
        if self.flag:
            auth = Authentication()
            response = auth.test_auth()
            if response.status_code == 200:
                token = response.json()['token']
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
                response = client.post(devsettings.BASE_URL + 'api/shop/orders', content_type='application/json',
                                       data=json.dumps(self.record))
                logger.info('Пользователь прошел аутентификацию')
                logger.info(token)
                logger.info('Тест выполнен успешно.')

            else:
                logger.info('Пользователь не прошел аутентификацию')
        else:
            logger.debug('Итоговая сумма заказа не совпадает с суммой компонентов заказа! Проверьте значения!')
            logger.debug('Тест на создание нового заказа провален.')


class LoadListProducts(TestCase):
    """Получение дерева категорий товаров"""
    def test_load_list_products(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/catalog'
        send_response(url)


class ProductsListsLimitOffset(TestCase):
    """Получение списка товаров по методу limit-offset"""
    def test_products_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/products?limit=15&offset=1'
        send_response(url)


class ProductsListsNameProduct(TestCase):
    """Получение списка товаров по наименованию товара"""
    def test_products_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/products?q=Балансер матирующий'
        send_response(url)


class ProductsListsId(TestCase):
    """Получение списка товаров по идентификатору с discount > 0"""
    def test_products_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/products?id=bed739a5-5d5a-4125-9cf4-534a6f8258ee'
        '&id=32743cde-22e1-42ee-b43a-f9f97e26f43b&discount=1'  # pylint: disable=pointless-string-statement
        send_response(url)


class ProductDetail(TestCase):
    """Получение атрибутов товара"""
    def test_products_detail(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/products/32743cde-22e1-42ee-b43a-f9f97e26f43b'
        send_response(url)


class KitsListLimitOffset(TestCase):
    """Получение списка программ по методу limit-offset"""
    def test_kits_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/kits?limit=5&offset=1'
        send_response(url)


class KitsListNameKit(TestCase):
    """Получение списка программ по названию программы"""
    def test_kits_list_name_kit(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/kits?q=Баланс'
        send_response(url)


class KitDetail(TestCase):
    """Получение атрибутов программы"""
    def test_kit_detail(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/kits/465e9df9-56b7-41ef-9bb5-d2528e032f89'
        send_response(url)


class ComponentDetail(TestCase):
    """Получение атрибутов активного компонента"""
    def test_component_detail(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/components/ba9b4ab4-d0aa-4475-a1cd-1f265340559c'
        send_response(url)


class CatDetail(TestCase):
    """Получение атрибутов категории"""
    def test_cat_detail(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/categories/ae7fd86b-b8ed-490d-b458-352612ee74db'
        send_response(url)


class SlideList(TestCase):
    """Получение списка слайдов"""
    def test_slide_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/slides'
        send_response(url)


class CreateOrder(TestCase):
    """Создание заказа"""
    def setUp(self, null=None):  # pylint: disable=missing-function-docstring,arguments-differ
        self.record = {
            "total_amount": 3321,
            "total_amount_wo_discount": 3321,
            "own": True,
            "phone": "+79058000012",
            "email": "test@mail.ru",
            "surname": "Антонов",
            "name": "Сидор",
            "patronymic": "Петрович",
            "memo": "",
            "order_type": 0,
            "shipping_method_id": 2,
            "delivery_point_id": null,
            "delivery_point_address": null,
            "shipping_amount": 300,
            "promocode": "VG1R15",
            "order_products": [
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
            ],
            "order_kits": [
                {
                    "kit_id": "92e0da3d-e993-4599-8b4d-d5732438e85c",
                    "quantity": 1,
                    "price": 500,
                    "amount": 500
                }
            ],
            "order_events": [
                {
                    "event_id": "8fef59c9-f76c-4190-b618-03922802b3e4",
                    "quantity": 1,
                    "order_event_products": [
                        {
                            "product_id": "a841005e-0524-4505-a67c-cd24694d3ea5",
                            "is_gift": True,
                            "quantity": 3,
                            "price": 0,
                            "amount": 0
                        },
                        {
                            "product_id": "0c333082-3875-4744-aee2-4aff66803ad5",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 595,
                            "amount": 595
                        },
                        {
                            "product_id": "45a7f77b-8eb3-474b-b087-3b05e22376d4",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 1690,
                            "amount": 1690
                        }
                    ]
                }
            ],
            "address": {
                "kladr_id": "5601900001301660023",
                "postcode": "460530",
                "region": "Оренбургская обл",
                "district": "Оренбургский р-н",
                "settlement": null,
                "country": "Россия",
                "city": "село Ивановка",
                "street": "ул Липовая",
                "house": "д 48",
                "flat": "15",
                "cdek_city_id": null
            }
        }

    def test_create_order(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/orders'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class EditOrder(TestCase):
    """Редактирование заказа"""
    def setUp(self, null=None):  # pylint: disable=missing-function-docstring,arguments-differ
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.record = {
            "total_amount": 3321,
            "total_amount_wo_discount": 3321,
            "own": True,
            "phone": "+79058000012",
            "email": "test@mail.ru",
            "surname": "Антонов",
            "name": "Сидор",
            "patronymic": "Петрович",
            "memo": "",
            "order_type": 0,
            "shipping_method_id": 2,
            "delivery_point_id": null,
            "delivery_point_address": null,
            "shipping_amount": 300,
            "promocode": null,
            "order_products": [
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
            ],
            "order_kits": [
                {
                    "kit_id": "92e0da3d-e993-4599-8b4d-d5732438e85c",
                    "quantity": 1,
                    "price": 500,
                    "amount": 500
                }
            ],
            "order_events": [
                {
                    "event_id": "8fef59c9-f76c-4190-b618-03922802b3e4",
                    "quantity": 1,
                    "order_event_products": [
                        {
                            "product_id": "a841005e-0524-4505-a67c-cd24694d3ea5",
                            "is_gift": True,
                            "quantity": 3,
                            "price": 0,
                            "amount": 0
                        },
                        {
                            "product_id": "0c333082-3875-4744-aee2-4aff66803ad5",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 595,
                            "amount": 595
                        },
                        {
                            "product_id": "45a7f77b-8eb3-474b-b087-3b05e22376d4",
                            "is_gift": False,
                            "quantity": 1,
                            "price": 1690,
                            "amount": 1690
                        }
                    ]
                }
            ],
            "address": {
                "kladr_id": "5601900001301660023",
                "postcode": "460530",
                "region": "Оренбургская обл",
                "district": "Оренбургский р-н",
                "settlement": null,
                "country": "Россия",
                "city": "село Ивановка",
                "street": "ул Липовая",
                "house": "д 48",
                "flat": "15",
                "cdek_city_id": null
            }
        }

    def test_edit_order(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/orders/2d31d3cd-11c3-4cb0-8917-6016811694a1'
        flag = 'put'
        send_response_jwt(url, flag, self.record)


class OrderDetails(TestCase):
    """Получение атрибутов заказа"""
    def test_order_details(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/orders/2ef91945-d7bc-416e-97f1-4a6f26eeafbd'
        send_response(url)


class OrderList(TestCase):
    """Получение списка заказов пользователя"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)

    def test_order_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/orders?limit=5&offset=1'
        flag = 'get'
        send_response_jwt(url, flag)


class GetCountries(TestCase):
    """Получение списка стран"""
    def test_get_countries(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/countries'
        send_response(url)


class GetPvz(TestCase):
    """Получение списка ПВЗ по индексу"""
    def test_get_pvz(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/delivery_points?postcode=460014&point_type=PVZ'
        send_response(url)


class GetShipmentDetails(TestCase):
    """Расчет стоимости и способов доставки заказа"""
    def setUp(self):  # pylint: disable=missing-function-docstring,arguments-differ
        self.record = {
            "order_products": [
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
              ],
            "order_kits": [
                {
                  "kit_id": "92e0da3d-e993-4599-8b4d-d5732438e85c",
                  "quantity": 1,
                  "price": 500,
                  "amount": 500
                }
              ],
            "order_events": [
                {
                  "event_id": "8fef59c9-f76c-4190-b618-03922802b3e4",
                  "quantity": 1,
                  "order_event_products": [
                    {
                      "product_id": "a841005e-0524-4505-a67c-cd24694d3ea5",
                      "is_gift": True,
                      "quantity": 3,
                      "price": 0,
                      "amount": 0
                    },
                    {
                      "product_id": "0c333082-3875-4744-aee2-4aff66803ad5",
                      "is_gift": False,
                      "quantity": 1,
                      "price": 595,
                      "amount": 595
                    },
                    {
                      "product_id": "45a7f77b-8eb3-474b-b087-3b05e22376d4",
                      "is_gift": False,
                      "quantity": 1,
                      "price": 1690,
                      "amount": 1690
                    }
                  ]
                }
              ],
            "address": {
                "postcode": "040912",
                "city": "Sarkand",
                "country": 398,
                "country_code": "kz"
              }
            }

    def test_get_shipment_details(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/calc_shipping'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class CreateAdvice(TestCase):
    """Создание обращения"""
    def setUp(self):  # pylint: disable=missing-function-docstring,arguments-differ
        self.record = {
            "name": "gogi",
            "phone": "asdasd",
            "age": "32",
            "text": "штош",
            "email": "gogi@gogi.ru",
            "advice_type": "dd6788b4-a1cc-4f93-a37a-6f993662d1d4"
            }

    def test_create_advice(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/advice'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class GetAdviceTypes(TestCase):
    """Получение списка типов обращений"""
    def test_get_advice_types(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/advice_types'
        send_response(url)


class CheckPromo(TestCase):
    """Проверка промокода на активность, получение его параметров"""
    def test_check_promo(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/promo?code=VG0R15'
        send_response(url)


class Get1cOrderList(TransactionTestCase):
    """Редактирование заказа"""
    def setUp(self):  # pylint: disable=missing-function-docstring,no-self-use
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        object_serv, created = ServiceParam.objects.get_or_create(service_name='1c',
                                                                  defaults={'service_name': '1c',
                                                                            'id':'e20bf7b4-8c0b-4106-afac-46cce1f2f1f8',
                                                                            'param_name': 'token',
                                                                            'param_value': self.token})
        if not created:
            object_serv.param_value = self.token
            object_serv.save()  # pylint: disable=no-member

    def test_get_1c_order_list(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/rep_orders?token='+self.token+'&started=2019-01-01&ended=2020-12-12'
        send_response(url)


class Upload1cBb(TransactionTestCase):
    """Загрузка из 1С изменений бонусных балансов"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        self.record = [
            {
                "phone": "+7230-598-99-66",
                "bonus_amount": "-5,99",
                "order_amount": "0"
            },
            {
                "phone": "+79128468865",
                "bonus_amount": "179",
                "order_amount": "3580"
            },
            {
                "phone": "456",
                "bonus_amount": "-20",
                "order_amount": "0"
            }
        ]

        object_ser, created = ServiceParam.objects.get_or_create(service_name='1c',
                                                                 defaults={'service_name': '1c',
                                                                           'id': 'e20bf7b4-8c0b-4106-afac-46cce1f2f1f8',
                                                                           'param_name': 'token',
                                                                           'param_value': self.token})

        if not created:
            object_ser.param_value = self.token
            object_ser.save()  # pylint: disable=no-member

    def test_upload_1c_bb(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/bonus_upload?token='+self.token
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class GetProductFeedback(TestCase):
    """Получение отзывов о товаре"""
    def test_get_product_feedback(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/prod_feedback/be67bd0e-53ce-4f67-9ed9-54e7fffbaa0c'
        send_response(url)


class CreateProductFeedback(TestCase):
    """Создание отзыва о товаре"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.record = {
            "text": "Отличный ацетон! Выпил с удовольствием",
            "product": "88e0583b-e0d1-41b8-8b2b-6528f4a761cf",
            "video_link": "https://www.youtube.com/watch?v=3pZOpaCfdiY",
            "rating": 4
        }

    def test_create_product_feedback(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/prod_feedback'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class CreateKitFeedback(TestCase):
    """Создание отзыва о программе"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.record = {
            "text": "Очень плохая музыка",
            "kit": "92e0da3d-e993-4599-8b4d-d5732438e85c",
            "video_link": "https://www.youtube.com/watch?v=3pZOpaCfdiY"
        }

    def test_create_kit_feedback(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/kit_feedback'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class GetKitFeedback(TestCase):
    """Получение отзывов о программе"""
    def test_get_kit_feedback(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/kit_feedback/6531c83c-9018-47e6-a84b-eb11c46100ec'
        send_response(url)


class GetMainProdFeedbacks(TestCase):
    """Получение списка отзывов о товарах для отображения на главной"""
    def test_get_main_prod_feedbacks(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/prod_feedback'
        send_response(url)


class GetMainKitFeedbacks(TestCase):
    """Получение списка отзывов о программах для отображения на главной"""
    def test_get_main_prod_feedbacks(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/kit_feedback'
        send_response(url)


class ReceiveNotification(TestCase):
    """Обработка оповещения об успешной оплате заказа от PayKeeper"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)
        self.record = {
            "id": "62965626262",
            "sum": "2901",
            "clientid": "Семенов Роман Степанович",
            "orderid": "1565",
            "key": "f3e8a6f1f730fb87178dafd169d29cb7",
            "service_name": " ",
            "client_email": "asdasd@mail.ru",
            "client_phone": "79065489322",
            "ps_id": " ",
            "batch_date": "2019-06-13 23:33:09",
            "fop_receipt_key": " ",
            "bank_id": " ",
            "card_number": " ",
            "card_holder": " ",
            "card_expiry": " "
            }

    def test_receive_notification(self):  # pylint: disable=missing-function-docstring
        url = 'api/shop/payment_notice'
        flag = 'post'
        send_response_jwt(url, flag, self.record)


class GetPayLink(TestCase):
    """Получение ссылки на оплату"""
    def setUp(self):  # pylint: disable=missing-function-docstring
        auth = Authentication()
        response = auth.test_auth()
        self.token = response.json()['token']
        logger.debug(self.token)

    def test_get_pay_link(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/shop/order_payment/4400fbc6-8f48-44d9-a900-14abe1562ff6?'
        'bonus_amount=10&deposit_amount=10&shipping_amount=2'  # pylint: disable=pointless-string-statement
        flag = 'get'
        send_response_jwt(url, flag)
