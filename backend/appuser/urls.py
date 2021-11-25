"""
Appuser urls
"""
from django.urls import include, path

import appuser.views as views

urlpatterns = [
    path('login', views.MyObtainJSONWebToken.as_view(), name='login'),
    path('logout', views.MyLogoutView.as_view(), name='logout'),
    path('change_password',
         views.MyPasswordChangeView.as_view(),
         name='change_password'),
    path('users/<uuid:id>',
         views.AppUserView.as_view(),
         name='user-get-update'),
    path('users', views.AppUserCreateView.as_view(), name='user-create'),
    path('accounts/', include('allauth.urls')),
    path('ref_orders',
         views.ViewReferrerOrdersList.as_view(),
         name='ref-orders-list'),
    path('auth/social', views.SocialAuthView.as_view(), name='social-auth'),
    path('avatar_upload/<filename>',
         views.AvatarUploadView.as_view(),
         name='avatar-upload'),
    path('bonus_to_balance',
         views.BonusToBalanceView.as_view(),
         name='bonus-to-balance'),
    path('password/reset',
         views.PasswordReset.as_view(),
         name='password-reset'),
    path('password/confirm/<uuid:id>',
         views.PasswordConfirm.as_view(),
         name='password-confirm'),
    path('users_1c/<str:phone>', views.Users1CView.as_view(), name='users-1c'),
    path('referrals', views.ViewReferrerList.as_view(), name='referrrals'),
    path('bonus-history', views.ViewBonusHistoryList.as_view(), name='bonus-history'),
]

# urlpatterns += [
#     re_path(r"^confirm-email/(?P<key>[-:\w]+)/$", ConfirmEmailView.as_view(),
#         name='account_confirm_email'),
# ]
