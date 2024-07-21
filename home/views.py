from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

def landing_page(request):
    return render(request, 'landing_page.html')
