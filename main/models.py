from django.db import models
from django.conf import settings


class Currency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class IncomeType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ExpenseType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    income_type = models.ForeignKey(IncomeType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.amount} {self.currency} on {self.date}"


class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.amount} {self.currency} on {self.date}"
