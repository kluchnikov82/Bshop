"""
Shop urls
"""
from django.urls import path

import shop.views as views

urlpatterns = []

urlpatterns += [
    path('products/<uuid:id>',
         views.ViewProductDetail.as_view(),
         name='product-detail'),
    path('products/<str:slug>',
         views.ViewProductDetail.as_view(),
         name='product-detail-slug'),
    path('products', views.ViewProductList.as_view(), name='product-list'),
    path('products_all',
         views.ViewProductListAll.as_view(),
         name='product-list-all'),
    path('orders/<uuid:id>', views.ViewOrder.as_view(), name='order'),
    path('orders', views.ViewOrders.as_view(), name='order-list'),
    path('catalog',
         views.ViewCatProductList.as_view(),
         name='cat-subcat-product-list'),
    path('categories/<str:slug>',
         views.ViewCatDetail.as_view(),
         name='cat-detail'),
    path('categories',
         views.ViewCategoriesList.as_view(),
         name='cats-list'),
    path('subcategories/<str:slug>',
         views.ViewSubCatDetail.as_view(),
         name='sub-cat-detail'),
    path('kits/<uuid:id>', views.ViewKitDetail.as_view(), name='kit-detail'),
    path('kits/<str:slug>', views.ViewKitDetail.as_view(), name='kit-detail-slug'),
    path('kits', views.ViewKitsList.as_view(), name='kits-list'),
    path('advice_types',
         views.ViewAdviceTypesList.as_view(),
         name='advice-types-list'),
    path('advice', views.ViewCreateAdvice.as_view(), name='create-advice'),
    path('order_payment/<uuid:order_id>',
         views.ViewOrderPayment.as_view(),
         name='order-payment'),
    path('payment_notice',
         views.ViewPaymentNotice.as_view(),
         name='payment-notice'),
    path('components/<uuid:id>',
         views.ViewActiveComponentDetail.as_view(),
         name='component-detail'),
    path('components/<str:slug>',
         views.ViewActiveComponentDetail.as_view(),
         name='component-detail-slug'),
    path('slides', views.ViewSlides.as_view(), name='slides-list'),
    path('events', views.ViewEvents.as_view(), name='events-list'),
    path('events/<uuid:id>',
         views.ViewEventDetail.as_view(),
         name='event-detail'),
    path('rep_orders', views.ViewOrders1C.as_view(), name='rep-orders'),
    path('bonus_upload',
         views.View1CBonusUpload.as_view(),
         name='bonus-upload'),
    path('promo', views.ViewPromocodes.as_view(), name='check-promo'),
    path('sb_payment_notice',
         views.ViewSBNotice.as_view(),
         name='sb-payment-notice'),
]

# Сервисы управления отзывами (старые, для удаления)
urlpatterns += [
    path('prod_feedback/<uuid:id>',
         views.ViewProductFeedback.as_view(),
         name='prod-feedback-get'),
    path('prod_feedback',
         views.ViewProductFeedback.as_view(),
         name='prod-feedback-create'),
    path('kit_feedback/<uuid:id>',
         views.ViewKitFeedback.as_view(),
         name='kt-feedback-get'),
    path('kit_feedback',
         views.ViewKitFeedback.as_view(),
         name='kt-feedback-create'),
    ]

# Сервисы управления отзывами
urlpatterns += [
    path('prod_feedbacks',
         views.ViewProductFeedbacks.as_view(),
         name='products-feedbacks-list'),
    path('prod_feedbacks/<uuid:id>',
         views.ViewProductFeedback.as_view(),
         name='product-feedback-get'),
    path('kit_feedbacks/<uuid:id>',
         views.ViewKitFeedback.as_view(),
         name='kit-feedback-get'),
    path('kit_feedbacks',
         views.ViewKitFeedbacks.as_view(),
         name='kit-feedbacks-list'),
    path('feedbacks',
         views.ViewFeedbackList.as_view(),
         name='all-feedbacks-list'),
    ]

#  Сервисы доставки
urlpatterns += [
    path('calc_shipping',
         views.ViewCalcShipping.as_view(),
         name='calc-shipping'),
    path('countries', views.ViewCountries.as_view(), name='countries'),
    path('delivery_points',
         views.ViewDeliveryPoints.as_view(),
         name='delivery-points'),
    path('cdek/regions', views.ViewCDEKRegions.as_view(), name='cdek-regions'),
    path('cdek/cities', views.ViewCDEKCities.as_view(), name='cdek-cities'),
    path('cdek/delivery_points', views.ViewCDEKDeliveryPoints.as_view(),
         name='cdek-delivery-points'),
]
