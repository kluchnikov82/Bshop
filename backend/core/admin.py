"""
Base admin model
"""
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils import timezone as tz


class BaseModelAdmin(admin.ModelAdmin):
    """
    Базовая модель для админки
    """
    def get_actions(self, request):
        """
        Override метод получения доступных пользователю действий для удаления "удаления"
        :param request: запрос
        :return: массив действий
        """
        actions = super(BaseModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def my_delete_selected(self, request, queryset):
        """
        Override метода удаления объектов в queryset - устанавливаем deleted = now()
        """
        for obj in queryset:
            obj.deleted = tz.now()
            obj.save()

        if queryset.count() == 1:
            self.message_user(request, '1 объект успешно удален')
        else:
            self.message_user(request,
                              f'{queryset.count()} объектов успешно удалено')

    my_delete_selected.short_description = 'Удалить выбранные записи'

    def delete_model(self, request, obj):
        """
        Override метода удаления модели - устанавливаем deleted = now()
        """
        obj.deleted = tz.now()
        obj.save()

    formfield_overrides = {
        models.TextField: {
            'widget':
            Textarea(attrs={
                'rows': 1,
                'cols': 40,
                'style': 'height: 3em;'
            })
        },
    }

    actions = [my_delete_selected]

    def get_queryset(self, request):
        qs = super(BaseModelAdmin, self).get_queryset(request)
        return qs.filter(deleted__isnull=True)
