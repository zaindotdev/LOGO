import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from cart.models import Cart
from .models import Order, OrderItem
from accounts.models import Address

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    return render(request, "checkout.html")


@login_required
def create_checkout_session(request, cart_id):
    address = Address.objects.filter(user=request.user, default=True).first()
    print("Default address:", address)
    if not address:
        return JsonResponse({
            "error": "Please add a shipping address before checkout.",
            "redirect": "/accounts/address/"
        }, status=400)

    if request.method == "POST":
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
                full_name=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                address=address,
                total=total_amount,
                payment_id=session.id,
                payment_intent=session.payment_intent,
                status="created",
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
            print("Stripe Error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def stripe_webhook(request):
    print("=" * 80)
    print("WEBHOOK ENDPOINT HIT!")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print("=" * 80)
    
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        print("Webhook ValueError:", str(e))
        return JsonResponse({"error": str(e)}, status=400)

    print("Stripe Webhook received:", event.type)
    
    if event.type == "checkout.session.completed":
        session = event.data.object
        session_id = session.id
        payment_intent = session.payment_intent
        
        print("Session ID:", session_id)
        print("Payment Intent:", payment_intent)
        
        try:
            order = Order.objects.get(payment_id=session_id)
            print(f"Found order: {order.id}, current status: {order.status}, current payment_intent: {order.payment_intent}")
            
            order.payment_intent = payment_intent
            order.status = "paid"
            order.save()
            
            print(f"Order {order.id} updated - new status: {order.status}, new payment_intent: {order.payment_intent}")
            
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                order_items = order.items.all()
                items_text = '\n'.join([
                    f"- {item.product.title} x {item.quantity} - Rs. {item.price * item.quantity}"
                    for item in order_items
                ])
                
                send_mail(
                    subject=f'Order Confirmation - #{order.id}',
                    message=f'''Hi {order.full_name},

Thank you for your order!

Order ID: #{order.id}
Order Total: Rs. {order.total}

Items:
{items_text}

Shipping Address:
{order.address.line1}
{order.address.line2 if order.address.line2 else ''}
{order.address.city}, {order.address.postal_code}
{order.address.country}

We'll send you another email when your order ships.

Best regards,
LOGO Store Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    fail_silently=True,
                )
                print(f"Order confirmation email sent to {order.email}")
            except Exception as e:
                print(f"Failed to send order confirmation email: {e}")
            
        except Order.DoesNotExist:
            print(f"ERROR: No order found with payment_id={session_id}")
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            print(f"ERROR updating order: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"status": "success"})


@login_required
def success(request):
    # Update the most recent pending order to paid status
    latest_order = Order.objects.filter(
        user=request.user, 
        status='created'
    ).order_by('-created_at').first()
    
    if latest_order:
        latest_order.status = 'paid'
        latest_order.save()
        print(f"Order {latest_order.id} marked as paid")
        
        # Send order confirmation email
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            order_items = latest_order.items.all()
            items_text = '\n'.join([
                f"- {item.product.title} x {item.quantity} - Rs. {item.price * item.quantity}"
                for item in order_items
            ])
            
            send_mail(
                subject=f'Order Confirmation - #{latest_order.id}',
                message=f'''Hi {latest_order.full_name},

Thank you for your order!

Order ID: #{latest_order.id}
Order Total: Rs. {latest_order.total}

Items:
{items_text}

Shipping Address:
{latest_order.address.line1}
{latest_order.address.line2 if latest_order.address.line2 else ''}
{latest_order.address.city}, {latest_order.address.postal_code}
{latest_order.address.country}

We'll send you another email when your order ships.

Best regards,
LOGO Store Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[latest_order.email],
                fail_silently=True,
            )
            print(f"Order confirmation email sent to {latest_order.email}")
        except Exception as e:
            print(f"Failed to send order confirmation email: {e}")
    
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
