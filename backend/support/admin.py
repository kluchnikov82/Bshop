"""
Support admin
"""

from django.contrib import admin

from core.admin import BaseModelAdmin

from .models import Request, RequestType


class RequestTypeAdmin(BaseModelAdmin):
    """
    Тип запроса в support
    """
    list_display = ('created', 'description')
    list_editable = ('description', )
    fields = ('description', 'created', 'updated')
    search_fields = ('description', )
    ordering = ('description', )
    readonly_fields = ('created', 'updated')


class RequestAdmin(BaseModelAdmin):
    """
    Запрос в support
    """
    list_display = ('created', 'user', 'text', 'request_type',
                    'request_status')
    list_editable = ('request_status', )
    fields = ('created', 'updated', 'user', 'text', 'request_type',
              'request_status')
    list_filter = ('request_status', )
    ordering = ('-created', )
    readonly_fields = ('created', 'updated')


admin.site.register(RequestType, RequestTypeAdmin)
admin.site.register(Request, RequestAdmin)
