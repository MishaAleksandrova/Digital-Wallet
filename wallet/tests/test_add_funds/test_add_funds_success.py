from decimal import Decimal
from django.urls import reverse
from wallet.models import Transaction
from wallet.tests.base import WalletTestCase

class AddFundsSuccessTest(WalletTestCase):
    def test_post_valid_data_increases_balance_and_logs_transaction(self):
        self.client.force_login(self.user)

        url = reverse('add_funds')
        response = self.client.post(url, {
            'user': self.user.id,
            'wallet': self.wallet.id,
            'amount': '50.00',
            'note': 'Test deposit'
        }, follow=True)

        self.wallet.refresh_from_db()
        self.assertEquals(self.wallet.balance, Decimal('150.00'))

        transaction = Transaction.objects.filter(
            receiver=self.user,
            amount=Decimal('50.00'),
            transaction_type='ADD'
        ).first()

        self.assertIsNotNone(transaction)
        self.assertEquals(transaction.transaction_type, 'ADD')
