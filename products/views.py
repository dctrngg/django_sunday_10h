# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Order, OrderItem, Comment
import json


# ====================== SẢN PHẨM ======================
def product_list(request):
    """Danh sách sản phẩm có tìm kiếm & lọc"""
    products = Product.objects.all().order_by("id")

    # Tìm kiếm
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Lọc thương hiệu
    brand = request.GET.get("brand")
    if brand and brand != "all":
        products = products.filter(brand=brand)

    # Lọc giá
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    brands = dict(Product.BRAND_CHOICES).keys()

    context = {
        "page_obj": page_obj,
        "brands": brands,
        "selected_brand": brand or "all",
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, product_id):
    """Chi tiết sản phẩm + bình luận"""
    product = get_object_or_404(Product, pk=product_id)
    related = Product.objects.filter(brand=product.brand).exclude(pk=product.id)[:4]
    
    # Lấy bình luận đang hoạt động
    comments = product.comments.filter(is_active=True)

    context = {
        "product": product,
        "related_products": related,
        "comments": comments,
    }
    return render(request, "products/product_detail.html", context)


# ====================== BÌNH LUẬN ======================
@login_required
def add_comment(request, product_id):
    """Thêm bình luận cho sản phẩm"""
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if not content:
            messages.error(request, "Vui lòng nhập nội dung bình luận.")
        elif len(content) < 5:
            messages.error(request, "Bình luận phải có ít nhất 5 ký tự.")
        else:
            Comment.objects.create(
                product=product,
                user=request.user,
                content=content
            )
            messages.success(request, "Bình luận của bạn đã được gửi thành công!")

    return redirect("product_detail", product_id=product_id)




# ====================== GIỎ HÀNG ======================
@login_required
def cart(request):
    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    items = order.order_items.all()
    return render(request, "products/cart.html", {"order": order, "items": items})


@login_required
def update_item(request):
    """AJAX: thêm / giảm số lượng trong giỏ hàng"""
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

        return JsonResponse({"status": "success", "cart_total": order.get_cart_items})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    if not created:
        order_item.quantity += 1
    order_item.save()
    messages.success(request, f"Đã thêm {product.name} vào giỏ hàng!")
    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    item.delete()
    messages.info(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("cart")


@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    if request.method == "POST":
        qty = request.POST.get("quantity", "1")
        try:
            new_qty = int(qty)
            if new_qty > 0:
                item.quantity = new_qty
                item.save()
            else:
                item.delete()
        except ValueError:
            messages.error(request, "Số lượng không hợp lệ.")
    return redirect("cart")


# ====================== BLOG ======================
def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/blog_detail.html', {'blog': blog})


def blog_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        is_published = request.POST.get('is_published') == 'on'
        image = request.FILES.get('image')

        blog = Blog(title=title, content=content, is_published=is_published)
        if image:
            blog.image = image
        blog.save()
        return redirect('blog_list')
    return render(request, 'blog/blog_form.html')


def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.is_published = request.POST.get('is_published') == 'on'
        if request.FILES.get('image'):
            blog.image = request.FILES.get('image')
        blog.save()
        return redirect('blog_list')
    return render(request, 'blog/blog_form.html', {'blog': blog})


def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})