from rest_framework import generics, authentication, permissions, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import status, viewsets, filters

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q

from user.permissions import ProfileAccessPermission
from user import serializers
from core import models


class CreateUserAPIView(generics.CreateAPIView):
    """Creates a new user in the system"""

    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (ProfileAccessPermission,)


class UserListView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (ProfileAccessPermission,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_superuser:
            return queryset

        if self.request.user.is_owner:
            """if user is owner, then return self and manangers, salesmans created by him"""

            queryset = queryset.filter(
                Q(created_by=self.request.user) | Q(pk=self.request.user.id)
            )

            return queryset


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = serializers.AuthtokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, ProfileAccessPermission)

    def get_object(self):
        """Retrive and return authenticated user"""
        return self.request.user
