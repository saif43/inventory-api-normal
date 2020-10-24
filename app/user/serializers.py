from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object"""

    def validate(self, data):
        data["created_by"] = self.context["request"].user
        return data

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "name",
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
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


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
