from datetime import timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class BaseUserManagerExtended(UserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username.lower()})


class User(AbstractUser):

    objects = BaseUserManagerExtended()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    REQUIRED_FIELDS = []

    preferred_language = 'en'

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        self.username = self.email
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Our delete is a little softer than the default.
        """
        self.is_active = False
        self.save()

    def delete_finally(self, using=None, keep_parents=False):
        """
        This is an explicit delete, it's not exposed via API to normal users.
        """
        return super().delete(using=using, keep_parents=keep_parents)

    def get_scopes(self):
        scopes = [
            _.upper() for _ in self.groups.all().values_list('name', flat=True)
        ] if not self.is_superuser else [
            _.upper() for _ in Group.objects.all().values_list('name', flat=True)
        ]
        if self.is_staff:
            scopes.append('STAFF')
        if self.is_superuser:
            scopes.append('SUPERUSER')
        return scopes

    def enhance_jwt_token(self, token):
        for k, v in {
            'iss': settings.APPLICATION_SHORT_NAME,
            'sub': self.email,
            'aud': settings.APPLICATION_SHORT_NAME,
            'iat': now(),
            'exp': now() + timedelta(days=30),
            'scope': self.get_scopes()
        }.items():
            token[k] = v

        return token

    def get_by_natural_key(self, username):
        return self.objects.get(**{self.USERNAME_FIELD: username})