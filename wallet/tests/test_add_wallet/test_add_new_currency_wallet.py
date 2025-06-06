from wallet.models import Wallet, Currency
from wallet.tests.base import WalletTestCase
from django.urls import reverse

class AddNewCurrencyWalletTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.add_wallet_url = reverse('account_settings')
        self.currency = Currency.objects.create(
            code='EUR',
            name='Euro',
        )

    def test_add_new_currency_wallet(self):
        response = self.client.post(self.add_wallet_url, data={
            'currency': self.currency.id,
            'add_wallet': '1'
        })

        self.assertEqual(response.status_code, 302)
        wallet_exists = Wallet.objects.filter(user=self.user, currency=self.currency).exists()
        self.assertTrue(wallet_exists)