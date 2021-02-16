from rest_framework import generics, authentication, permissions, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework import status, viewsets, filters

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework.response import Response


from user.permissions import ProfileAccessPermission
from user import serializers
from core import models

import random


class UserOTPView(viewsets.ModelViewSet):
    """Viewset for User OTP"""

    queryset = models.UserOTP.objects.all()
    serializer_class = serializers.UserOTPSerializer
    authentication_classes = (TokenAuthentication,)

    # def create(self, request):
    #     # ref: https://stackoverflow.com/a/41003177/8666088
    #     otp = int("".join([str(random.randint(0, 9)) for _ in range(7)]))

    #     try:
    #         exist = models.UserOTP.objects.get(email=request.data["email"])

    #         if exist:
    #             exist.otp = otp
    #             exist.save()
    #             data = serializers.UserOTPSerializer(exist).data
    #             return Response(data=data, status=status.HTTP_201_CREATED)
    #     except:
    #         request.data["otp"] = otp
    #         return super().create(request)


class CreateUserAPIView(generics.CreateAPIView):
    """Creates a new user in the system"""

    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (ProfileAccessPermission,)


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


class SearchedUserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("=username",)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    # serializer_class = serializers.AuthtokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        has_shop = False

        try:
            if user.is_owner:
                has_shop = True if models.Shop.objects.get(owner=user) else False
            elif user.is_manager or user.is_salesman:
                owner = user.created_by
                has_shop = True if models.Shop.objects.get(owner=owner) else False
        except:
            has_shop = False

        usertype = ""

        if user.is_owner:
            usertype = "owner"
        elif user.is_manager:
            usertype = "manager"
        elif user.is_salesman:
            usertype = "salesman"

        return Response(
            {
                "token": token.key,
                "user": {"id": user.pk, "name": user.name, "type": usertype},
                "has_shop": has_shop,
            }
        )

        # ref: https://stackoverflow.com/questions/58588653/django-rest-framework-obtainauthtoken-user-login-api-view


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, ProfileAccessPermission)

    def get_object(self):
        """Retrive and return authenticated user"""
        return self.request.user

    
