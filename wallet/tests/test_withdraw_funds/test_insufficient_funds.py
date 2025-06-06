from decimal import Decimal
from django.urls import reverse
from django.contrib.messages import get_messages
from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class InsufficientFundsWithdrawTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.wallet.balance = Decimal('10.00')
        self.wallet.save()

    def test_insufficient_funds_shown_error_and_does_not_change_balance(self):
        url = reverse('withdraw_funds')
        response = self.client.post(url, {
            'wallet': self.wallet.id,
            'amount': '100.00',
        }, follow=True)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('10.00'))

        transaction_exists = Transaction.objects.filter(
            sender=self.user,
            transaction_type='WITHDRAW',
            amount=Decimal('100.00'),
        )

        self.assertFalse(transaction_exists)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Insufficient funds" in str(msg) for msg in messages))