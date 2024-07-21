from django.shortcuts import render, redirect
from .models import Income, Expense, IncomeType, ExpenseType, Currency
from .forms import IncomeForm, ExpenseForm
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    context = {
        'incomes': incomes,
        'expenses': expenses,
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
