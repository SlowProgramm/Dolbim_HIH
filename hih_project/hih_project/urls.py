from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

urlpatterns = [
    path('', index_view, name='home'),
    path('about/', about_view, name='about'),
    path('create/', create_view, name='create'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('admin/', admin.site.urls),
    path('apps/', apps_view, name='apps'),
    path('fuck/', index_view, name='app_detail'),  # Заглушка
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)