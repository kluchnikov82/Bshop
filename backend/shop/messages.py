"""
Тексты email
"""


def get_order_created_message(order_no, total_amount, order_link):
    """
    Текст оповещения о создании заказа
    :param order_no: номер заказа
    :param total_amount: сумма заказа
    :param order_link:
    :return:
    """
    return f"""
Добрый день!
Ваш email был указан в качестве контактного при оформлении заказа №{order_no} на сумму {total_amount} рублей в интернет-магазине dari-cosmetics.ru.
Ссылка на заказ: { order_link }
Оплатить заказ вы можете перейдя по ссылке: {order_link}
Спасибо!

С уважением,
Интернет-магазин dari-cosmetics.ru
"""  # noqa: E501


def get_order_updated_message(order_no, total_amount, order_link):
    """
    Текст оповещения об изменении заказа
    :param order_no: номер заказа
    :param total_amount: сумма заказа
    :param order_link:
    :return:
    """
    return f"""
Добрый день!
Изменен заказ №{order_no} на сумму {total_amount} рублей в интернет-магазине dari-cosmetics.ru.
Ссылка на заказ: { order_link }
Оплатить заказ вы можете перейдя по ссылке: {order_link}
Спасибо!

С уважением,
Интернет-магазин dari-cosmetics.ru
"""  # noqa: E501
