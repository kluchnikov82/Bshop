"""
Blog urls
"""
from django.urls import path

from .views import ViewArticle, ViewArticleList

urlpatterns = []

urlpatterns += [
    path('articles/<uuid:id>', ViewArticle.as_view(), name='article'),
    path('articles/<str:slug>', ViewArticle.as_view(), name='article-slug'),
    path('articles', ViewArticleList.as_view(), name='article-list'),
]
