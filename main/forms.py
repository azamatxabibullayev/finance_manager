from django import forms
from .models import Income, Expense, Transaction


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date', 'description', 'currency', 'income_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'description', 'currency', 'expense_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'date', 'currency', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
