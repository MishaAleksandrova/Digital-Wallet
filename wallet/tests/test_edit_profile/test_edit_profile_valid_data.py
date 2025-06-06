from wallet.models import Currency, Wallet
from wallet.tests.base import WalletTestCase

from django.urls import reverse

class EditProfileValidDataTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.account_url = reverse('account_settings')

    def test_edit_profile_valid_data(self):
        new_email = 'new_user@example.com'
        new_phone = '1234567899'

        response = self.client.post(self.account_url, {
            'edit_profile': '1',
            'email': new_email,
            'phone_number': new_phone,
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)
        self.assertEqual(self.user.phone_number, new_phone)