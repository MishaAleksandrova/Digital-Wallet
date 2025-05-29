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
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    note = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )

class WithdrawFundsForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )

class TransferFundsForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
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



