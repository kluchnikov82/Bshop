"""
Тексты писем
"""


def payment_confirmed_message(order_no, order_date, order_amount):
    """
    Текст оповещения о подтверждении платежа
    :param order_no: номер заказа
    :param order_date: дата заказа
    :param order_amount: сумма заказа
    """
    return f"""
    Здравствуйте!

    Поступила оплата по счету №{order_no} от {order_date} на сумму {order_amount} руб.

    Подробную информацию о платеже и счете вы можете увидеть на сайте https://dari-cosmetics.ru.

    Благодарим за выбор нашей услуги!

    С уважением,
    dari-cosmetics.ru
    """
