from decimal import Decimal
from unittest.mock import patch
from django.urls import reverse

from wallet.models import Transaction, User
from wallet.tests.base import WalletTestCase


class TransferFundsDifferentCurrencyTest(WalletTestCase):
    def setUp(self):
        super().setUp()

        self.client.force_login(self.user)

        self.recipient = User.objects.create(
            username="recipient",
            password="testpass",
            email="recipient@example.com",
        )
        self.wallet.balance = Decimal('100.00')
        self.wallet.save()

    @patch('wallet.views.get_exchange_rate', return_value='2.0')
    def test_transfer_different_currency_applies_conversion(self, mock_rate):
        self.wallet.balance = Decimal('100.00')
        self.wallet.save()
        different_currency = self.create_currency('EUR', 'Euro')
        recipient_wallet = self.create_wallet(
            user=self.recipient,
            currency=different_currency,
        )

        url = reverse('transfer_funds')
        response = self.client.post(url, {
            'sender_wallet': self.wallet.id,
            'recipient': self.recipient.username,
            'recipient_wallet': recipient_wallet.id,
            'amount': '30.00',
            'note': 'Test conversion'
        }, follow=True)

        self.wallet.refresh_from_db()
        recipient_wallet.refresh_from_db()

        self.assertEquals(self.wallet.balance, Decimal('70.00'))
        self.assertEquals(recipient_wallet.balance, Decimal('60.00'))

        transaction = Transaction.objects.filter(
            sender=self.user,
            receiver=self.recipient,
            transaction_type='TRANSFER',
        ).first()

        self.assertIsNotNone(transaction)
