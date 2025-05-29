import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Currency(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
    )
    name = models.CharField(
        max_length=100,
    )
    symbol = models.CharField(
        max_length=5,
        default='$',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

class User(AbstractUser):
    email_verified = models.BooleanField(
        default=False,
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True
    )
    phone_verified = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.username


class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallets',
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.user.username}'s {self.currency.code} Wallet: ${self.balance}"

    def deposit(self, amount):
        self.balance += Decimal(amount)
        self.save()

    def withdraw(self, amount):
        if self.balance >= Decimal(amount):
            self.balance -= Decimal(amount)
            self.save()
            return True
        return False

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('ADD', 'Add Funds'),
        ('WITHDRAW', 'Withdraw Funds'),
        ('TRANSFER', 'Transfer Funds'),
        ('RECEIVE', 'Receive Funds'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('FLAGGED', 'Flagged'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transaction_sent',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transaction_received',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    transaction_type = models.CharField(
        max_length=15,
        choices=TRANSACTION_TYPE_CHOICES,
    )
    note = models.TextField(
        blank=True,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='COMPLETED',
    )
    flagged = models.BooleanField(
        default=False,
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} of ${self.amount} on {self.timestamp.strftime('%Y-%m-%d')}"

    def mark_flagged(self, reason=None):
        self.flagged = True
        self.status = 'FLAGGED'
        if reason:
            self.note += f"\n[Flagged {reason}]"
        self.save()

    def mark_complete(self):
        self.status = 'COMPLETED'
        self.save()

