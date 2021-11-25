"""
Blog views
"""

from django.utils import timezone as tz
from rest_framework.permissions import AllowAny

from core.views import ListView, RetrieveHitCountAPIView
from core.views import MultipleFieldLookupMixin
from .models import Article
from .serializers import ArticleListSzr, ArticleSzr


class ViewArticleList(ListView):
    """Просмотр списка статей"""
    serializer_class = ArticleListSzr
    permission_classes = (AllowAny, )
    queryset = Article.objects.filter(started__lte=tz.now(),
                                      ended__gte=tz.now())
    paginate = True


class ViewArticle(MultipleFieldLookupMixin, RetrieveHitCountAPIView):
    """Получение атрибутов статьи"""
    permission_classes = (AllowAny, )
    serializer_class = ArticleSzr
    queryset = Article.objects.filter(deleted__isnull=True)
    lookup_field = 'id'
    multiple_lookup_fields = ('id', 'slug',)
