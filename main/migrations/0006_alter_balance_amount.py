# Generated by Django 5.0.7 on 2024-07-23 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_expense_amount_alter_income_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='amount',
            field=models.IntegerField(),
        ),
    ]
