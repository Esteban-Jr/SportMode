from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/edit/', views.edit_product, name='edit_product'),
    path('<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('<slug:slug>/reviews/add/', views.add_review, name='add_review'),
    path(
        '<slug:slug>/reviews/<int:review_id>/edit/',
        views.edit_review,
        name='edit_review',
    ),
    path(
        '<slug:slug>/reviews/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review',
    ),
]
