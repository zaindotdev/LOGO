from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path("add/<int:id>/", views.cart_add, name="cart_add"),
    path('update/', views.update_cart_item, name='update_cart_item'),
    path("", views.cart_view, name="cart_view"),
    path("remove/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
]
