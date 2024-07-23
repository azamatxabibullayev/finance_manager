from django.shortcuts import render, redirect
from .models import Income, Expense, Transaction, Balance, Currency, CurrencyType
from .forms import IncomeForm, ExpenseForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
import calendar
from django.db.models import Sum
from django.utils import timezone
import json


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    balance_cash = Balance.objects.filter(
        user=request.user, currency__type__type=CurrencyType.CASH
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    balance_card = Balance.objects.filter(
        user=request.user, currency__type__type=CurrencyType.CARD
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00
    overall_balance = balance_cash + balance_card

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

    weekly_expenses = \
        Expense.objects.filter(user=request.user, date__range=[start_week, end_week]).aggregate(Sum('amount'))[
            'amount__sum'] or 0.00
    monthly_expenses = Expense.objects.filter(user=request.user, date__month=today.month).aggregate(Sum('amount'))[
                           'amount__sum'] or 0.00
    yearly_expenses = Expense.objects.filter(user=request.user, date__year=today.year).aggregate(Sum('amount'))[
                          'amount__sum'] or 0.00

    incomes_last_12_months = [0] * 12
    expenses_last_12_months = [0] * 12

    for i in range(12):
        month = (today.month - i - 1) % 12 + 1
        year = today.year if today.month - i > 0 else today.year - 1
        monthly_income = \
            Income.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(Sum('amount'))[
                'amount__sum'] or 0.00
        monthly_expense = \
            Expense.objects.filter(user=request.user, date__year=year, date__month=month).aggregate(Sum('amount'))[
                'amount__sum'] or 0.00
        incomes_last_12_months[11 - i] = monthly_income
        expenses_last_12_months[11 - i] = monthly_expense

    context = {
        'transactions': transactions,
        'balance_cash': balance_cash,
        'balance_card': balance_card,
        'overall_balance': overall_balance,
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
            Balance.objects.create(user=request.user, amount=income.amount, date=income.date, currency=income.currency)
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
            Balance.objects.create(user=request.user, amount=-expense.amount, date=expense.date,
                                   currency=expense.currency)
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
    incomes_by_type = incomes.values('income_type__name').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'incomes': incomes,
        'total_income': total_income,
        'period': period,
        'incomes_by_type': incomes_by_type,
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
    expenses_by_type = expenses.values('expense_type__name').annotate(total=Sum('amount')).order_by('-total')
    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'period': period,
        'expenses_by_type': expenses_by_type,
    }
    return render(request, 'main/expense_stats.html', context)


@login_required
def stats(request):
    selected_date_str = request.GET.get('date')
    selected_date = None
    incomes = []
    expenses = []

    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
            incomes = Income.objects.filter(user=request.user, date=selected_date).select_related('income_type',
                                                                                                  'currency')
            expenses = Expense.objects.filter(user=request.user, date=selected_date).select_related('expense_type',
                                                                                                    'currency')
        except ValueError:
            pass

    context = {
        'selected_date': selected_date_str,
        'incomes': incomes,
        'expenses': expenses,
    }
    return render(request, 'main/stats.html', context)
