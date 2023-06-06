# coding=utf-8
import shutil

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches

from django.urls import reverse
from django.contrib.auth.models import Permission, User
from rest_framework.test import APITestCase

from core.email.adapter.test_email import TestEmail
from .factory import user_factory

DEFAULT_PASSWORD = "QCNArDz96w4BmamVri04TI11SMYPijyE"


class UserAwareTestCase(APITestCase):
    """
    Sets up standard user and staff user.

    If init_permissions is set to True, than permissions are set up for every test. If you don't like that, set it to
    false and call equip_with_permissions() manually.

    editable_models is only required for DjangoModelPermission aware models, but it won't hurt to add them.
    """

    DUMMY_PIC = "backend/core/tests/test_pic.jpg"

    authenticate_standard_user = True
    init_permissions_for_staff_user = True

    # editable_models = (
    #     (ModelA, ('add', 'change', 'delete'),
    #     (ModelB, ('delete')
    # )
    #
    # or just
    # editable_models = ( ModelA, ModelB )
    editable_models = ()

    def getTokenFor(self, user, authenticate=True):
        response = self.client.post(reverse("jwt-create"), {"email": user.email, "password": DEFAULT_PASSWORD})
        token = response.json()["access"]
        if authenticate:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def logOut(self):
        self.client.credentials(HTTP_AUTHORIZATION="")

    def setUp(self):
        for cache in settings.CACHES.keys():
            caches[cache].clear()

        TestEmail.reset_outbox()
        from user.tests.factory import user_factory

        user_factory.create_group(name="CUSTOMER", models=[User])

        self.standard_user = user_factory.create_user()
        self.staff_user = user_factory.create_user(
            username="max",
            email="max.staff@avantgarde.com",
            password=DEFAULT_PASSWORD,
            first_name="Max",
            last_name="Staff",
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

        if self.authenticate_standard_user:
            self.getTokenFor(self.standard_user, authenticate=True)

        if self.init_permissions_for_staff_user:
            self.equip_with_permissions(user=self.staff_user)

    def equip_with_permissions(self, editable_models=None, user=None):
        user = user or self.standard_user
        editable_models = editable_models or self.editable_models
        if not isinstance(editable_models, (list, tuple)):
            editable_models = [editable_models]
        permissions = []

        for editables in editable_models:
            if isinstance(editables, (list, tuple)):
                model = editables[0]
                prefixes = editables[1]
            else:
                model = editables
                prefixes = ("add", "change", "delete")

            code_names = [prefix + "_" + model.__name__.lower() for prefix in prefixes]
            permissions += list(
                Permission.objects.filter(
                    codename__in=code_names, content_type=ContentType.objects.get_for_model(model)
                )
            )
        user.user_permissions.add(*permissions)

    def tearDown(self):
        try:
            shutil.rmtree("test-files")
        except FileNotFoundError:
            pass
