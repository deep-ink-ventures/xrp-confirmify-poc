from django.urls import reverse

from core.email.adapter.test_email import TestEmail
from . import DEFAULT_PASSWORD, UserAwareTestCase
from ..models import User
from ..serializers.user_serializer import UserSerializer


class APITestCase(UserAwareTestCase):

    authenticate_standard_user = False

    def test_non_staff_users_can_only_see_themself(self):
        self.equip_with_permissions(editable_models=[User], user=self.standard_user)
        self.getTokenFor(self.standard_user)

        response = self.client.get(reverse('user-user-list'))
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['results'][0]['id'], self.standard_user.id)

        self.getTokenFor(self.staff_user)
        self.equip_with_permissions(editable_models=[User], user=self.staff_user)
        response = self.client.get(reverse('user-user-list'))
        payload = response.json()
        self.assertEqual(payload['count'], 2)

    def test_me(self):
        self.equip_with_permissions(editable_models=[User], user=self.standard_user)
        self.getTokenFor(self.standard_user)
        self.equip_with_permissions(user=self.standard_user)
        response = self.client.get(reverse("user-user-detail", kwargs={'pk': 'me'}))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["email"], self.standard_user.email)

    def test_user_create_and_activate(self):
        # create
        response = self.client.post(
            reverse("user-user-list"),
            {"email": "mail.christianpeters@gmail.com", "password": DEFAULT_PASSWORD},
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='mail.christianpeters@gmail.com')
        self.assertFalse(user.is_active)

        payload = response.json()
        for _ in UserSerializer.Meta.fields:
            if _ != 'password':
                self.assertIn(_, payload)

        # fetch email
        self.assertEqual(len(TestEmail.outbox), 1)
        self.assertEqual(TestEmail.last_mail().template, 'activation')
        context = TestEmail.last_mail().context

        # activate
        response = self.client.post(reverse("user-user-activation"), {"uid": context["uid"], "token": context["token"]})
        self.assertEqual(response.status_code, 204)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

        self.assertEqual(len(TestEmail.outbox), 2)
        self.assertEqual(TestEmail.last_mail().template, 'confirmation')

        response = self.client.post(
            reverse("jwt-create"), {"email": 'mail.christianpeters@gmail.com', "password": DEFAULT_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)

        # case insensitive
        response = self.client.post(
            reverse("jwt-create"), {"email": 'Mail.christianpeters@gmail.com', "password": DEFAULT_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)

    def test_resend_activation_email(self):
        response = self.client.post(reverse("user-user-resend-activation"), data={'email': 'user@does-not.exist'})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(TestEmail.outbox), 0)

        self.standard_user.is_active = False
        self.standard_user.save()

        response = self.client.post(reverse("user-user-resend-activation"), data={'email': self.standard_user.email})
        self.assertEqual(response.status_code, 204)

        self.assertEqual(len(TestEmail.outbox), 1)
        self.assertEqual(TestEmail.last_mail().template, 'activation')

    def test_change_password(self):
        self.equip_with_permissions(editable_models=[User], user=self.standard_user)
        self.getTokenFor(self.standard_user)

        new_password = 'NBX0TUFTA8ScDLuMiNGz4oF5Ega5TX0m'
        self.assertTrue(self.standard_user.check_password(DEFAULT_PASSWORD))
        response = self.client.patch(
            reverse("user-user-detail", kwargs={'pk': 'me'}), {"password": new_password},
        )

        self.assertEqual(response.status_code, 200)
        self.standard_user.refresh_from_db()
        self.assertTrue(self.standard_user.check_password(new_password))

        # unsecure pw
        response = self.client.patch(
            reverse("user-user-detail", kwargs={'pk': 'me'}), {"password": 'test'},
        )
        payload = response.json()
        self.assertIn('This password is too short. It must contain at least 8 characters.', payload['error'])
        self.assertIn('This password is too common.', payload['error'])
        self.assertEqual(400, response.status_code)

        self.standard_user.refresh_from_db()
        self.assertTrue(self.standard_user.check_password(new_password))

    def test_email_not_changeable(self):
        original_email = self.standard_user.email
        self.equip_with_permissions(editable_models=[User], user=self.standard_user)
        self.getTokenFor(self.standard_user)

        response = self.client.patch(
            reverse("user-user-detail", kwargs={'pk': 'me'}), {"email": 'new@email.de'},
        )
        self.assertEqual(response.status_code, 200)
        self.standard_user.refresh_from_db()
        self.assertEqual(self.standard_user.email, original_email)

    def test_password_reset_flow(self):
        new_password = "QtdTxh`baw`b,)J3I(y742W]]3N^f8"
        self.assertTrue(self.standard_user.check_password(DEFAULT_PASSWORD))
        response = self.client.post(reverse("user-user-reset-password"), {"email": 'user@does-not.exist'})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(TestEmail.outbox), 0)

        response = self.client.post(reverse("user-user-reset-password"), {"email": self.standard_user.email})
        self.assertEqual(response.status_code, 204)

        self.assertEqual(len(TestEmail.outbox), 1)
        context = TestEmail.last_mail().context

        # bad password
        response = self.client.post(
            reverse("user-user-reset-password-confirm"),
            {
                "uid": context["uid"],
                "token": context["token"],
                "password": 'test',
            }
        )
        payload = response.json()
        self.assertIn('This password is too short. It must contain at least 8 characters.', payload['error'])
        self.assertIn('This password is too common.', payload['error'])
        self.assertEqual(400, response.status_code)

        context = TestEmail.last_mail().context
        response = self.client.post(
            reverse("user-user-reset-password-confirm"),
            {
                "uid": context["uid"],
                "token": context["token"],
                "password": new_password,
            }
        )
        self.assertEqual(response.status_code, 204)

        self.standard_user.refresh_from_db()
        self.assertTrue(self.standard_user.check_password(new_password))

        # token outdated
        response = self.client.post(
            reverse("user-user-reset-password-confirm"),
            {
                "uid": context["uid"],
                "token": context["token"],
                "password": new_password,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['token'][0], 'Invalid token for given user.')
