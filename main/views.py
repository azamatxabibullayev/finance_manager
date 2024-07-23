from django.shortcuts import render, redirect
from .models import Income, Expense, Transaction, Balance
from .forms import IncomeForm, ExpenseForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
import calendar
from django.db.models import Sum
from django.utils import timezone
import json
from decimal import Decimal


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

    # Calculate expenses
    weekly_expenses = \
        Expense.objects.filter(user=request.user, date__range=[start_week, end_week]).aggregate(Sum('amount'))[
            'amount__sum'] or 0.00
    monthly_expenses = Expense.objects.filter(user=request.user, date__month=today.month).aggregate(Sum('amount'))[
                           'amount__sum'] or 0.00
    yearly_expenses = Expense.objects.filter(user=request.user, date__year=today.year).aggregate(Sum('amount'))[
                          'amount__sum'] or 0.00

    # Get data for the past 12 months
    incomes_last_12_months = []
    expenses_last_12_months = []
    for i in range(12):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        monthly_income = \
            Income.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(Sum('amount'))[
                'amount__sum'] or 0.00
        monthly_expense = \
            Expense.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(Sum('amount'))[
                'amount__sum'] or 0.00
        incomes_last_12_months.append(monthly_income)
        expenses_last_12_months.append(monthly_expense)

    incomes_last_12_months.reverse()
    expenses_last_12_months.reverse()

    context = {
        'transactions': transactions,
        'balance': balance,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
        'weekly_expenses': weekly_expenses,
        'monthly_expenses': monthly_expenses,
        'yearly_expenses': yearly_expenses,
        'incomes_last_12_months': json.dumps(incomes_last_12_months),
        'expenses_last_12_months': json.dumps(expenses_last_12_months),
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
def income_stats(request, period):
    today = timezone.now().date()
    if period == 'weekly':
        start_period = today - timedelta(days=today.weekday())
        end_period = start_period + timedelta(days=6)
    elif period == 'monthly':
        start_period = today.replace(day=1)
        end_period = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif period == 'yearly':
        start_period = today.replace(month=1, day=1)
        end_period = today.replace(month=12, day=31)
    else:
        return redirect('dashboard')

    incomes = Income.objects.filter(user=request.user, date__range=[start_period, end_period])
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'incomes': incomes,
        'total_income': total_income,
        'period': period,
    }
    return render(request, 'main/income_stats.html', context)


@login_required
def expense_stats(request, period):
    today = timezone.now().date()
    if period == 'weekly':
        start_period = today - timedelta(days=today.weekday())
        end_period = start_period + timedelta(days=6)
    elif period == 'monthly':
        start_period = today.replace(day=1)
        end_period = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif period == 'yearly':
        start_period = today.replace(month=1, day=1)
        end_period = today.replace(month=12, day=31)
    else:
        return redirect('dashboard')

    expenses = Expense.objects.filter(user=request.user, date__range=[start_period, end_period])
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'period': period,
    }
    return render(request, 'main/expense_stats.html', context)
