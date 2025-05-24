from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
        ]
        help_texts = {
            'username': "Letters, digits and @/./+/-/_ only.",
            'password1': "Your password must contain at least 8 characters.",
        }

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