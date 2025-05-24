from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Wallet, Transaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'is_active',
        'is_staff',
        'email_verified',
    )
    search_fields = (
        'username',
        'email'
    )
    list_filter = (
        'is_active',
        'email_verified',
        'is_staff',
        'is_superuser',
    )
    ordering = (
        'date_joined',
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('email_verified',)}),
    )

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'balance',
    )
    search_fields = (
        'user__username',
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'sender',
        'receiver',
        'amount',
        'transaction_type',
        'status',
        'created_at',
    )
    list_filter = (
        'transaction_type',
        'status',
        'created_at',
    )
    search_fields = (
        'sender__username',
        'recipient__username',
    )