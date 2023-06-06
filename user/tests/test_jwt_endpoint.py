from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from user.models import User
from user.tests import DEFAULT_PASSWORD, UserAwareTestCase


class JWTEndpoint(UserAwareTestCase):

    authenticate_standard_user = False

    def test_flow(self):
        self.standard_user.additional_scopes = ["read", "write"]
        self.standard_user.token_data = {"some": {"nested": "data"}}
        self.standard_user.save()
        self.equip_with_permissions(editable_models=[User], user=self.standard_user)

        # initally we are not logged in ...
        response = self.client.get(reverse("user-user-detail", kwargs={'pk': 'me'}))
        self.assertEqual(response.status_code, 401)

        # create JWT Token
        response = self.client.post(
            reverse("jwt-create"), {"email": self.standard_user.email, "password": DEFAULT_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        create_payload = response.json()

        self.assertIn("access", create_payload)
        self.assertIn("refresh", create_payload)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {create_payload["access"]}')
        response = self.client.get(reverse("user-user-detail", kwargs={'pk': 'me'}))
        self.assertEqual(response.status_code, 200)

        # refresh JWT Token
        response = self.client.post(reverse("jwt-refresh"), {"refresh": create_payload["refresh"]})
        self.assertEqual(response.status_code, 200)
        refresh_payload = response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_payload["access"]}')
        response = self.client.get(reverse("user-user-detail", kwargs={'pk': 'me'}))
        self.assertEqual(response.status_code, 200)

        # verify JWT Token
        response = self.client.post(reverse("jwt-verify"), {"token": refresh_payload["access"]})
        self.assertEqual(response.status_code, 200)

        # check additional token values
        token = AccessToken(create_payload["access"])
        self.assertEqual(token["token_type"], "access")
        self.assertEqual(token["iss"], settings.APPLICATION_SHORT_NAME)
        self.assertEqual(token["sub"], self.standard_user.email)
        self.assertEqual(token["aud"], settings.APPLICATION_SHORT_NAME)
        self.assertIn('iat', token)
        self.assertIn('exp', token)
        self.assertGreater(token['exp'], token['iat'])
