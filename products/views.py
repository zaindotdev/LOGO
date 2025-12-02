from django.shortcuts import render, get_object_or_404
from .models import Product

def product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    related_products = Product.objects.filter(categories__in=product.categories.all()).exclude(slug=slug).distinct()[:4]
    return render(request, 'product.html', {
        'product': product,
        'related_products': related_products
    })
