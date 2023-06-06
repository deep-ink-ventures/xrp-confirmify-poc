from logging import getLogger
from time import sleep

import sib_api_v3_sdk
from django.conf import settings

from core.email.adapter import Adapter
from sib_api_v3_sdk.rest import ApiException


def get_client():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.EMAIL_SERVICE_API_KEY
    return sib_api_v3_sdk.ApiClient(configuration=configuration)


class SendInBlue(Adapter):

    def send(self, to):
        to = [{'email': _} for _ in list(to)]
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(get_client())
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=self.uuid,
            params=self.context
        )
        try:
            api_instance.send_transac_email(send_smtp_email)
        except ApiException as exc:
            sleep(1)
            try:
                api_instance.send_transac_email(send_smtp_email)
            except ApiException as exc:
                getLogger('alerts').critical(
                    f'Sending mails to {to} with uuid {self.uuid} failed: {exc.reason} / {exc.body}.'
                )