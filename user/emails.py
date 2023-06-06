from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from core.email import EmailService


def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_str(urlsafe_base64_decode(pk))


class TokenBasedEmail(EmailService):

    def get_base_url(self):
        raise NotImplementedError

    def get_context_data(self):
        context = super().get_context_data()
        uid = encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)

        context["url"] = f'{settings.BASE_URL}{self.get_base_url()}?uid={uid}&token={token}'
        context["uid"] = uid
        context["token"] = token
        return context


class ConfirmationEmail(EmailService):
    template = "confirmation"


class ActivationEmail(TokenBasedEmail):
    template = 'activation'

    def get_base_url(self):
        return settings.EMAIL_ACTIVATION_URL


class PasswordResetEmail(TokenBasedEmail):
    template = "password_reset"

    def get_base_url(self):
        return settings.EMAIL_PASSWORD_RESET_URL
