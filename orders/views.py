import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from cart.models import Cart
from .models import Order, OrderItem
from accounts.models import Address

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    return render(request, "checkout.html")


@login_required
def create_checkout_session(request):

    address = Address.objects.filter(user=request.user, default=True).first()
    if not address:
        return JsonResponse({
            "error": "You must add a shipping address before proceeding to checkout."
        }, status=400)

    if request.method == "POST":
        cart_id = request.POST.get("cart_id")
        cart = get_object_or_404(Cart, id=cart_id)

        try:
            line_items = []
            total_amount = 0

            for item in cart.items.all():
                price = item.product.discounted_price if item.product.on_sale else item.product.price

               
                line_items.append({
                    "price_data": {
                        "currency": "pkr",
                        "product_data": {
                            "name": item.product.title,
                        },
                        "unit_amount": int(price * 100),
                    },
                    "quantity": item.quantity,
                })

                total_amount += price * item.quantity

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri("/orders/success/"),
                cancel_url=request.build_absolute_uri("/orders/cancel/"),
            )

            order = Order.objects.create(
                user=request.user,
                full_name=request.user.get_full_name(),
                email=request.user.email,
                total=total_amount,
                status="created",
                payment_intent=session.payment_intent,
            )

            for item in cart.items.all():
                price = item.product.discounted_price if item.product.on_sale else item.product.price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=price,
                    quantity=item.quantity,
                )

            return JsonResponse({"sessionId": session.id})

        except Exception as e:
            print("❌ Stripe Error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        payment_intent = session.payment_intent
        order = Order.objects.get(payment_intent=payment_intent)
        order.status = "paid"
        order.save()

    return JsonResponse({"status": "success"})


@login_required
def success(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.delete()

    return render(request, "success.html")


@login_required
def cancel(request):
    return render(request, "cancel.html")


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "cancelled"
    order.save()
    return redirect("accounts:profile")
