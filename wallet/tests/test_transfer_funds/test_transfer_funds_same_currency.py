from wallet.models import User, Wallet
from decimal import Decimal
from django.urls import reverse
from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class TransferFundsSameCurrencyTest(WalletTestCase):
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

    def test_transfer_same_currency_adjusts_balance_and_log_transaction(self):
        recipient_wallet = Wallet.objects.create(
            user=self.recipient,
            currency=self.wallet.currency
        )

        url = reverse('transfer_funds')
        response = self.client.post(url, {
            'sender_wallet': self.wallet.id,
            'recipient': self.recipient.username,
            'recipient_wallet': recipient_wallet.id,
            'amount': '40.00',
            'note': 'Test same currency transfer'
        }, follow=True)

        self.wallet.refresh_from_db()
        recipient_wallet.refresh_from_db()

        self.assertEquals(self.wallet.balance, Decimal('60.00'))
        self.assertEquals(recipient_wallet.balance, Decimal('40.00'))

        transaction = Transaction.objects.filter(
            sender=self.user,
            receiver=self.recipient,
            amount=Decimal('40.00'),
            transaction_type='TRANSFER'
        ).first()
        self.assertIsNotNone(transaction)

