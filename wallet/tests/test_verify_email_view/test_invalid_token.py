from wallet.tests.base import WalletTestCase
from django.urls import reverse


class TestVerifyEmailViewInvalidToken(WalletTestCase):
    def test_verify_email_invalid_token_renders_failure_template(self):
        url = reverse('verify_email') + f'?token=invalid_or_expired'
        response = self.client.get(url)

        self.assertTemplateUsed(response, 'wallet/verify_failed.html')
