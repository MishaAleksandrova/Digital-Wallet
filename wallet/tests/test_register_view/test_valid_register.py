from django.urls import reverse
from django.core import mail
from wallet.models import User, Wallet
from wallet.tests.base import WalletTestCase


class TestRegisterView(WalletTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('register')

    def test_post_valid_data_creates_inactive_user_add_wallet_and_sends_email(self):
        valid_data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "phone_number": "1234567890",
            "password1": "SecureP@ssw0rd",
            "password2": "SecureP@ssw0rd",
            "currency": self.currency.id,
        }
        response = self.client.post(self.url, data=valid_data)

        user = User.objects.filter(username="new_user").first()
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        self.assertTrue(Wallet.objects.filter(user=user, currency=self.currency).exists())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify Email", mail.outbox[0].subject)
        self.assertIn("new_user@example.com", mail.outbox[0].to)
        self.assertTemplateUsed(response, 'wallet/verify_prompt.html')