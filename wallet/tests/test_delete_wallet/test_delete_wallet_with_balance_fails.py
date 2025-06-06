from wallet.models import Currency, Wallet
from wallet.tests.base import WalletTestCase

from django.urls import reverse

class DeleteWalletWithBalanceFailsTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.delete_wallet_url = reverse('account_settings')
        self.currency = Currency.objects.create(
            code='EUR',
            name='Euro',
        )

    def test_delete_wallet_with_balance_fails(self):
        wallet = Wallet.objects.create(
            user=self.user,
            currency=self.currency,
            balance=100,
        )
        response = self.client.post(self.delete_wallet_url, {
            'delete_wallet': '1',
            'wallet_id': wallet.id,
        })

        self.assertEquals(response.status_code, 302)
        self.assertTrue(Wallet.objects.filter(id=wallet.id).exists())