from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from products.models import Product


@login_required
def cart_add(request, id):
    """Add a product to the user's cart."""
    product = get_object_or_404(Product, pk=id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If already in cart, increase quantity by 1
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_view')


@require_POST
@login_required
def update_cart_item(request):
    """Update quantity of a cart item and return updated totals."""
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')

    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.quantity = int(quantity)
        item.save()

        subtotal = sum(i.total_price for i in item.cart.items.all())

        return JsonResponse({
            'success': True,
            'total_price': item.total_price,  
            'subtotal': subtotal              
        })

    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)


@login_required
def cart_view(request):
    """Display the user's cart with subtotal and items."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    subtotal = sum(i.total_price for i in items)

    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'cart.html', context)


@login_required
def remove_from_cart(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    item.delete()
    return redirect('cart:cart_view')