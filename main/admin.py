from django.contrib import admin
from .models import Currency, IncomeType, ExpenseType, Income, Expense, CurrencyType, Transaction, Balance

# Register your models here.


admin.site.register(Currency)
admin.site.register(IncomeType)
admin.site.register(ExpenseType)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(CurrencyType)
admin.site.register(Transaction)
admin.site.register(Balance)
