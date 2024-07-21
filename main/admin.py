from django.contrib import admin
from .models import Currency, IncomeType, ExpenseType, Income, Expense

# Register your models here.


admin.site.register(Currency)
admin.site.register(IncomeType)
admin.site.register(ExpenseType)
admin.site.register(Income)
admin.site.register(Expense)
