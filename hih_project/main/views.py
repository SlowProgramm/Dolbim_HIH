from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.utils import timezone
from django.contrib.auth import login, authenticate
import urllib.parse
from .models import AppEstimation, App, AppSubcategory, AppCategory, AppDeveloper
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
    return render(request, 'account.html', {'user_estimations': request.user.query_apps_estimations()})


def apps_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'apps.html', {
        'popular_apps': App.query_popular_apps(),
        'user_top_10_apps': request.user.get_personal_top_10_apps() if request.user.is_authenticated else ()
    })


def app_detail_view(request: HttpRequest, app_id: str) -> HttpResponse:
    try:
        app = App.objects.get(id=app_id)
    except App.DoesNotExist:
        return render(request, '404.html', status=404)
    
    try:
        estimation = AppEstimation.objects.get(author=request.user, app=app)
    except AppEstimation.DoesNotExist:
        estimation = None

    if request.user.is_authenticated:
        if len(request.user.history) == 100:
            request.user.history.pop()
        request.user.history.insert(0, app.subcategory.id)
        request.user.save()
    
    if request.method == 'POST':
        form = EstimationForm(request.POST)
        if form.is_valid():
            form_estimation: float = form.cleaned_data['estimation']
            form_estimation_content: str = form.cleaned_data['content']
            if estimation is not None:
                app.rating = app.rating - (estimation.estimation - form_estimation) / app.estimations_count
                app.save()

                estimation.estimation = form_estimation
                estimation.content = form_estimation_content
                estimation.published_at = timezone.now()
                estimation.save()
            else:
                estimation = AppEstimation.objects.create(
                    app=app,
                    author=request.user,
                    estimation=form_estimation,
                    published_at=timezone.now(),
                    content=form_estimation_content
                )

                app.rating = (app.rating * app.estimations_count + estimation.estimation) / (app.estimations_count + 1)
                app.estimations_count += 1
                app.save()
    elif estimation is not None:
        form = EstimationForm(initial={
            'estimation': estimation.estimation,
            'estimation_content': estimation.content
        })
    else:
        form = EstimationForm()

    star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for est in AppEstimation.objects.filter(app=app):
        if est.estimation in star_counts:
            star_counts[est.estimation] += 1
    
    return render(request, 'app_detail.html', {
        'app': app,
        'user_estimation_exists': estimation is not None,
        'estimations': AppEstimation.objects.filter(app=app),
        'app_preview_images': app.query_preview_images(),
        'form': form,
        'app_download_link': f'https://www.rustore.ru/catalog/search?query={urllib.parse.quote(app.name)}',
        'star_counts': star_counts,  
    })


def category_view(request: HttpRequest) -> HttpResponse:
    categories = AppCategory.objects.all()
    context = {'categories': categories}

    if request.method == 'POST':
        if category_id := request.POST.get('category_id'):
            selected_category = AppCategory.objects.get(id=category_id)
            context['selected_category'] = selected_category
            context['subcategories'] = AppSubcategory.objects.filter(category=selected_category)
        elif subcategory_id := request.POST.get('subcategory_id'):
            subcategory = AppSubcategory.objects.get(id=subcategory_id)
            context['selected_category'] = subcategory.category
            context['subcategories'] = AppSubcategory.objects.filter(category=subcategory.category)
            context['apps'] = App.objects.filter(subcategory=subcategory)
    
    return render(request, 'category_list.html', context)


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

    context = {
        'apps': apps,
        'subcategory_id': subcategory_id,
    }
    
    return render(request, 'app_for_category.html', context)


def developer_view(request: HttpRequest, dev_id: str) -> HttpResponse:
    try:
        dev = AppDeveloper.objects.get(id=dev_id)
        return render(request, 'developer_page.html', {
            'dev': dev,
            'apps' : App.query_popular_apps(developer=dev)
        })
    except App.DoesNotExist or AppDeveloper.DoesNotExist:
        return render(request, '404.html', status=404)


def search_apps_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        if (form := SearchAppsForm(request.POST)).is_valid():
            search_request = form.cleaned_data['search_request'].strip().lower()
            apps = sorted(
                (app for app in App.objects.all() if search_request in app.name.lower()),
                key={
                    1: lambda x: (-x.rating, -x.downloads),
                    2: lambda x: (-x.rating,),
                    3: lambda x: (-x.downloads,),
                    4: lambda x: (x.rating, x.downloads),
                    5: lambda x: (x.rating,),
                    6: lambda x: (x.downloads,),
                }[form.cleaned_data['search_sorting_method']]
            )
    else:
        form = SearchAppsForm()
        search_request = None
        apps = None
    return render(request, 'search.html', {'form': form, 'apps': apps, 'search_request': search_request})


def onboarding_welcome(request: HttpRequest) -> HttpResponse:
    """Приветственный экран onboarding"""
    return render(request, 'onboarding/welcome.html')


def onboarding_tour(request: HttpRequest) -> HttpResponse:
    return render(request, 'onboarding/tour.html')
