"""
Blog serializers
"""
from rest_framework import serializers

from core.serializers import EagerLoadingMixin, FilteredListSerializer
from shop.models import Category
from shop.serializers import ProductShortSzr

from .models import Article, ArticleSubCategory, CatArticle, SubCatArticle


class ArticleCategoriesSzr(serializers.HyperlinkedModelSerializer):
    """
        Сериализатор связки статья-категории
    """
    category_id = serializers.ReadOnlyField(source='category.id')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = CatArticle
        fields = (
            'category_id',
            'category_name',
        )


class ArticleSubCategoriesSzr(serializers.HyperlinkedModelSerializer):
    """
        Сериализатор связки статья-подкатегории
    """
    subcategory_id = serializers.ReadOnlyField(source='subcategory.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.name')

    class Meta:
        model = SubCatArticle
        list_serializer_class = FilteredListSerializer
        fields = (
            'subcategory_id',
            'subcategory_name',
        )


class ArticleListSzr(serializers.ModelSerializer, EagerLoadingMixin):
    """Сериализатор списка статей"""
    _PREFETCH_RELATED_ARGS = (
        ('catarticle_set__category',
         Category.objects.filter(deleted__isnull=True)),
        ('subcatarticle_set',
         SubCatArticle.objects.filter(deleted__isnull=True)),
        ('subcatarticle_set__subcategory',
         ArticleSubCategory.objects.filter(deleted__isnull=True)),
    )

    categories = ArticleCategoriesSzr(source='catarticle_set', many=True)
    subcategories = ArticleSubCategoriesSzr(source='subcatarticle_set',
                                            many=True)

    class Meta:
        model = Article
        fields = ('id', 'header', 'teaser', 'image', 'products', 'created',
                  'updated', 'categories', 'subcategories', 'hit_count',
                  'slug')


class ArticleSzr(serializers.ModelSerializer):
    """Сериализатор статьи"""
    categories = ArticleCategoriesSzr(source='catarticle_set', many=True)
    subcategories = ArticleSubCategoriesSzr(source='subcatarticle_set',
                                            many=True)
    products = ProductShortSzr(many=True)

    class Meta:
        model = Article
        fields = ('id', 'header', 'body', 'image', 'created', 'updated',
                  'hit_count', 'products', 'categories', 'subcategories',
                  'hit_count', 'slug')
