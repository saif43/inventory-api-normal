from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from core import models

import random


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object"""

    def validate(self, data):
        # ref: https://stackoverflow.com/a/40216082/8666088
        if not "email" in data.keys():
            msg = {"email": _("User must have an email address.")}
            raise serializers.ValidationError(msg, code="authentication")

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "name",
            "contact",
            "password",
            "is_owner",
            "is_manager",
            "is_salesman",
            "created_by",
        )

        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
            }
        }

        read_only_fields = ("id", "created_by")

    def create(self, validated_data):
        """creates user with encrypted password and retruns the user"""

        if self.context["request"].user.is_anonymous:
            validated_data["created_by"] = get_user_model().objects.get(
                username="superuser"
            )
        else:
            validated_data["created_by"] = self.context["request"].user

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserOTPSerializer(serializers.ModelSerializer):
    """Serializer for user OTP"""

    class Meta:
        model = models.UserOTP
        fields = ("id", "email", "otp")
        read_only_fields = ("id", "otp")

    def create(self, validated_data):
        """creates user with encrypted password and retruns the user"""

        otp = int("".join([str(random.randint(0, 9)) for _ in range(6)]))
        email = validated_data["email"]

        exist = models.UserOTP.objects.filter(email=email)

        if exist:
            for i in exist:
                i.delete()

        return models.UserOTP.objects.create(email=email, otp=otp)


class AuthtokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    username = serializers.CharField()
    password = serializers.CharField(
        style={
            "input_type": "password",
        },
        trim_whitespace=False,
    )

    def validate(self, data):
        """validate and authticate the user"""
        username = data.get("username")
        password = data.get("password")

        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        data["user"] = user
        return data
