from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, Textarea, CharField, PasswordInput, Form, IntegerField
from django.db.models import Model
from .models import StoreUser, AppEstimation
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
        

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'signup_page_form_input',
            'placeholder': 'Введите имя пользователя',
            'autocomplete': 'username'
        }),
        help_text=''
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'signup_page_form_input',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        }),
        help_text=''
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'signup_page_form_input',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        }),
        help_text=''
    )

    class Meta:
        model = StoreUser
        fields = ('avatar', 'username', 'password1', 'password2')

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов')
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        
        return cleaned_data
    
    
class LoginForm(AuthenticationForm):
    username: CharField = CharField(label='Имя пользователя')
    password: CharField = CharField(label='Пароль', widget=PasswordInput)


class EstimationForm(forms.ModelForm):

    estimation = forms.TypedChoiceField(
        choices=[
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
        ],
        coerce=int,
        label="Оценка",
        widget=forms.Select(attrs={
            "class": "review-select"
        })
    )

    content = forms.CharField(
        label="Ваш отзыв",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "review-textarea",
            "rows": 4,
            "maxlength": 500,
            "placeholder": "Напишите ваш отзыв…"
        })
    )

    class Meta:
        model = AppEstimation
        fields = ["estimation", "content"]


class SearchAppsForm(Form):
    search_request = CharField(
        label='Поисковый запрос',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'search-request'
        })
    )
    search_sorting_method = forms.TypedChoiceField(
        coerce=int,
        choices=[
            (1, 'популярности (Возрастание)'),
            (2, 'отзывам (Возрастание)'),
            (3, 'скачиваниям (Возрастание)'),
            (4, 'популярности (Убывание)'),
            (5, 'отзывам (Убывание)'),
            (6, 'скачиваниям (Убывание)')
        ],
        required=False,
        initial=1,
        label='Метод сортировки поиска',
        widget=forms.Select(attrs={'class': 'search-sorting-methods'})
    )
