 
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import login, authenticate
from .models import *
from .forms import *

def index_view(request: HttpRequest) -> HttpResponse:
    tasks = Task.objects.all()
    tasks = Task.objects.order_by('id')
    return render(request, 'hello.html', {'title':'Главная', 'tasks':tasks})


def about_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')

# skjlfh
def create_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            redirect('home')

    form = TaskForm()
    context = {
        'form':form
        }
    return render(request, 'create.html', context)


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

# Библиотека приложений
def apps_view(request: HttpRequest) -> HttpResponse:
    apps = App.objects.all()
    return render(request, 'apps.html', {'apps': apps})

# Страница игры подробная
def app_detail_view(request: HttpRequest, app_id:int)-> HttpResponse:
    try:
        app = App.objects.get(id=app_id)
        context = {
            'app': app
        }
        return render(request, 'app_detail.html', context)
    except App.DoesNotExist:
        return render(request, '404.html', status=404)
    

# Страница выбора категории
def categories_view(request):
    categories = AppCategory.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


# Страница с приложениями конкретной категории
def apps_for_category_view(request):
    # Бля еще изменения
    # БАБАБАБАБАБАБ
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    
    apps = App.objects.all()
    
    if subcategory_id:
        apps = apps.filter(subcategory_id=subcategory_id)
    elif category_id:
        apps = apps.filter(subcategory__category_id=category_id)
    
    return render(request, 'apps.html', {'apps': apps})