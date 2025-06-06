from wallet.models import Currency, Wallet
from wallet.tests.base import WalletTestCase

from django.urls import reverse

class EditProfileInvalidDataFailsTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.account_url = reverse('account_settings')

    def test_edit_profile_invalid_data_fails(self):
        original_email = self.user.email

        response = self.client.post(self.account_url, {
            'edit_profile': '1',
            'email': 'invalid_email',
            'phone_number': self.user.phone_number,
        })

        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address.', form.errors['email'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)