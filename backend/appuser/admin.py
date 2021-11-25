"""
Admin models for appuser
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.admin import BaseModelAdmin
from .models import AppUser, UserAddress


class UserAddressInline(admin.TabularInline):
    """
    Сохраненные адреса пользователя
    """
    model = UserAddress
    fields = ('address', 'is_primary', 'created')
    list_display = ('address', 'is_primary', 'created')
    readonly_fields = ('created', )
    extra = 0
    can_delete = True


class AppUserAdmin(BaseModelAdmin, UserAdmin):
    """
    Пользователь
    """
    model = AppUser
    search_fields = ('email', 'phone', 'username', 'last_name')
    list_display = ('username', 'created', 'partner_type_id', 'ref_id',
                    'last_name', 'first_name', 'patronymic', 'email', 'phone',
                    'bonus_balance', 'balance')
    fieldsets = (
        (None, {
            'fields': (
                'last_name', 'first_name', 'patronymic', 'email',
                'password', 'is_active', 'is_staff', 'groups',
                'phone', 'sms_notice', 'email_notice',
                'partner_type_id', 'current_target', 'current_discount',
                'current_bonus_share', 'balance', 'total_payments',
                'current_period_payments', 'last_period_payments',
                'bonus_balance', 'total_bonus_payments',
                'current_period_bonus_payments', 'last_period_bonus_payments',
                'total_sale_amount', 'current_period_sale_amount',
                'last_period_sale_amount', 'total_amount')
            }),
    )
    readonly_fields = ('current_discount', 'current_bonus_share',
                       'total_payments', 'current_period_payments',
                       'last_period_payments', 'total_bonus_payments',
                       'current_period_bonus_payments',
                       'last_period_bonus_payments',
                       'current_period_sale_amount', 'last_period_sale_amount',
                       'total_sale_amount', 'current_target', 'total_amount')
    list_filter = ('partner_type_id', )
    ordering = ('-created', )
    inlines = [
        UserAddressInline,
    ]


admin.site.register(AppUser, AppUserAdmin)
