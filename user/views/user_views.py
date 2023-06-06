from random import random
from time import sleep

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from ..emails import ActivationEmail, ConfirmationEmail, PasswordResetEmail
from ..models import User
from ..permissions import RequestedAccountIsLoggedInAccountOrAuthIfNotDetail
from ..serializers.user_serializer import UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer, TokenSerializer

class LoginThrottle(AnonRateThrottle):

    def get_rate(self):
        if settings.APPLICATION_STAGE in ['staging', 'development']:
            return "1000/hour"
        return "25/hour"


class UserViewSet(ModelViewSet):
    permission_classes = [RequestedAccountIsLoggedInAccountOrAuthIfNotDetail]
    serializer_class = UserSerializer

    def get_throttles(self):
        if self.action in (
                'create', 'activation', 'resend_activation', 'reset_password', 'reset_password_confirm',
        ):
            return [LoginThrottle()]
        return super().get_throttles()

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        extra_payload = {'is_active': False}

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(**extra_payload)
        headers = self.get_success_headers(serializer.data)

        ActivationEmail(request=self.request, user=user).send()
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        if self.action in (
                'create', 'activation', 'resend_activation', 'reset_password', 'reset_password_confirm',
        ):
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.all()
        if not user.is_staff:
            qs = qs.filter(pk=user.pk)

        return qs

    def get_object(self):
        if not self.kwargs.get('pk').isdigit():
            if self.kwargs.get('pk') == 'me':
                self.kwargs['pk'] = self.request.user.id
        return super().get_object()

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data, require_user_to_be_inactive=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        ConfirmationEmail(request=self.request, user=user).send()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path='resend-activation')
    def resend_activation(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get('email'), is_active=False)
            ActivationEmail(request=self.request, user=user).send()
        except User.DoesNotExist:
            # this is to prevent timing attacks!
            sleep(random())

        return Response(status=HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get('email'))
            PasswordResetEmail(request=self.request, user=user).send()
        except User.DoesNotExist:
            # this is to prevent timing attacks!
            sleep(random())

        return Response(status=HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path='reset-password-confirm')
    def reset_password_confirm(self, request, *args, **kwargs):
        validate_password(request.data.get('password'))
        serializer = TokenSerializer(data=request.data, require_user_to_be_inactive=False)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(request.data.get('password'))
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)


class ProfileBasedTokenView(TokenObtainPairView):
    throttle_classes = (LoginThrottle,)
    serializer_class = TokenObtainPairSerializer

    def get_serializer_class(self):
        return TokenObtainPairSerializer


class TokenRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer
