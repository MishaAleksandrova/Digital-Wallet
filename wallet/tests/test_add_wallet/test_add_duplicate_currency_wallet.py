from django.urls import reverse
from wallet.models import Wallet, Currency
from wallet.tests.base import WalletTestCase

class AddDuplicateCurrencyWalletTests(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.add_wallet_url = reverse('account_settings')
        self.currency = Currency.objects.create(
            code='EUR',
            name='Euro',
        )


    def test_add_duplicate_currency_wallet(self):

        Wallet.objects.create(user=self.user, currency=self.currency)
        response = self.client.post(self.add_wallet_url, data={
            'currency': self.currency.id,
            'add_wallet': '1'
        })

        self.assertEqual(response.status_code, 302)
        wallets = Wallet.objects.filter(user=self.user, currency=self.currency)
        self.assertEqual(wallets.count(), 1)