from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
import json

def product_list(request):
    """Danh sách sản phẩm có phân trang & theo hãng"""
    all_products = Product.objects.all().order_by("id")
    paginator = Paginator(all_products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    brands = dict(Product.BRAND_CHOICES).keys()
    products_by_brand = {
        brand: Product.objects.filter(brand=brand)[:4]
        for brand in brands if Product.objects.filter(brand=brand).exists()
    }

    return render(request, "products/product_list.html", {
        "page_obj": page_obj,
        "products_by_brand": products_by_brand,
    })


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

