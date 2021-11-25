"""
Support views
"""
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.views import LCView, ListView

from .models import Request, RequestStatus, RequestType
from .serializers import RequestSzr, RequestTypeSzr
from .tasks import post_create_request


class ViewRequestTypeList(ListView):
    """Просмотр списка типов обращений в поддержку"""
    serializer_class = RequestTypeSzr
    permission_classes = (AllowAny, )
    queryset = RequestType.objects.filter(deleted__isnull=True)


class ViewRequestList(LCView):
    """Просмотр списка обращений пользователя в поддержку"""
    serializer_class = RequestSzr
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = Request.objects.filter(
            user_id=self.request.user.id,
            deleted__isnull=True).order_by('-created')
        return queryset

    def perform_create(self, serializer):
        user_id = self.request.user.id
        request_status = RequestStatus.objects.get(
            status=RequestStatus.IN_PROGRESS).id
        serializer.save(user_id=user_id, request_status_id=request_status)

        request_dict = dict(request_type_id=serializer.data['request_type'],
                            text=serializer.data['text'])
        post_create_request.delay(request_dict, user_id)
