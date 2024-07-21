from django.shortcuts import render, redirect
from .models import Income, Expense, IncomeType, ExpenseType, Currency, CurrencyType, Transaction, Balance
from .forms import IncomeForm, ExpenseForm, TransactionForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
import calendar
from django.db.models import Sum
from django.utils import timezone


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    balance = Balance.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00

    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    start_month = today.replace(day=1)
    start_year = today.replace(month=1, day=1)

    weekly_transactions = transactions.filter(date__range=[start_week, end_week])
    monthly_transactions = transactions.filter(date__month=today.month)
    yearly_transactions = transactions.filter(date__year=today.year)

    weekly_total = weekly_transactions.aggregate(Sum('amount'))['amount__sum'] or 0.00
    monthly_total = monthly_transactions.aggregate(Sum('amount'))['amount__sum'] or 0.00
    yearly_total = yearly_transactions.aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'transactions': transactions,
        'balance': balance,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
    }
    return render(request, 'main/dashboard.html', context)


@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('dashboard')
    else:
        form = IncomeForm()
    return render(request, 'main/add_income.html', {'form': form})


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'main/add_expense.html', {'form': form})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'main/add_transaction.html', {'form': form})
