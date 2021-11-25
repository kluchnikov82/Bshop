"""
Self-made authentification backends
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from core.utils import normalize_phone


class EmailBackend(ModelBackend):
    """
    Аутентификация по email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(
                    user):
                return user
        return None


class PhoneBackend(ModelBackend):
    """
    Аутентификация по номеру телефона
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(phone=normalize_phone(username))
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(
                    user):
                return user
        return None
