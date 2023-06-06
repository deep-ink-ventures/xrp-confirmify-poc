from django.conf import settings

from core.email.adapter import Adapter
from core.utils import OnTheFlyObject


class TestEmail(Adapter):

    outbox = []

    @classmethod
    def count(cls):
        return len(cls.outbox)

    @classmethod
    def reset_outbox(cls):
        cls.outbox = []

    @classmethod
    def last_mail(cls):
        return cls.outbox[-1]

    @property
    def template_name(self):
        for k, v in settings.EMAIL_UUID_MAPPING['en'].items():
            if v == self.uuid:
                return k

    def send(self, to):
        if not settings.TESTING:
            print("=== Test Email ===")
            print(f"Template: {self.template_name}")
            print(f"Template UUID: {self.uuid}")
            print(f"To: {to}")
            print(f"Context: {self.context}")
        self.outbox.append(OnTheFlyObject(
            uuid=self.uuid,
            to=to,
            context=self.context,
            template=self.template_name
        ))
