from decimal import Decimal
from django.urls import reverse

from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class ValidWithdrawTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.wallet.balance = Decimal('100.00')
        self.wallet.save()

    def test_valid_withdraw_create_transaction_and_update_balance(self):
        url = reverse('withdraw_funds')
        response = self.client.post(url, {
            'wallet': self.wallet.id,
            'amount': '50.00',
        }, follow=True)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('50.00'))

        transaction = Transaction.objects.filter(
            sender=self.user,
            transaction_type='WITHDRAW',
            amount=Decimal('50.00'),
        ).first()

        self.assertIsNotNone(transaction)
        self.assertContains(response,'withdrawn successfully')