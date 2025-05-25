from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm, AddFundsForm, WithdrawFundsForm
from .models import User, Wallet, Transaction
from django.db.models import Q
from .utils import generate_email_token, verify_email_token
from django.utils.dateparse import parse_date


@login_required
def dashboard_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.user.is_superuser:
        transactions = Transaction.objects.all()
    else:
        base_filter = Q(sender=request.user) | Q(receiver=request.user)
        add_funds_filter = Q(transaction_type='ADD', receiver=request.user)
        transactions = Transaction.objects.filter(base_filter | add_funds_filter).distinct()

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

@staff_member_required

def add_funds_view(request):
    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data['note']

            wallet,_ = Wallet.objects.get_or_create(user=user)
            wallet.deposit(amount)

            Transaction.objects.create(
                sender=None,
                receiver=user,
                amount=amount,
                transaction_type='ADD',
                note= note or f"Funds added by admin {request.user.username}"
            )
            messages.success(request, f"{amount} added to {user.username}`s wallet.")
            return redirect('wallet_dashboard')
    else:
        form = AddFundsForm()
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