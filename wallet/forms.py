from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Currency, Wallet


class RegisterForm(UserCreationForm):
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        required=True,
        label="Preferred Currency",
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
            'currency',
        ]
        help_texts = {
            'username': "Letters, digits and @/./+/-/_ only.",
            'password1': "Your password must contain at least 8 characters.",
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        return user


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'email',
            'phone_number',
        ]


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['email'].required = False
        self.fields['phone_number'].required = False

        if self.instance:
            email_placeholder = self.instance.email if self.instance.email else ''
            phone_placeholder = self.instance.phone_number if self.instance.phone_number else ''

            self.fields['email'].widget.attrs['placeholder'] = email_placeholder
            self.fields['phone_number'].widget.attrs['placeholder'] = phone_placeholder


class AddWalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = [
            'currency',
        ]


class AddFundsForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Select User"
    )
    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        label="Select Wallet",
        required=True,
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    note = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user_selected', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user)
        else:
            self.fields['wallet'].queryset = Wallet.objects.none()

class WithdrawFundsForm(forms.Form):
    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        label="Select Wallet",
        required=True,
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user)
            self.fields['wallet'].label_form_istance = self.wallet_label_from_instance

    def wallet_label_from_instance(self, obj):
        return f"{obj.currency.code} - {obj.balance}"


class TransferFundsForm(forms.Form):
    sender_wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        label="From Your Wallet",

    )
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Recipient",
    )
    recipient_wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        label="Recipient Wallet",
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['sender_wallet'].queryset = Wallet.objects.filter(user=user)
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)

        if 'recipient' in self.data:
            try:
                recipient_id = int(self.data.get('recipient'))
                self.fields['recipient_wallet'].queryset = Wallet.objects.filter(user_id=recipient_id)
            except (ValueError, TypeError):
                pass



