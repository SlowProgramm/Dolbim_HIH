from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from main.views import *

urlpatterns = [
    path('', index_view, name='index'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('admin/', admin.site.urls),
    path('apps/', apps_view, name='apps'),
    path('app/<str:app_id>/', app_detail_view, name='app_detail'), 
    path('categories/', category_view, name='categories'),
    path('app_for_category/', apps_for_category_view, name='app_for_category'),
    path('developer/<str:dev_id>/', developer_view, name='developer'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('search/', search_apps_view, name='search')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)