from django.contrib import admin
from django.urls import path, URLPattern
from main.views import index, about

urlpatterns: list[URLPattern]  = [
    path('', index, name = 'home'),
    path('about/', about, name = 'about'),
]
