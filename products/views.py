from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
import json

from django.db.models import Q

def product_list(request):
    """Danh sách sản phẩm có tìm kiếm & lọc theo giá / thương hiệu"""
    products = Product.objects.all().order_by("id")

    # --- TÌM KIẾM ---
    query = request.GET.get("q")
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # --- LỌC THEO THƯƠNG HIỆU ---
    brand = request.GET.get("brand")
    if brand and brand != "all":
        products = products.filter(brand=brand)

    # --- LỌC THEO GIÁ ---
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # --- PHÂN TRANG ---
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- LẤY DANH SÁCH THƯƠNG HIỆU ---
    brands = dict(Product.BRAND_CHOICES).keys()

    context = {
        "page_obj": page_obj,
        "brands": brands,
        "selected_brand": brand,
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, product_id):
    """Trang chi tiết sản phẩm"""
    product = get_object_or_404(Product, pk=product_id)
    related = Product.objects.filter(brand=product.brand).exclude(pk=product.id)[:4]

    return render(request, "products/product_detail.html", {
        "product": product,
        "related_products": related,
    })


@login_required
def cart(request):
    """Hiển thị giỏ hàng người dùng"""
    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    items = order.order_items.all()
    return render(request, "products/cart.html", {"order": order, "items": items})


@login_required
def update_item(request):
    """API thêm/xoá sản phẩm trong giỏ hàng (AJAX)"""
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("productId")
        action = data.get("action")

        product = get_object_or_404(Product, id=product_id)
        order, _ = Order.objects.get_or_create(user=request.user, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == "add":
            order_item.quantity += 1
        elif action == "remove":
            order_item.quantity -= 1

        if order_item.quantity <= 0:
            order_item.delete()
        else:
            order_item.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    if not created:
        order_item.quantity += 1
    order_item.save()

    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    item.delete()
    return redirect('cart')


@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    if request.method == 'POST':
        new_qty = int(request.POST.get('quantity', 1))
        if new_qty > 0:
            item.quantity = new_qty
            item.save()
        else:
            item.delete()
    return redirect('cart')


@login_required
def cart_view(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    items = order.order_items.all()
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'products/cart.html', context)

