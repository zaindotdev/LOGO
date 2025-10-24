from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('<str:slug>/', views.product, name='product'),
]
