from django.urls import reverse
from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class DashboardTransactionTypeFilterTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.receiver = self.create_user(username='receiver_user')
        self.transaction_types = [
            'ADD',
            'WITHDRAW',
            'TRANSFER',
        ]

        for t_type in self.transaction_types:
            Transaction.objects.create(
                sender=self.user if t_type != 'ADD' else None,
                receiver=self.receiver if t_type != 'WITHDRAW' else None,
                amount=10,
                transaction_type=t_type,
            )

    def test_filter_by_transaction_type(self):
        for t_type in self.transaction_types:
            response = self.client.get(reverse('wallet_dashboard'), {
                'type': t_type,
            })
            self.assertEqual(response.status_code, 200)
            transactions = response.context['transactions']
            for tx in transactions:
                self.assertEqual(tx.transaction_type, t_type)