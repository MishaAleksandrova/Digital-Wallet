from decimal import Decimal
import requests
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_GET

from .forms import RegisterForm, AddFundsForm, WithdrawFundsForm, AddWalletForm, EditProfileForm
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
                Q(sender__wallet__id=wallet.id) |
                Q(receiver__wallet__id=wallet.id)
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

    #Get wallet currency and calculate exchange to EUR for display
    # convert_balance = None
    # target_currency_code = 'EUR'
    #
    # if wallet and wallet.currency.code != target_currency_code:
    #     exchange_rate = get_exchange_rate(wallet.currency.code, target_currency_code)
    #     if exchange_rate:
    #         convert_balance = wallet.balance * Decimal(str(exchange_rate))

    context = {
        'wallet': wallet,
        'wallets': wallets,
        # 'converted_balance': convert_balance,
        # 'target_currency_code': target_currency_code,
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
    return render(request, 'verify_failed.html')


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
    form = WithdrawFundsForm(request.POST or None)
    if form.is_valid():
        wallet = request.user.wallet
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
            messages.success(request, f"{amount} withdrawn successfully.")
            return redirect('wallet_dashboard')
        else:
            messages.error(request, "Insufficient funds.")
    return render(request, 'wallet/withdraw.html', {'form': form})

@login_required
def transfer_funds_view(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        amount = request.POST.get('amount')
        note = request.POST.get('note', '')

        if not recipient_username or not amount:
            messages.error(request, "Recipient and amount are required.")
            return redirect('transfer_funds')

        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            messages.error(request, "Recipient user not found.")
            return redirect('transfer_funds')

        if recipient == request.user:
            messages.error(request, "You cannot transfer to yourself.")
            return redirect('transfer_funds')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount.")
            return redirect('transfer_funds')

        sender_wallet = Wallet.objects.get(user=request.user)
        recipient_wallet = Wallet.objects.get(user=recipient)

        if sender_wallet.balance < amount:
            messages.error(request, "Insufficient funds.")
            return redirect('transfer_funds')

        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        sender_wallet.save()
        recipient_wallet.save()

        Transaction.objects.create(
            sender=request.user,
            receiver=recipient,
            amount=amount,
            transaction_type='TRANSFER',
            note=note,
        )

        messages.success(request, f"Transferred ${amount} to {recipient.username}.")
        return redirect('wallet_dashboard')

    return render(request, 'wallet/transfer_funds.html')


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