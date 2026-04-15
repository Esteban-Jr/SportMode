from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('orders/<order_number>/', views.order_detail, name='order_detail'),
]
