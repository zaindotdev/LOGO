from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path("profile/", views.profile, name="profile"),
    path('address/', views.address_view, name='address_view'),
    path('save-address/', views.save_address, name='save_address'),
]
