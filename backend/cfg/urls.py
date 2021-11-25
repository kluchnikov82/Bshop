"""
Common urls map
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import core.views

urlpatterns = []

urlpatterns += [
    path('admin/', admin.site.urls),
    path('admin_tools/', include('admin_tools.urls')),
]
"""
    Управление профилем пользователя (аутентификация, логаут, изменение пароля, редактирование профиля, etc.)
"""
urlpatterns += [
    path('api/appuser/', include('appuser.urls')),
]
"""
    Управление магазином
"""
urlpatterns += [
    path('api/shop/', include('shop.urls')),
]
"""
    Управление блогом
"""
urlpatterns += [
    path('api/blog/', include('blog.urls')),
]
"""
    Управление обращениями в техподдержку
"""
urlpatterns += [
    path('api/support/', include('support.urls')),
]
"""
    Реферральная ссылка
"""
urlpatterns += [
    path('api/ref/<ref_id>', core.views.ReferralView.as_view()),
]

urlpatterns += [
    path('_nested_admin/', include('nested_admin.urls')),
]

if settings.DEBUG:
    from core.views import TestView
    urlpatterns += [
        path('api/test', TestView.as_view(), name='test-view'),
    ]
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
