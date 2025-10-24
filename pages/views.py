from django.shortcuts import render
from products.models import Product

# Create your views here.
def home(request):
    new_in = Product.objects.filter(categories__slug='new-in')
    men = Product.objects.filter(categories__slug='men')
    women = Product.objects.filter(categories__slug='women')
    return render(request, 'home.html',{
        'new_in': new_in,
        'men': men,
        'women': women,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def products(request,category):
    products = Product.objects.filter(categories__slug=category).order_by('-created_at')
    return render(request, 'products.html', {'products': products})