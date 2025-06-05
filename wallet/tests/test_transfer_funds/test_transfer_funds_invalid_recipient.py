from wallet.tests.base import WalletTestCase
from django.urls import reverse


class TransferFundsInvalidRecipientTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_transfer_invalid_recipient_show_error(self):
        url = reverse('transfer_funds')
        response = self.client.post(url, {
            'sender_wallet': self.wallet.id,
            'recipient': 'non_existing_user',
            'recipient_wallet': self.wallet.id,
            'amount': '10.00',
            'note': 'Invalid recipient test'
        }, follow=True)

        self.assertContains(response, 'Recipient not found.')
