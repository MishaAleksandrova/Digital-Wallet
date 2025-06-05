from wallet.tests.base import WalletTestCase
from django.urls import reverse
from wallet.utils import generate_email_token


class TestVerifyEmailViewValidToken(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.inactive_user = self.create_inactive_user()
        self.token = generate_email_token(self.inactive_user.email)

    def test_verify_email_valid_token_activates_user(self):
        url = reverse('verify_email') + f'?token={self.token}'
        response = self.client.get(url)

        self.inactive_user.refresh_from_db()

        self.assertTrue(self.inactive_user.is_active)
        self.assertTrue(self.inactive_user.email_verified)
        self.assertRedirects(response, reverse('wallet_dashboard'))
        self.assertIn('_auth_user_id', self.client.session)
