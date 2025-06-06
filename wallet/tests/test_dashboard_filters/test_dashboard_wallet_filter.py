from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class DashboardWalletFilterTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

        self.wallet2 = self.create_wallet(balance=200)

        self.tx_wallet1 = Transaction.objects.create(
            sender=self.user,
            receiver=None,
            amount=50,
            transaction_type='WITHDRAW',
        )

        self.tx_wallet2 = Transaction.objects.create(
            sender=self.user,
            receiver=None,
            amount=75,
            transaction_type='WITHDRAW',
        )

    def test_filter_by_wallet(self):
        response = self.client.get('/dashboard/', {
            'wallet': self.wallet2.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.tx_wallet2.amount))