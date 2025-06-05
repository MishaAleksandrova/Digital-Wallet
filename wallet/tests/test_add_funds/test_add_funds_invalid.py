from django.urls import reverse
from wallet.tests.base import WalletTestCase


class AddFundsInvalidTest(WalletTestCase):
    def test_post_invalid_user_or_wallet_shows_error(self):
        self.client.force_login(self.user)
        url = reverse('add_funds')

        response = self.client.post(url, {
            'user': 9999,
            'wallet': 9999,
            'amount': '50.00',
            'note': 'Invalid test',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context.get('form')
        self.assertIsNotNone(form)

        self.assertTrue('user' in form.errors or 'wallet' in form.errors)