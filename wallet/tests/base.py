from django.test import TestCase
from wallet.models import User, Wallet, Currency
import uuid


class WalletTestCase(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(
            code='USD',
            name="US Dollar",
            symbol="$",
        )

        self.user = self.create_user()
        self.wallet = Wallet.objects.create(
            user=self.user,
            currency=self.currency,
            balance=100.00,
        )

        self.client.login(username='new_user', password='userP@ssw0rd')

    def create_user(self, username=None, email=None, phone_number=None, password='userP@ssw0rd', is_active=True, is_staff=True):
        uid = uuid.uuid4().hex[:6]
        username = username or f'inactive_user_{uid}'
        email = email or f'inactive_{uid}@example.com'
        phone_number = phone_number or f'123456{uid}'
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            is_active=is_active,
        )
        user.is_staff = is_staff
        user.save()
        return user

    def create_inactive_user(self):
        return self.create_user(is_active=False)

    def create_wallet(self, user=None, currency=None, balance=0):
        if not user:
            user=self.user
        if not currency:
            currency=self.currency
        return Wallet.objects.create(
            user=user,
            currency=currency,
            balance=balance,
        )

    def create_currency(self, code, name=''):
        return Currency.objects.create(
            code=code,
            name=name or code
        )