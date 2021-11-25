from admin_tools.dashboard import AppIndexDashboard, Dashboard, modules
from django.utils.translation import ugettext_lazy as _

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # noqa: F401


class CustomIndexDashboard(Dashboard):
    columns = 3

    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)

        self.children += [
            modules.ModelList(title='Управление магазином',
                              models=[
                                  'shop.models.Product',
                                  'shop.models.Kit',
                                  'shop.models.Category',
                                  'shop.models.SubCategory',
                                  'shop.models.ProductFeedback',
                                  'shop.models.KitFeedback',
                                  'shop.models.ActiveComponent',
                                  'shop.models.Event',
                              ])
        ]

        self.children += [
            modules.ModelList(title='Управление заказами и обращениями',
                              models=[
                                  'shop.models.Order',
                                  'shop.models.AdviceType',
                                  'shop.models.Advice',
                              ])
        ]

        self.children += [
            modules.ModelList(title='Управление клиентами',
                              models=[
                                  'appuser.models.AppUser',
                              ])
        ]

        self.children += [
            modules.ModelList(title='Управление контентом сайта',
                              models=[
                                  'blog.models.Article', 'shop.models.Slide',
                                  'blog.models.ArticleSubCategory',
                                  'shop.models.DefaultDeliveryPrice'
                              ])
        ]

        self.children += [
            modules.ModelList(
                title='Управление бонусными программами и промокодами',
                models=[
                    'shop.models.BonusParams',
                    'shop.models.PromoCode',
                ])
        ]

        self.children += [
            modules.ModelList(
                title='Управление обращениями в техподдержку',
                models=[
                    'support.models.RequestType',
                    # 'support.models.RequestStatus',
                    'support.models.Request',
                ])
        ]

        # self.children.append(
        #     modules.LinkList(_('Полезные ссылки'),
        #                      draggable=True,
        #                      deletable=True,
        #                      collapsible=True,
        #                      children=[
        #                          {
        #                              'title': _('Tiande'),
        #                              'url': 'https://www.oren-tiande.ru',
        #                              'external': True,
        #                              'attrs': {
        #                                  'target': '_blank'
        #                              },
        #                          },
        #                          {
        #                              'title': _('amoCRM'),
        #                              'url': 'https://www.amocrm.ru/',
        #                              'external': True,
        #                              'attrs': {
        #                                  'target': '_blank'
        #                              },
        #                          },
        #                      ]))


class CustomAppIndexDashboard(AppIndexDashboard):
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

    def init_with_context(self, context):
        return super(CustomAppIndexDashboard, self).init_with_context(context)
