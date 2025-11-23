# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ====================== TRANG CHỦ & SẢN PHẨM ======================
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # ====================== BÌNH LUẬN ======================
    path('product/<int:product_id>/comment/add/', views.add_comment, name='add_comment'),
    
    # ====================== GIỎ HÀNG ======================
    path('cart/', views.cart, name='cart'),
    path('update_item/', views.update_item, name='update_item'),  # AJAX
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-item/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    
    # ====================== BLOG ======================
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('blogs/create/', views.blog_create, name='blog_create'),
    path('blogs/<int:pk>/edit/', views.blog_update, name='blog_update'),
    path('blogs/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
]