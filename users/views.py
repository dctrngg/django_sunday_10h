from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def user_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Anonymous')
        email = request.POST.get('email')
        age = request.POST.get('age', 18)
        avatar = request.FILES.get('avatar')
        User.objects.create(name=name or 'Anonymous', email=email, age=age or 18, avatar=avatar)
        return redirect('user_list')
    return render(request, 'users/user_form.html', {'action': 'create'})

@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.name = request.POST.get('name', user.name)
        user.email = request.POST.get('email', user.email)
        user.age = request.POST.get('age', user.age)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        return redirect('user_list')
    return render(request, 'users/user_form.html', {'action': 'update', 'user': user})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})
