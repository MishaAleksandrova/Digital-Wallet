from decimal import Decimal
from django.urls import reverse
from wallet.models import User
from wallet.tests.base import WalletTestCase


class TransferFundsInsufficientBalanceTest(WalletTestCase):
    def setUp(self):
        super().setUp()

        self.client.force_login(self.user)

        self.recipient = User.objects.create(
            username="recipient",
            password="testpass",
            email="recipient@example.com",
        )

    def test_insufficient_funds_shows_error(self):
        self.wallet.balance = Decimal('10.00')
        self.wallet.save()
        recipient_wallet = self.create_wallet(
            user=self.recipient,
            currency=self.currency,
        )

        url = reverse('transfer_funds')
        response = self.client.post(url, {
            'sender_wallet': self.wallet.id,
            'recipient': self.recipient.username,
            'recipient_wallet': recipient_wallet.id,
            'amount': '100.00',
            'note': 'Too much',
        }, follow=True)

        self.assertContains(response, 'Insufficient funds.')