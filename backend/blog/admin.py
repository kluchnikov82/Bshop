"""
Blog admin
"""
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from core.admin import BaseModelAdmin
from core.tasks import sitemap_generate
from .models import Article, ArticleSubCategory, SubCatArticle


class ArticleSubCategoryInline(admin.TabularInline):
    model = SubCatArticle
    readonly_fields = ('created', )
    fields = ('subcategory', 'created')
    extra = 1
    can_delete = True


class ArticleAdmin(BaseModelAdmin):
    list_display = ('header', 'created', 'updated', 'started', 'ended',
                    'image_tag')
    fields = ('header', 'slug', 'teaser', 'image', 'hit_count', 'body', 'started',
              'ended', 'products')
    search_fields = ('header', 'teaser', 'body')
    ordering = ('-created', )
    readonly_fields = ('created', 'updated')

    def save_model(self, request, obj, form, change):
        sitemap_generate.delay(settings.SITEMAP_GENERATE_PATH)

    formfield_overrides = {
        models.TextField: {
            'widget':
            Textarea(attrs={
                'rows': 1,
                'cols': 140,
                'style': 'height: 15em;'
            })
        },
    }

    inlines = (ArticleSubCategoryInline, )


class ArticleSubCategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'category', 'description', 'created')
    list_editable = ('description', )
    fields = ('category', 'created', 'name', 'description')
    search_fields = ('name', 'description')
    ordering = (
        'category',
        'name',
    )
    readonly_fields = ('created', )


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleSubCategory, ArticleSubCategoryAdmin)
