from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Task
from .forms import TaskForm

def index(request: HttpRequest) -> HttpResponse:
    tasks = Task.objects.all()
    tasks = Task.objects.order_by('id')
    return render(request, 'hello.html', {'title':'Главная', 'tasks':tasks})

def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')

def create(request: HttpRequest) -> HttpResponse:
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
