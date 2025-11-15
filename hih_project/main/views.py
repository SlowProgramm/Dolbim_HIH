 
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import login, authenticate
from .models import *
from .forms import *

def index_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', {'title':'Главная'})


def about_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('account')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('account')
    return render(request, 'login.html', {'form': form})


def account_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'account.html')


def apps_view(request: HttpRequest) -> HttpResponse:
    apps = App.objects.all()
    return render(request, 'apps.html', {'apps': apps})


def app_detail_view(request: HttpRequest, app_id: str)-> HttpResponse:
    try:
        app = App.objects.get(id=app_id)
        context = {
            'app': app
        }
        return render(request, 'app_detail.html', context)
    except App.DoesNotExist:
        return render(request, '404.html', status=404)
    

def categories_view(request):
    categories = AppCategory.objects.prefetch_related('appsubcategory_set').all()
    return render(request, 'category_list.html', {'categories': categories})


def apps_for_category_view(request):
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    apps = App.objects.all()
    
    if subcategory_id:
        apps = apps.filter(subcategory_id=subcategory_id)
    elif category_id:
        apps = apps.filter(subcategory__category_id=category_id)
    return render(request, 'apps.html', {'apps': apps})


def apps_for_category_view(request: HttpRequest) -> HttpResponse:
    subcategory_id = request.GET.get('subcategory')
    apps = App.objects.select_related(
        'subcategory', 
        'subcategory__category', 
        'developer'
    ).all()
    
    if subcategory_id:
        apps = apps.filter(subcategory_id=subcategory_id)
    # Если подкатегория не выбрана, показываем все игры
    context = {
        'apps': apps,
        'subcategory_id': subcategory_id,
    }
    
    return render(request, 'app_for_category.html', context)


def developer_view(request: HttpRequest, dev_id: str) -> HttpResponse:
    name = request.GET.get('name')
    try:
        dev = AppDeveloper.objects.get(id=dev_id)

        apps = App.objects.filter(developer=dev)

        context = {
            'dev': dev,
            'apps' : apps,
        }
        return render(request, 'developer_page.html', context)
    except App.DoesNotExist:
        return render(request, '404.html', status=404)
