"""
ID и описания дополнительных полей
"""
AMOCRM_FIELDS = {
    "contacts": {
        "127489": {
            "id": 127489,
            "name": "Должность",
            "field_type": 1,
            "sort": 7,
            "code": "POSITION",
            "is_multiple": False,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "127491": {
            "id": 127491,
            "name": "Телефон",
            "field_type": 8,
            "sort": 4,
            "code": "PHONE",
            "is_multiple": True,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "264231": "WORK",
                "264233": "WORKDD",
                "264235": "MOB",
                "264237": "FAX",
                "264239": "HOME",
                "264241": "OTHER"
            }
        },
        "127493": {
            "id": 127493,
            "name": "Email",
            "field_type": 8,
            "sort": 6,
            "code": "EMAIL",
            "is_multiple": True,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "264243": "WORK",
                "264245": "PRIV",
                "264247": "OTHER"
            }
        },
        "127497": {
            "id": 127497,
            "name": "Мгн. сообщения",
            "field_type": 8,
            "sort": 8,
            "code": "IM",
            "is_multiple": True,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "264249": "SKYPE",
                "264251": "ICQ",
                "264253": "JABBER",
                "264255": "GTALK",
                "264257": "MSN",
                "264259": "OTHER"
            }
        },
        "127829": {
            "id": 127829,
            "name": "CF_NAME_USER_AGREEMENT",
            "field_type": 3,
            "sort": 9,
            "code": "USER_AGREEMENT",
            "is_multiple": False,
            "is_system": True,
            "is_editable": False,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "334163": {
            "id": 334163,
            "name": "Instagram",
            "field_type": 7,
            "sort": 506,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "384813": {
            "id": 384813,
            "name": "Адрес доставки",
            "field_type": 7,
            "sort": 504,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "401761": {
            "id": 401761,
            "name": "Примечание",
            "field_type": 1,
            "sort": 505,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "443463": {
            "id": 443463,
            "name": "Возраст",
            "field_type": 2,
            "sort": 503,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "480381": {
            "id": 480381,
            "name": "Фото до",
            "field_type": 7,
            "sort": 510,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "480591": {
            "id": 480591,
            "name": "Фото после",
            "field_type": 7,
            "sort": 511,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        }
    },
    "leads": {
        "384803": {
            "id": 384803,
            "name": "Регион клиента",
            "field_type": 4,
            "sort": 502,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "745009": "Адыгея",
                "745011": "Алтайский край",
                "745013": "Амурская область",
                "745015": "Архангельская область",
                "745017": "Астраханская область",
                "745019": "Башкортостан",
                "745021": "Белгородская область",
                "745023": "Брянская область",
                "745025": "Бурятия Республика",
                "745027": "Владимирская область",
                "745029": "Волгоградская область",
                "745031": "Вологодская область",
                "745033": "Воронежская область",
                "745035": "Дагестан",
                "745037": "Еврейская АО",
                "745039": "Ивановская область",
                "745041": "Ингушетия",
                "745043": "Иркутская область",
                "745045": "Кабардино-Балкария",
                "745047": "Калининградская область",
                "745049": "Калмыкия",
                "745051": "Калужская область",
                "745053": "Камчатка",
                "745055": "Карачаево-Черкессия",
                "745057": "Карелия",
                "745059": "Кемеровская область",
                "745061": "Кировская область",
                "745063": "Коми Республика",
                "745065": "Коми-Пермяцкий АО",
                "745067": "Костромская область",
                "745069": "Краснодарский край",
                "745071": "Красноярский край",
                "745073": "Курганская область",
                "745075": "Курская область",
                "745077": "Ленинградская область",
                "745079": "Липецкая область",
                "745081": "Магаданская область",
                "745083": "Мари-Эл",
                "745085": "Мордовия",
                "745087": "Московская область",
                "745089": "Мурманская область",
                "745091": "Нижегородская область",
                "745093": "Новгородская область",
                "745095": "Новосибирская область",
                "745097": "Омская область",
                "745099": "Оренбургская область",
                "745101": "Орловская область",
                "745103": "Пензенская область",
                "745105": "Пермская область",
                "745107": "Приморский край",
                "745109": "Псковская область",
                "745111": "Ростовская область",
                "745113": "Рязанская область",
                "745115": "Самарская область",
                "745117": "Саратовская область",
                "745119": "Сахалин",
                "745121": "Свердловская область",
                "745123": "Северная Осетия",
                "745125": "Смоленская область",
                "745127": "Ставропольский край",
                "745129": "Таймыр",
                "745131": "Тамбовская область",
                "745133": "Татарстан",
                "745135": "Тверская область",
                "745137": "Томская область",
                "745139": "Тува",
                "745141": "Тульская область",
                "745143": "Тюменская область",
                "745145": "Удмуртия",
                "745147": "Ульяновская область",
                "745149": "Усть-Ордынский АО",
                "745151": "Хабаровский край",
                "745153": "Хакассия",
                "745155": "Ханты-Мансийск",
                "745157": "Челябинская область",
                "745159": "Чеченская Республика",
                "745161": "Читинская область",
                "745163": "Чувашская Республика",
                "745165": "Якутия (Саха)",
                "745167": "Ямало-Ненецкий АО",
                "745169": "Ярославская область",
                "763601": "Республика Крым",
                "823301": "Казахстан",
                "823303": "Украина",
                "823305": "Беларусь"
            }
        },
        "384805": {
            "id": 384805,
            "name": "Источник лида",
            "field_type": 4,
            "sort": 503,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "745171": "Instagram",
                "745173": "Рекомендации",
                "745175": "Сайт",
                "745177": "Facebook",
                "745179": "Вконтакте",
                "745181": "Реклама в Яндексе",
                "745183": "YouTube"
            }
        },
        "384807": {
            "id": 384807,
            "name": "Интерес клиента",
            "field_type": 5,
            "sort": 504,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "745185": "Проблемная кожа",
                "745187": "Сухая кожа",
                "745189": "Уход за глазами",
                "745191": "Антивозрастное",
                "745193": "Пигментация",
                "745195": "Рост волос",
                "745197": "Уход за молодой кожей",
                "745199": "Серия 25+",
                "745201": "Серия 35+",
                "745203": "Жирная кожа",
                "745205": "Антицелюлит",
                "745207": "Уход за телом",
                "745209": "Рубцы и шрамы",
                "745211": "Кушон",
                "763603": "Подарки",
                "881711": "Мезороллер"
            }
        },
        "384821": {
            "id": 384821,
            "name": "Отзыв",
            "field_type": 9,
            "sort": 506,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "384823": {
            "id": 384823,
            "name": "Причина отказа",
            "field_type": 4,
            "sort": 507,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "745213": "Не устроила цена",
                "745215": "Не устроил срок доставки",
                "745217": "Нет в наличии",
                "745219": "Хотят посмотреть прежде чем покупать",
                "745221": "Купил в другом месте",
                "745223": "Не сказал причину"
            }
        },
        "384825": {
            "id": 384825,
            "name": "Отказ подробно",
            "field_type": 9,
            "sort": 508,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "401573": {
            "id": 401573,
            "name": "Онлайн счет",
            "field_type": 7,
            "sort": 501,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "443333": {
            "id": 443333,
            "name": "Откуда узнали",
            "field_type": 5,
            "sort": 505,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "823241": "Хэштег",
                "823243": "Рекомендация от подруги/сестры",
                "823245": "гив",
                "823247": "повторный заказ",
                "823249": "Ботановна",
                "823251": "Екатерина Шрейнер",
                "823253": "Елена Горд",
                "823255": "Кристи (Kristitheone)",
                "823257": "не помню",
                "823259": "топ в инстаграм//рекомендация в инстаграм",
                "828923": "блоггер не помню кто",
                "875569": "Блоггер Тома Блум"
            }
        },
        "485367": {
            "id": 485367,
            "name": "Адрес доставки",
            "field_type": 1,
            "sort": 510,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": False,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "485369": {
            "id": 485369,
            "name": "Комментарий к заказу",
            "field_type": 1,
            "sort": 511,
            "code": "",
            "is_multiple": False,
            "is_system": False,
            "is_editable": False,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        }
    },
    "companies": {
        "127491": {
            "id": 127491,
            "name": "Телефон",
            "field_type": 8,
            "sort": 4,
            "code": "PHONE",
            "is_multiple": True,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "264231": "WORK",
                "264233": "WORKDD",
                "264235": "MOB",
                "264237": "FAX",
                "264239": "HOME",
                "264241": "OTHER"
            }
        },
        "127493": {
            "id": 127493,
            "name": "Email",
            "field_type": 8,
            "sort": 6,
            "code": "EMAIL",
            "is_multiple": True,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {},
            "enums": {
                "264243": "WORK",
                "264245": "PRIV",
                "264247": "OTHER"
            }
        },
        "127495": {
            "id": 127495,
            "name": "Web",
            "field_type": 7,
            "sort": 8,
            "code": "WEB",
            "is_multiple": False,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        },
        "127499": {
            "id": 127499,
            "name": "Адрес",
            "field_type": 9,
            "sort": 12,
            "code": "ADDRESS",
            "is_multiple": False,
            "is_system": True,
            "is_editable": True,
            "is_required": False,
            "is_deletable": True,
            "is_visible": True,
            "params": {}
        }
    },
    "customers": [],
    "catalogs": {
        "4987": {
            "438391": {
                "id": 438391,
                "name": "Артикул",
                "field_type": 1,
                "sort": 0,
                "code": "SKU",
                "is_multiple": False,
                "is_system": True,
                "is_editable": True,
                "is_required": False,
                "is_deletable": False,
                "is_visible": True,
                "params": {}
            },
            "438393": {
                "id": 438393,
                "name": "Описание",
                "field_type": 9,
                "sort": 3,
                "code": "DESCRIPTION",
                "is_multiple": False,
                "is_system": True,
                "is_editable": True,
                "is_required": False,
                "is_deletable": False,
                "is_visible": True,
                "params": {}
            },
            "438395": {
                "id": 438395,
                "name": "Цена",
                "field_type": 2,
                "sort": 2,
                "code": "PRICE",
                "is_multiple": False,
                "is_system": True,
                "is_editable": True,
                "is_required": False,
                "is_deletable": False,
                "is_visible": True,
                "params": {}
            },
            "438397": {
                "id":
                438397,
                "name":
                "Группа",
                "field_type":
                18,
                "sort":
                1,
                "code":
                "GROUP",
                "is_multiple":
                False,
                "is_system":
                True,
                "is_editable":
                True,
                "is_required":
                False,
                "is_deletable":
                False,
                "is_visible":
                True,
                "params": {},
                "enums": {
                    "587": "Другое",
                    "595": "Умывание",
                    "597": "Волосы",
                    "599": "Тонизирование",
                    "601": "Кремы",
                    "603": "Глаза",
                    "605": "Кушон",
                    "607": "Пигментация",
                    "729": "Маски",
                    "899": "Сыворотки",
                    "901": "Пилинги"
                },
                "values_tree": [{
                    "id": 587,
                    "value": "Другое",
                    "depth": 0
                }, {
                    "id": 595,
                    "value": "Умывание",
                    "depth": 0
                }, {
                    "id": 597,
                    "value": "Волосы",
                    "depth": 0
                }, {
                    "id": 599,
                    "value": "Тонизирование",
                    "depth": 0
                }, {
                    "id": 601,
                    "value": "Кремы",
                    "depth": 0
                }, {
                    "id": 603,
                    "value": "Глаза",
                    "depth": 0
                }, {
                    "id": 605,
                    "value": "Кушон",
                    "depth": 0
                }, {
                    "id": 607,
                    "value": "Пигментация",
                    "depth": 0
                }, {
                    "id": 729,
                    "value": "Маски",
                    "depth": 0
                }, {
                    "id": 899,
                    "value": "Сыворотки",
                    "depth": 0
                }, {
                    "id": 901,
                    "value": "Пилинги",
                    "depth": 0
                }]
            },
            "438399": {
                "id": 438399,
                "name": "This is set",
                "field_type": 3,
                "sort": 14,
                "code": "IS_SET",
                "is_multiple": False,
                "is_system": True,
                "is_editable": True,
                "is_required": False,
                "is_deletable": False,
                "is_visible": False,
                "params": {}
            },
            "438401": {
                "id": 438401,
                "name": "External ID",
                "field_type": 1,
                "sort": 15,
                "code": "EXTERNAL_ID",
                "is_multiple": False,
                "is_system": True,
                "is_editable": True,
                "is_required": False,
                "is_deletable": False,
                "is_visible": False,
                "params": {}
            }
        }
    }
}


def get_field_id(cat_name, code):
    """
    Получение id поля по его коду или названию
    :param cat_name: именование типа объекта (contacts, leads, companies, etc)
    :param code: код или наименование поля
    :return: id поля
    """
    for cat, fields in AMOCRM_FIELDS.items():
        if cat == cat_name:
            if cat != 'catalogs':
                if isinstance(fields, dict):
                    for item_id, item in fields.items():
                        if code in (item['name'], item['code']):
                            return item_id
            else:
                for _, cat_items in fields.items():
                    for item_id, item in cat_items.items():
                        if code in (item['name'], item['code']):
                            return item_id
    return None
