from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order


# Create your views here.
@login_required
def checkout(request):
    return render(request, 'checkout.html')