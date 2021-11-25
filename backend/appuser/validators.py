"""Appuser validators"""

from rest_framework.validators import UniqueValidator, qs_filter

from core.utils import normalize_phone


class PhoneUniqueValidator(UniqueValidator):
    """Валидатор уникальности номера телефона"""
    def filter_queryset(self, value, queryset, field_name):
        value = normalize_phone(value)
        filter_kwargs = {'%s__%s' % (field_name, self.lookup): value}
        return qs_filter(queryset, **filter_kwargs)
