from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

urlpatterns = [
    path('', index_view, name='home'),
    path('about/', about_view, name='about'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('admin/', admin.site.urls),
    path('apps/', apps_view, name='apps'),
    path('app/<int:app_id>/', app_detail_view, name='app_detail'), 
    path('categories/', categories_view, name='category_list'),
    path('app_for_category/', apps_for_category_view, name='app_for_category'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)