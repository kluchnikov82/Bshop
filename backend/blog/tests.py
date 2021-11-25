"""В данном модуле происходит тестировние следующих API-сервисов:
1. Получение списка статей.
2. Получение контента статьи.
"""
import logging
from django.test import TestCase
from appuser.utils import send_response  # pylint: disable=import-error

from bshop.backend.cfg import devsettings  # pylint: disable=wrong-import-position

logging.config.dictConfig(devsettings.LOGGING)
logger = logging.getLogger('blog')  # pylint: disable=invalid-name


class ArticlesList(TestCase):
    """Получение списка статей"""
    def test_articles_list(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/blog/articles?limit=5&offset=1'
        send_response(url)


class ArticleDetail(TestCase):
    """Получение контента статьи"""
    def test_article_detail(self):  # pylint: disable=missing-function-docstring,no-self-use
        url = 'api/blog/articles/7b202ab2-27be-4e66-82b4-a7f51c255438'
        send_response(url)

