from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser


class CurrencyType(models.Model):
    CASH = 'CASH'
    CARD = 'CARD'

    CURRENCY_CHOICES = [
        (CASH, 'Cash'),
        (CARD, 'Card'),
    ]

    type = models.CharField(
        max_length=4,
        choices=CURRENCY_CHOICES,
        default=CASH
    )

    def __str__(self):
        return dict(self.CURRENCY_CHOICES).get(self.type, 'Unknown')


class Currency(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(CurrencyType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


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


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('outcome', 'Outcome'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError('Amount must be positive')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.transaction_type == 'outcome':
            Balance.objects.create(user=self.user, amount=-self.amount, date=self.date, currency=self.currency)
        elif self.transaction_type == 'income':
            Balance.objects.create(user=self.user, amount=self.amount, date=self.date, currency=self.currency)


class Balance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
