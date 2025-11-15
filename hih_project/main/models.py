from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from uuid import uuid6

def generate_id() -> str:
    return uuid6().hex


def user_path(instance: 'StoreUser', filename: str) -> str:
    return f'users/user_id{instance.id}/{filename}'


def achievement_path(instance: 'Achievement', filename: str) -> str:
    return f'achievements/achievement_id{instance.id}/{filename}'


def icon_path(_, filename: str) -> str:
    return f'icons/{filename}'


def app_developer_path(instance: 'AppDeveloper', filename: str) -> str:
    return f'app_developers/developer_id{instance.id}/{filename}'


def app_path(instance: 'App', filename: str) -> str:
    return f'apps/app_id{instance.id}/{filename}'

    
def app_preview_image_path(instance: 'AppPreviewImage', filename: str) -> str:
    return app_path(instance.app, f'preview_images/{filename}')


class StoreUser(AbstractUser):
    id = models.TextField(editable=False, primary_key=True, default=generate_id)
    avatar= models.ImageField(blank=True, upload_to=user_path)
    achievements = models.JSONField(editable=False, default=list)
    estimations = models.JSONField(editable=False, default=list)
    bought_apps = models.JSONField(editable=False, default=list)

    def __str__(self) -> str:
        return f'{self.id}_{self.username}'


class AppCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(blank=True, upload_to=icon_path)

    def __str__(self) -> str:
        return f'Категория {self.name}'


class AppSubcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AppCategory, models.CASCADE)
    description = models.TextField(blank=True)
    icon = models.ImageField(blank=True, upload_to=icon_path)

    def __str__(self) -> str:
        return f'AppSubcategory(name={self.name}, category={self.category.name})'
    

class AppAgeRating(models.Model):
    min_age = models.PositiveIntegerField(unique=True)
    
    def __str__(self) -> str:
        return f'AppAgeRating {self.min_age}+'
    

class AppDeveloper(models.Model):
    id = models.TextField(editable=False, primary_key=True, default=generate_id)
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(blank=True, upload_to=app_developer_path)

    def __str__(self) -> str:
        return f'AppDeveloper(name={self.name})'


class App(models.Model):
    id = models.TextField(editable=False, primary_key=True, default=generate_id)
    """App UUID"""
    name = models.CharField(max_length=256)
    """App name."""
    description = models.TextField()
    """App description."""
    icon = models.ImageField(upload_to=app_path, blank=True)
    """App icon."""
    size = models.FloatField()
    """Size of the app in bytes."""
    age_rating = models.ForeignKey(AppAgeRating, models.PROTECT)
    """App age rating."""
    subcategory = models.ForeignKey(AppSubcategory, models.PROTECT)
    """Subcategory of the app."""
    developer = models.ForeignKey(AppDeveloper, models.CASCADE)
    """App developer."""
    rating = models.FloatField(editable=False, default=0.0)
    """App rating from 0.0 to 5.0."""
    estimations_count = models.PositiveBigIntegerField(editable=False, default=0)
    """Amount of estimations."""
    downloads = models.PositiveBigIntegerField(editable=False, default=0)
    """Amount of unique downloads."""
    views = models.PositiveBigIntegerField(editable=False, default=0)
    """Amount of unique views."""

    def __str__(self) -> str:
        return f'App(name={self.name})'


class AppEstimation(models.Model):
    app = models.ForeignKey(App, models.CASCADE)
    """App that is estimated."""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    """User that left the estimation."""
    estimation = models.PositiveSmallIntegerField()
    """Estimation from 0.0 to 5.0."""
    published_at = models.DateTimeField()
    """Date and time of estimation published."""
    content = models.TextField(blank=True)
    """Text content of the estimation."""


class AppPreviewImage(models.Model):
    app = models.ForeignKey(App, models.CASCADE)
    place = models.PositiveIntegerField()
    source = models.ImageField(default=None, upload_to=app_preview_image_path)


class Achievement(models.Model):
    id = models.TextField(editable=False, primary_key=True, default=generate_id)
    title = models.CharField(max_length=256)
    description = models.TextField()
    icon = models.ImageField(blank=True, upload_to=achievement_path)
