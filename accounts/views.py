from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Address, Profile
from orders.models import Order

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pages:home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('pages:home')
    return render(request, 'login.html', {'form': AuthenticationForm()})

def logout_view(request):
    if request.method == 'POST':
        logout(request, locals=True)
        return redirect('pages:home')
    return redirect('accounts:profile')

@login_required
def address_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'address.html', {'addresses': addresses})


@login_required
def save_address(request):
    from_url = request.GET.get('from')
    if request.method == 'POST':
        line1 = request.POST.get('address_line1')
        line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')

        # If no default address exists, make this one default
        no_default_before = not Address.objects.filter(user=request.user, default=True).exists()
        is_default = no_default_before

        Address.objects.create(
            user=request.user,
            line1=line1,
            line2=line2,
            city=city,
            postal_code=postal_code,
            country=country,
            default=is_default,
        )

        Profile.objects.create(
            user = request.user,
            phone_number = phone_number
        )

        # If user came from cart checkout and just set their first address, redirect to checkout
        if from_url == 'cart' or (no_default_before and from_url == 'cart'):
            return redirect('orders:checkout')
        return redirect('accounts:address_view')

    return render(request, 'address.html')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items', 'items__product', 'items__variant')
    return render(request, 'profile.html', {'orders': orders})