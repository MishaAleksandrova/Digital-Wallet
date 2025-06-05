from decimal import Decimal
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_GET

from .forms import RegisterForm, AddFundsForm, WithdrawFundsForm, AddWalletForm, EditProfileForm, TransferFundsForm
from .models import User, Wallet, Transaction
from django.db.models import Q
from .utils import generate_email_token, verify_email_token, get_exchange_rate
from django.utils.dateparse import parse_date


@login_required
def dashboard_view(request):
    wallets = Wallet.objects.filter(user=request.user)
    selected_wallet_id = request.GET.get('wallet')

    wallet = None
    if selected_wallet_id:
        wallet = wallets.filter(id=selected_wallet_id).first()
    else:
        wallet = wallets.first()

    if request.user.is_superuser:
        transactions = Transaction.objects.all()
        if wallet:
            transactions = transactions.filter(
                Q(sender=wallet.user) |
                Q(receiver=wallet.user)
            )
    else:
        base_filter = Q(sender=request.user) | Q(receiver=request.user)
        transactions = Transaction.objects.filter(base_filter)

        if wallet:
            wallet_user_filter = Q(sender=wallet.user) | Q(receiver=wallet.user)
            transactions = transactions.filter(wallet_user_filter)

    selected_type = request.GET.get('type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if selected_type:
        transactions = transactions.filter(transaction_type=selected_type)

    if start_date:
        start = parse_date(start_date)
        if start:
            transactions = transactions.filter(timestamp__date__gte=start)

    if end_date:
        end = parse_date(end_date)
        if end:
            transactions = transactions.filter(timestamp__date__lte=end)

    transactions = transactions.order_by('-timestamp')[:10]

    context = {
        'wallet': wallet,
        'wallets': wallets,
        'transactions': transactions,
        'selected_type': selected_type,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'wallet/dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            currency = form.cleaned_data['currency']
            Wallet.objects.create(user=user, currency=currency)

            token = generate_email_token(user.email)
            verify_link = request.build_absolute_uri(f"/verify-email/?token={token}")

            send_mail(
                'Verify Email',
                f'Click the link to verify: {verify_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            return render(request, 'wallet/verify_prompt.html')
    else:
        form = RegisterForm()
    return render(request, 'wallet/register.html', {'form': form})

def verify_email_view(request):
    token = request.GET.get('token')
    email = verify_email_token(token)

    if email:
        try:
            user = User.objects.get(email=email)
            user.email_verified = True
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('wallet_dashboard')
        except User.DoesNotExist:
            return render(request, 'wallet/verify_failed.html')
    return render(request, 'wallet/verify_failed.html')


@require_GET
@staff_member_required
def get_wallets(request):
    user_id = request.GET.get('user_id')
    wallets = []

    if user_id:
        user = get_object_or_404(User, id=user_id)
        wallets_qs = Wallet.objects.filter(user=user)
        wallets = [{
            'id': w.id,
            'label': f"{w.currency.code} = {w.balance}"
        }
            for w in wallets_qs
        ]
    return JsonResponse({'wallets': wallets})


@staff_member_required
def add_funds_view(request):
    selected_user_id = request.GET.get('user')
    user_selected = None

    if selected_user_id:
        user_selected = get_object_or_404(User, id=selected_user_id)

    if request.method == 'POST':
        form = AddFundsForm(request.POST, user_selected=request.POST.get('user'))
        if form.is_valid():
            wallet = form.cleaned_data['wallet']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data['note']

            wallet.deposit(amount)

            Transaction.objects.create(
                sender=None,
                receiver=wallet.user,
                amount=amount,
                transaction_type='ADD',
                note= note or f"Funds added by admin {request.user.username}"
            )
            messages.success(request, f"{amount} added to {wallet.user.username}`s wallet.")
            return redirect('wallet_dashboard')
    else:
        form = AddFundsForm(user_selected=user_selected )
    return render(request, 'wallet/add_funds.html', {'form': form})

@login_required
def withdraw_funds_view(request):
    form = WithdrawFundsForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        wallet = form.cleaned_data['wallet']
        amount = form.cleaned_data['amount']

        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()

            Transaction.objects.create(
                sender=request.user,
                receiver=None,
                amount=amount,
                transaction_type='WITHDRAW',
            )
            messages.success(request, f"{amount} withdrawn successfully from {wallet.currency.code} wallet.")
            return redirect('wallet_dashboard')
        else:
            messages.error(request, "Insufficient funds.")
    selected_wallet_id = request.POST.get('wallet') if request.method == 'POST' else None
    wallet_choices = [
        {
            'id': str(wallet.id),
            'label': f"{wallet.currency.code} - {wallet.balance}",
            'selected': str(wallet.id) == selected_wallet_id,
        }
        for wallet in form.fields['wallet'].queryset
    ]
    return render(request, 'wallet/withdraw.html', {'form': form, 'wallet_choices': wallet_choices})


@require_GET
def get_recipient_wallets(request):
    username = request.GET.get('username')
    data = {'wallets': []}

    try:
        recipient = User.objects.get(username__iexact=username)
        wallets = Wallet.objects.filter(user=recipient)

        data['wallets'] = [
            {
                'id': wallet.id,
                'currency': wallet.currency.code,
                'balance': str(wallet.balance),
            }
            for wallet in wallets
        ]
    except User.DoesNotExist:
        data['error'] = 'User not found'

    return JsonResponse(data)


@login_required
def transfer_funds_view(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        username = post_data.get('recipient')
        try:
            recipient = User.objects.get(username=username)
            post_data['recipient'] = recipient.id
        except User.DoesNotExist:
            messages.error(request, "Recipient not found.")
            form = TransferFundsForm(post_data, user=request.user)
            return render(request, 'wallet/transfer_funds.html', {'form': form})

        form = TransferFundsForm(post_data, user=request.user)
        if form.is_valid():
            sender_wallet = form.cleaned_data['sender_wallet']
            recipient = form.cleaned_data['recipient']
            recipient_wallet = form.cleaned_data['recipient_wallet']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data['note']

            if sender_wallet.user != request.user:
                messages.error(request, "Invalid sender wallet.")
                return redirect('transfer_funds')

            if sender_wallet.balance < amount:
                messages.error(request, "Insufficient funds.")
                return redirect('transfer_funds')

            if sender_wallet.currency == recipient_wallet.currency:
                converted_amount = amount
            else:
                rate = get_exchange_rate(sender_wallet.currency.code, recipient_wallet.currency.code)
                if not rate:
                    messages.error(request, "Currency conversion failed.")
                    return redirect('transfer_funds')
                converted_amount = amount * Decimal(str(rate))

            sender_wallet.balance -= amount
            sender_wallet.save()

            recipient_wallet.balance += converted_amount
            recipient_wallet.save()

            Transaction.objects.create(
                sender=request.user,
                receiver=recipient,
                amount=amount,
                transaction_type='TRANSFER',
                note=f"{note} | Converted to {converted_amount:.2f} {recipient_wallet.currency.code}" if sender_wallet.currency != recipient_wallet.currency else note,
            )

            messages.success(request, f"Transferred {amount:.2f} {sender_wallet.currency.code} to {recipient.username}."
                             f"({converted_amount:.2f} {recipient_wallet.currency.code})."
                             )
            return redirect('wallet_dashboard')
    else:
        form = TransferFundsForm(user=request.user)

    return render(request, 'wallet/transfer_funds.html', {'form': form})


@login_required
def account_view(request):
    user = request.user
    wallets = Wallet.objects.filter(user=user)

    if request.method == 'POST':
        wallet_form = AddWalletForm(request.POST)
        profile_form = EditProfileForm(
            request.POST or None,
            instance=request.user,
        )

        if 'add_wallet' in request.POST:
            wallet_form = AddWalletForm(request.POST)
            if wallet_form.is_valid():
                currency = wallet_form.cleaned_data['currency']
                if not wallets.filter(currency=currency).exists():
                    Wallet.objects.create(user=user, currency=currency)
                    messages.success(request, f"Wallet in {currency.code} added.")
                else:
                    messages.error(request, f"Wallet in {currency.code} already exists.")
                return redirect('account_settings')

        elif 'edit_profile' in request.POST:
            profile_form = EditProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, f"Profile updated.")
                return redirect('account_settings')

        elif 'delete_wallet' in request.POST:
            wallet_id = request.POST.get('wallet_id')
            wallet = get_object_or_404(Wallet, id=wallet_id, user=user)
            if wallet.balance == 0:
                wallet.delete()
                messages.success(request, f"{wallet.currency.code} wallet deleted.")
            else:
                messages.error(request, "You can only delete empty wallets.")
            return redirect('account_settings')
    else:
        wallet_form = AddWalletForm()
        profile_form = EditProfileForm(instance=user)

    context = {
        'wallet_form': wallet_form,
        'profile_form': profile_form,
        'wallets': wallets,
    }
    return render(request, 'wallet/account.html', context)