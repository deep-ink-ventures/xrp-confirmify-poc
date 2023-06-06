from django.test import TestCase

from user.tests import DEFAULT_PASSWORD
from ..models import User


class UserTest(TestCase):
    def setUp(self) -> None:
        from user.tests.factory import user_factory
        super().setUp()
        user_factory.create_group(name="RAPID_APPMELDUNG_CUSTOMER")

    def test_delete_finally(self):
        user = User.objects.create_user("foo", "foo@gmail.com", DEFAULT_PASSWORD)
        user.delete_finally()

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="foo")
