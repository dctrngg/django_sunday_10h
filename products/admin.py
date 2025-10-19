from django.contrib import admin
from .models import Product, Order, OrderItem, ShippingAddress

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'formatted_price', 'stock', 'created_at')
    search_fields = ('name', 'brand')
    list_filter = ('brand',)
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'complete', 'date_ordered', 'transaction_id')
    list_filter = ('complete',)
    search_fields = ('user__username',)
    ordering = ('-date_ordered',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'get_total')
    search_fields = ('product__name',)
    list_filter = ('order__complete',)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'city', 'state', 'zipcode', 'date_added')
    search_fields = ('user__username', 'address', 'city')
