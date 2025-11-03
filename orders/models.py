from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant
from accounts.models import Address

class Order(models.Model):
    STATUS_CHOICES = [
        ('created','Created'),
        ('paid','Paid'),
        ('shipped','Shipped'),
        ('cancelled','Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_intent = models.CharField(max_length=255, blank=True, null=True)  # for stripe

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
