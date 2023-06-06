from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from core.utils.test_utils import BaseFactory
from user.models import User


class Factory(BaseFactory):
    def create_user(self, **kwargs):
        from user.tests import DEFAULT_PASSWORD

        defaults = dict(
            username="john",
            email="john.doe@avantgarde.com",
            password=DEFAULT_PASSWORD,
            first_name="John",
            last_name="Doe"
        )
        merged = dict(defaults, **kwargs)

        try:
            User.objects.get(username=merged["username"])
        except User.DoesNotExist:
            return User.objects.create_user(**merged)

    def create_group(self, models=None, **kwargs):
        defaults = {"name": "awesome"}
        group: Group = self.create(Group, defaults, kwargs)

        if models is not None:
            permissions = []
            for model in models:
                if isinstance(model, (list, tuple)):
                    model = model[0]
                    prefixes = model[1]
                else:
                    model = model
                    prefixes = ("add", "change", "delete")

                code_names = [prefix + "_" + model.__name__.lower() for prefix in prefixes]
                permissions += list(
                    Permission.objects.filter(
                        codename__in=code_names, content_type=ContentType.objects.get_for_model(model)
                    )
                )
            for permission in permissions:
                group.permissions.add(permission)
        return group


user_factory = Factory()
