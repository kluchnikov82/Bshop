"""
Base views
"""
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone as tz
from rest_framework import filters, generics, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

DEFAULT_PAGINATE_LIMIT = settings.DEFAULT_PAGINATE_LIMIT


class RUDView(generics.RetrieveUpdateDestroyAPIView):
    """
        Базовая вьюха для редактирования и просмотра одного экземпляра класса
    """
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = tz.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if len(self.szrs) == 1:
            get_szr = update_szr = delete_szr = self.serializer_class
        else:
            get_szr = self.szrs[0]
            update_szr = self.szrs[1]
            delete_szr = self.szrs[2]
        if self.request.method == 'GET':
            return get_szr
        if self.request.method in ('PUT', 'PATCH'):
            return update_szr
        if self.request.method == 'DELETE':
            return delete_szr
        return get_szr

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LCView(generics.ListCreateAPIView):
    """
        Базовая вьюха для просмотра списка объектов и создания экземпляра объекта
    """
    filter_backends = (filters.SearchFilter, )

    def paginate_queryset(self, queryset):
        if hasattr(self, 'paginate') and self.paginate:
            limit = int(self.request.GET.get('limit', DEFAULT_PAGINATE_LIMIT))
            offset = int(self.request.GET.get('offset', 0))
            items_count = queryset.count()
            if items_count == 0 or offset > items_count:
                result = []
            else:
                result = list(queryset[offset:offset + limit])
        else:
            result = queryset
            items_count = queryset.count()
        return result, items_count

    def get_serializer_class(self):
        if hasattr(self, 'szrs'):
            if len(self.szrs) == 1:
                get_szr = update_szr = delete_szr = self.serializer_class
            else:
                get_szr = self.szrs[0]
                update_szr = self.szrs[1]
                delete_szr = self.szrs[2]

            if self.request.method == 'GET':
                return get_szr
            if self.request.method in ('PUT', 'PATCH', 'POST'):
                return update_szr
            if self.request.method == 'DELETE':
                return delete_szr
            return get_szr
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if hasattr(self, 'paginate') and self.paginate:
            page, items_count = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            data = dict(count=items_count, results=serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data=data)


