"""
Support serializers
"""
from rest_framework import serializers

from .models import Request, RequestType


class RequestTypeSzr(serializers.ModelSerializer):
    """
        Сериализатор типов обращений в техподдержку
    """
    class Meta:
        model = RequestType
        fields = ('id', 'description')


class RequestSzr(serializers.ModelSerializer):
    """
        Сериализатор обращений в техподдержку
    """
    class Meta:
        model = Request
        fields = ('request_type', 'text')
