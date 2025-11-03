from cart.models import Cart

def cart_counter(request):
    if not request.user.is_authenticated:
        return {'cart_count': 0}

    cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
    if not cart:
        return {'cart_count': 0}

    total_items = sum(item.quantity for item in cart.items.all())
    return {'cart_count': total_items}
