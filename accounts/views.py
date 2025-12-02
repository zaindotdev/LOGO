from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegisterForm
from django.core.mail import send_mail
from django.conf import settings
from .models import Address, Profile
from orders.models import Order


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            
            try:
                send_mail(
                    subject='Welcome to LOGO Store!',
                    message=f'Hi {user.username},\n\nThank you for registering at LOGO Store!\n\nWe\'re excited to have you with us. Start exploring our products and enjoy shopping!\n\nBest regards,\nLOGO Store Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send registration email: {e}")
            
            login(request, user)
            Profile.objects.filter(user=user).update(email=email)
            return redirect('pages:home')
    else:
        form = RegisterForm()
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
    logout(request)
    return redirect('pages:home')

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

        profile = Profile.objects.get(user=request.user)
        profile.phone = phone_number
        profile.save()

        # If user came from cart checkout and just set their first address, redirect to checkout
        if from_url == 'cart' or (no_default_before and from_url == 'cart'):
            return redirect('orders:checkout')
        return redirect('accounts:address_view')

    return render(request, 'address.html')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items', 'items__product', 'items__variant')
    return render(request, 'profile.html', {'orders': orders})