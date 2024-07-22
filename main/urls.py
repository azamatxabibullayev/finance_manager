from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_income/', views.add_income, name='add_income'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('income_stats/<str:period>/', views.income_stats, name='income_stats'),
    path('expense_stats/<str:period>/', views.expense_stats, name='expense_stats'),
]
