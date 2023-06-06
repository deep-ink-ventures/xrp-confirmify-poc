from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, AuthenticationFailed
from rest_framework.fields import empty
from rest_framework_simplejwt.authentication import default_user_authentication_rule

from ..emails import decode_uid
from ..models import User

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as OriginalTokenRefreshSerializer, \
    TokenObtainSerializer

from django.utils.translation import gettext_lazy as _

INVALID_CREDENTIALS_ERROR = _("Unable to log in with provided credentials.")
INACTIVE_ACCOUNT_ERROR = _("User account is disabled.")
INVALID_TOKEN_ERROR = _("Invalid token for given user.")
INVALID_UID_ERROR = _("Invalid user id or user doesn't exist.")
STALE_TOKEN_ERROR = _("Stale token for given user.")
PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
USERNAME_MISMATCH_ERROR = _("The two {0} fields didn't match.")
INVALID_PASSWORD_ERROR = _("Invalid password.")
EMAIL_NOT_FOUND = _("User with given email does not exist.")
CANNOT_CREATE_USER_ERROR = _("Unable to create account.")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        # we currently do not allow email update
        # if you want to do so, we need a full blown flow for this (validate email etc.)
        if 'email' in validated_data:
            validated_data.pop('email')

        if 'password' in validated_data:
            validate_password(validated_data['password'])

        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user


class TokenObtainPairSerializer(TokenObtainSerializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    @classmethod
    def get_token_data(cls, user, *args, **kwargs):
        refresh = cls.get_token(user)
        access = refresh.access_token
        access = user.enhance_jwt_token(access)
        return {
            'refresh': str(refresh),
            'access': str(access)
        }

    def validate(self, attrs):
        super().validate(attrs)
        return self.get_token_data(self.user, self.context['request'])


class TokenRefreshSerializer(OriginalTokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access = AccessToken(data["access"])
        user = User.objects.get(id=access.payload["user_id"])
        access = user.enhance_jwt_token(access)
        data["access"] = str(access)
        return data


class TokenSerializer(serializers.Serializer):

    def __init__(self, instance=None, data=empty, require_user_to_be_inactive=False, **kwargs):
        self.require_user_to_be_inactive = require_user_to_be_inactive
        super().__init__(instance, data, **kwargs)

    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "invalid_token": INVALID_TOKEN_ERROR,
        "invalid_uid": INVALID_UID_ERROR,
        "stale_token": STALE_TOKEN_ERROR
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        # uid validation have to be here, because validate_<field_name>
        # doesn't work with modelserializer
        try:
            uid = decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )

        if self.user.is_active and self.require_user_to_be_inactive:
            raise PermissionDenied(self.error_messages["stale_token"])

        is_token_valid = default_token_generator.check_token(
            self.user, self.initial_data.get("token", "")
        )
        if is_token_valid:
            return validated_data
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )
