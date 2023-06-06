from django.conf import settings
from django.utils.module_loading import import_string


class EmailService:

    template = None

    def __init__(self, request=None, context=None, user=None):
        self.request = request
        self.context = context or {}
        if user or request:
            self.user = user or request.user
        else:
            self.user = None

    @property
    def preferred_language(self):
        return self.user.preferred_language if self.user else 'en'

    def get_context_data(self, **kwargs):
        self.context.update({
            'language': self.preferred_language,
            'protocol': 'https',
            'site_name': settings.APPLICATION_NAME,
            'base_url': settings.FRONT_URL,
            'dashboard_url': settings.DASHBOARD_URL
        })
        if self.user:
            self.context.update({
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
            })
        self.context.update(**kwargs)
        return self.context

    def get_template_uuid(self):
        return settings.EMAIL_UUID_MAPPING[self.preferred_language][self.template]

    def send(self, **kwargs):
        to = [kwargs.get('email') or self.user.email]
        adapter = import_string(settings.EMAIL_ADAPTER)(
            self.get_template_uuid(), self.request, self.get_context_data(**kwargs), self.user
        )
        adapter.send(to)
