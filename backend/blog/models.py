"""
Blog models
"""
from ckeditor.fields import RichTextField
from django.db import models
from django.utils import timezone as tz

from core.models import BaseModel, AutoIncHitCountModelMixin
from core.models import ImagePreviewModelMixin
from core.validators import validate_slug
from shop.models import Category, Product


class ArticleSubCategory(BaseModel):
    """
    Подкатегория статьи
    """
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование подкатегории')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Категория',
                                 related_name='article_subcats')

    class Meta:
        verbose_name = 'Подкатегория статьи'
        verbose_name_plural = 'Подкатегории статьи'
        ordering = ['name']
        db_table = 'blog_subcategory'

    def __str__(self):
        return '%s -> %s' % (self.category.name, self.name)


class Article(BaseModel, ImagePreviewModelMixin, AutoIncHitCountModelMixin):
    """
    Статья блога
    """
    header = models.CharField(max_length=255,
                              verbose_name='Заголовок',
                              blank=False)
    image = models.ImageField(upload_to='article_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение')
    teaser = models.TextField(max_length=8000, verbose_name='Тизер')
    body = RichTextField(blank=True,
                         null=True,
                         default=None,
                         verbose_name='Текст статьи')
    products = models.ManyToManyField(Product,
                                      related_name='article_products',
                                      verbose_name='Товары в статье')
    started = models.DateTimeField(default=tz.now,
                                   verbose_name='Дата начала показа на сайте')
    ended = models.DateTimeField(
        blank=False, verbose_name='Дата завершения показа на сайте')
    hit_count = models.PositiveIntegerField(
        default=0, verbose_name='Количество просмотров')
    sub_categories = models.ManyToManyField(ArticleSubCategory,
                                            through='SubCatArticle',
                                            verbose_name='Подкатегории',
                                            related_name='subcat_articles')
    slug = models.CharField(
        max_length=255, unique=True, verbose_name='URL', validators=[validate_slug, ])

    class Meta:
        ordering = ['-created']
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Статьи блога'
        db_table = 'blog_article'

    def __str__(self):
        return self.header


class SubCatArticle(BaseModel):
    """
    Подкатегория статьи
    """
    subcategory = models.ForeignKey(ArticleSubCategory,
                                    on_delete=models.DO_NOTHING,
                                    verbose_name='Подкатегория')
    article = models.ForeignKey(Article,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Статья')

    class Meta:
        verbose_name = 'Подкатегории статьи'
        verbose_name_plural = 'Подкатегории статьи'
        db_table = 'blog_subcat_article'

    def __str__(self):
        return '%s -> %s: %s' % (self.subcategory.category.name,
                                 self.subcategory.name, self.article.header)


class CatArticle(models.Model):
    """
    Связка категория <-> статья
    """
    category = models.ForeignKey(Category,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Категория',
                                 related_name='article_cat')
    article = models.ForeignKey(Article,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Статья')
    name = models.CharField(max_length=250,
                            db_index=True,
                            verbose_name='Наименование категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='category_images/%Y/%m/%d/',
                              blank=True,
                              verbose_name='Изображение категории')

    class Meta:
        verbose_name = 'Категории статьи'
        verbose_name_plural = 'Категория статьи'
        db_table = 'view_article_categories'
        managed = False

    def __str__(self):
        return '%s: %s' % (self.category.name, self.article.header)
