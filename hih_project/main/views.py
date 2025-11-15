from uuid import uuid6
from uuid import uuid6
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.utils import timezone
from django.contrib.auth import login, authenticate
from datetime import datetime
from .models import *
from .forms import *
import os
import random
import shutil
from django.core.files import File
from django.conf import settings


def get_and_remove_random_icon():
    icons_dir = "C:/Users/Sol/Desktop/hih_icons"
    
    
    image_files = []
    for file in os.listdir(icons_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image_files.append(file)
    
    if not image_files:
        return None
    

    random_icon = random.choice(image_files)
    icon_path = os.path.join(icons_dir, random_icon)
    
    return icon_path, random_icon

def remove_icon_from_folder(icon_path):
    """Удалить файл иконки из папки"""
    try:
        if os.path.exists(icon_path):
            os.remove(icon_path)
            print(f"Иконка удалена: {icon_path}")
            return True
    except Exception as e:
        print(f"Ошибка при удалении иконки: {e}")
    return False



def create_app(request):
    # TARGET_CATEGORIES = [
    #     "Шутеры",
    #     "Аркады",
    #     "Гоночные",
    #     "Игры с AR",
    #     "Головоломки",
    #     "Словесные",
    #     "Викторины",
    #     "Приключения",
    #     "Ролевые",
    #     "Инди",
    #     "Стратегии",
    #     "Настольные игры",
    #     "Карточные",
    #     "Детские",
    #     "Семейные",
    # ]
    
    main_category, created = AppCategory.objects.get_or_create(name="Игры")
    
    # Создаем все субкатегории
    for category_name in TARGET_CATEGORIES:
        AppSubcategory.objects.get_or_create(
            name=category_name,
            category=main_category
        )
    
    # print(f"Создано {len(TARGET_CATEGORIES)} субкатегорий")


    # ico_path, dir = get_and_remove_random_icon()

    # app = App(
    #         id=str(uuid6()),
    #         name="Имя приложение",
    #         description="Это тестовое приложение, созданное через кнопку",
    #         size=125,
    #         age_rating=AppAgeRating.objects.order_by('?').first(),
    #         subcategory=AppSubcategory.objects.order_by('?').first(),
    #         developer=AppDeveloper.objects.order_by('?').first(),
    #         rating=0,
    #         estimations_count=0,
    #         downloads=0,
    #         views=0,
    #     )
    # icon_result = get_and_remove_random_icon()
    # if icon_result:
    #     icon_path, original_filename = icon_result
    #     with open(icon_path, 'rb') as f:
    #         app.icon.save(original_filename, File(f), save=False)
    #     app.save()
    #     remove_icon_from_folder(icon_path)
    #     print('ХАЙП')
    # else:
    #     print('Error')
    return render(request, 'account.html')


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
    if request.method == 'POST':
        create_app(request)
    return render(request, 'account.html', {'user_estimations': request.user.query_apps_estimations()})


def apps_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        pass

    return render(request, 'apps.html', {
        'popular_apps': App.objects.order_by('-rating', '-downloads').all(),

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

                request.user.estimations.append(estimation.id)
                request.user.save()
    elif estimation is not None:
        form = EstimationForm(initial={
            'estimation': estimation.estimation,
            'estimation_content': estimation.content
        })
    else:
        form = EstimationForm()
    return render(request, 'app_detail.html', {
        'app': app,
        'user_estimation_exists': estimation is not None,
        'estimations': AppEstimation.objects.filter(app=app),
        'form': form
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
    

def import_apps_from_json(json_file_path):
    # Чтение JSON файла
    with open(json_file_path, 'r', encoding='utf-8') as file:
        apps_data = json.load(file)
    
    for app_data in apps_data:
        try:
            # Создание основного объекта приложения
            app = App(
                id=str(uuid6()),
                name=app_data['name'],
                description=app_data.get('short_description', '') or "Описание отсутствует",
                size=125,  # Можно рассчитать на основе реальных данных или оставить по умолчанию
                age_rating=AppAgeRating.objects.order_by('?').first(),
                subcategory=AppSubcategory.objects.order_by('?').first(),
                developer=AppDeveloper.objects.order_by('?').first(),
                rating=app_data.get('rating', 0),
                estimations_count=app_data.get('rating_count', 0),
                downloads=0,
                views=0,
            )
            app.save()
            
            # Загрузка иконки
            if app_data.get('icon_url'):
                try:
                    icon_response = requests.get(app_data['icon_url'], timeout=10)
                    if icon_response.status_code == 200:
                        icon_name = f"app_icons/{app.id}_icon.jpg"
                        app.icon.save(icon_name, ContentFile(icon_response.content), save=True)
                except Exception as e:
                    print(f"Ошибка загрузки иконки для {app_data['name']}: {e}")
            
            # Загрузка скриншотов
            if app_data.get('screenshots'):
                for i, screenshot_url in enumerate(app_data['screenshots']):
                    try:
                        screenshot_response = requests.get(screenshot_url, timeout=10)
                        if screenshot_response.status_code == 200:
                            screenshot_name = f"app_screenshots/{app.id}_screenshot_{i}.jpg"
                            
                            # Создание объекта скриншота (предполагая, что у вас есть модель AppScreenshot)
                            screenshot = AppScreenshot(
                                app=app,
                                image=screenshot_name
                            )
                            screenshot.image.save(
                                screenshot_name, 
                                ContentFile(screenshot_response.content), 
                                save=True
                            )
                    except Exception as e:
                        print(f"Ошибка загрузки скриншота {i} для {app_data['name']}: {e}")
            
            print(f"Успешно добавлено приложение: {app_data['name']}")
            
        except Exception as e:
            print(f"Ошибка при добавлении приложения {app_data.get('name', 'Unknown')}: {e}")


def search_apps_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and (form := SearchAppsForm(request.POST)).is_valid():
        search_sorting_method = form.cleaned_data['search_sorting_method']

        if search_sorting_method == 1:
            order_method = '-rating', '-downloads'
        elif search_sorting_method == 2:
            order_method = '-rating'
        elif search_sorting_method == 3:
            order_method = '-downloads'
        elif search_sorting_method == 4:
            order_method = 'rating', 'downloads'
        elif search_sorting_method == 5:
            order_method = 'rating'
        elif search_sorting_method == 6:
            order_method = 'downloads'
        else:
            order_method = ()

        search_request = form.cleaned_data['search_request'].lower()
        apps = App.objects.get_queryset().filter(name__icontains=search_request).order_by(*order_method).all()
    else:
        form = SearchAppsForm()
        search_request = None
        apps = None
    return render(request, 'search.html', {'form': form, 'apps': apps, 'search_request': search_request})
