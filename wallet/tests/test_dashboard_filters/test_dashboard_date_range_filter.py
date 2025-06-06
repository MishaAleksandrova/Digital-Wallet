from datetime import timedelta
from django.utils import timezone
from wallet.models import Transaction
from wallet.tests.base import WalletTestCase


class DashboardDateRangeFilterTest(WalletTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

        self.older_transaction = Transaction.objects.create(
            sender=self.user,
            receiver=None,
            amount=10.00,
            transaction_type='WITHDRAW',
            timestamp=timezone.now() - timedelta(days=10),
        )
        self.recent_transaction = Transaction.objects.create(
            sender=self.user,
            receiver=None,
            amount=20.00,
            transaction_type='WITHDRAW',
            timestamp=timezone.now() - timedelta(days=2),
        )

    def test_filter_by_date_range(self):
        start_date = (timezone.now() - timedelta(days=5)).date()
        end_date = timezone.now().date()

        response = self.client.get('/dashboard/', {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.recent_transaction.amount))
        self.assertNotContains(response, str(self.older_transaction.amount))