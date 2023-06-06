from datetime import timedelta
import string, random

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from xrpl.core.keypairs import generate_seed
from xrpl.wallet import Wallet, generate_faucet_wallet


class BaseUserManagerExtended(UserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username.lower()})

    def create_superuser(self, email=None, password=None, **extra_fields):
        return super().create_superuser(email, email, password, **extra_fields)


class User(AbstractUser):

    objects = BaseUserManagerExtended()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    REQUIRED_FIELDS = []
    seed = models.CharField(max_length=16, unique=True)

    wallet_address = models.CharField(max_length=256)

    preferred_language = 'en'

    @staticmethod
    def generate_seed():
        """This is for demo purposes. In a real world scenario we'll use a safe key storage on aws"""
        while True:
            seed = ''.join(random.sample(string.ascii_lowercase, 16))
            if User.objects.filter(seed=seed).count() == 0:
                return seed

    def load_wallet(self, client=None):
        from core import ripple

        client = client or ripple.get_client()
        issuer_wallet = Wallet(seed=generate_seed(self.seed), sequence=0)
        from xrpl.models.requests.account_info import AccountInfo
        acct_info = AccountInfo(
            account=issuer_wallet.classic_address,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(acct_info)
        if response.result.get('error') == 'actNotFound':
            balance = 0
        else:
            balance = int(response.result['account_data']['Balance'])

        if balance < 1000:
            if settings.APPLICATION_STAGE == 'production':
                raise NotImplemented
            else:
                generate_faucet_wallet(client, issuer_wallet)
        return issuer_wallet

    def save(self, *args, **kwargs):
        if not self.seed:
            self.seed = self.generate_seed()
            self.wallet_address = Wallet(seed=generate_seed(self.seed), sequence=0).classic_address

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