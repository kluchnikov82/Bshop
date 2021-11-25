"""
Support urls
"""

from django.urls import path

import support.views as views

urlpatterns = []

urlpatterns += [
    path('req_types',
         views.ViewRequestTypeList.as_view(),
         name='request-type-list'),
    path('requests', views.ViewRequestList.as_view(), name='request-list')
]
