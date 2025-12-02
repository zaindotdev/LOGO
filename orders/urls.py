from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create-checkout-session/<int:cart_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
]
