from rest_framework import authentication
from rest_framework import exceptions
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger(__name__)

class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Check if user is already authenticated by checking _user attribute
        if hasattr(request, '_user') and request._user is not None:
            logger.info(f"User authenticated: {request._user.username}")
            return (request._user, None)
        return None 

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch the user by username
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None 