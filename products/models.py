from django.db import models
from django.contrib.auth.models import User  # dùng user đăng nhập hiện tại
from django.contrib.humanize.templatetags.humanize import intcomma
from django.conf import settings

class Product(models.Model):
    BRAND_CHOICES = [
        ('Lenovo', 'Lenovo'),
        ('HP', 'HP'),
        ('Xiaomi', 'Xiaomi'),
        ('Other', 'Khác'),
        ('Phụ kiện', 'Phụ kiện'),
    ]

    name = models.CharField("Tên sản phẩm", max_length=255)
    brand = models.CharField("Hãng", max_length=50, choices=BRAND_CHOICES)
    image = models.ImageField("Ảnh sản phẩm", upload_to="products/", blank=True, null=True)
    description = models.TextField("Mô tả chi tiết", blank=True)
    price = models.DecimalField("Giá bán (VNĐ)", max_digits=10, decimal_places=0)
    delprice = models.DecimalField("Giá trước khi giảm (VNĐ)", max_digits=10, decimal_places=0, blank=True, null=True)
    stock = models.PositiveIntegerField("Tồn kho", default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_brand_display()})"

    def formatted_price(self):
        return f"{intcomma(int(self.price))} VNĐ"
    formatted_price.short_description = "Giá bán"

    def formatted_delprice(self):
        if self.delprice:
            return f"{intcomma(self.delprice)} VNĐ"
        return ""
    formatted_delprice.short_description = "Giá bán trước khi giảm"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

    @property
    def total_price(self):
        return sum(item.get_total for item in self.order_items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity

    @property
    def formatted_price(self):
        return f"{intcomma(int(self.get_total))} VNĐ"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping_addresses")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}, {self.city}"



