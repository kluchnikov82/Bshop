"""
Base serializers and methods
"""
from django.db.models.query import Prefetch
from rest_framework import serializers

from .models import OKSM


class FilteredListSerializer(serializers.ListSerializer):  # pylint: disable=abstract-method
    """
    Класс для фильтрации неудаленных записей во всех моделях
    """
    def to_representation(self, data):
        data = data.filter(deleted__isnull=True)
        return super(FilteredListSerializer, self).to_representation(data)


class EagerLoadingMixin:
    """
    Предзагрузка связанных моделей для ускоренной сериализации
    """
    @classmethod
    def setup_eager_loading(cls, queryset):  # pylint: disable=missing-function-docstring
        if hasattr(cls, "_SELECT_RELATED_FIELDS"):
            queryset = queryset.select_related(*cls._SELECT_RELATED_FIELDS)
        if hasattr(cls, "_PREFETCH_RELATED_FIELDS"):
            queryset = queryset.prefetch_related(*cls._PREFETCH_RELATED_FIELDS)
        if hasattr(cls, "_PREFETCH_RELATED_ARGS"):
            args = []
            for item in cls._PREFETCH_RELATED_ARGS:
                args.append(Prefetch(item[0], item[1]))
            queryset = queryset.prefetch_related(*args)
        return queryset


class OKSMSzr(serializers.ModelSerializer):
    """
    Сериализатор классификатора ОКСМ
    """
    class Meta:
        model = OKSM
        fields = '__all__'
