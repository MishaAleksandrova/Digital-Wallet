from wallet.models import Wallet, Transaction
from wallet.tests.base import WalletTestCase


class DashboardUserAccessTest(WalletTestCase):
    def setUp(self):
        super().setUp()

        self.admin_user = self.create_user(
            username='admin_user',
            is_staff=True,
        )
        self.admin_user.is_superuser = True
        self.admin_user.save()

        self.user2 = self.create_user(
            username='other_user',
        )
        self.wallet2= self.create_wallet(
            user=self.user2,
            balance=200
        )

        self.transaction = Transaction.objects.create(
            sender=self.user,
            receiver=self.user2,
            amount=100,
            transaction_type='TRANSFER'
        )

    def test_regular_user_sees_own_transactions(self):
        self.client.force_login(self.user)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.transaction.amount))

    def test_admin_user_sees_all_transactions(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.transaction.amount))