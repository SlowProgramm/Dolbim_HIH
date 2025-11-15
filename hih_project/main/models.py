from django.db.models import CharField, TextField, Model, IntegerField, PositiveBigIntegerField, FloatField, ImageField, DateTimeField, ForeignKey, JSONField, CASCADE, PROTECT
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
    id: TextField = TextField(editable=False, primary_key=True, default=generate_id)
    avatar: ImageField = ImageField(blank=True, upload_to=user_path)
    achievements: JSONField = JSONField(editable=False, default=list)
    estimations: JSONField = JSONField(editable=False, default=list)
    bought_apps: JSONField = JSONField(editable=False, default=list)

    def __str__(self) -> str:
        return f'{self.id}_{self.username}'


class AppCategory(Model):
    name: CharField = CharField(max_length=100, unique=True)
    description: TextField = TextField(default='')
    icon: ImageField = ImageField(blank=True, upload_to=icon_path)

    def __str__(self) -> str:
        return f'{self.id}'


class AppSubcategory(Model):
    name: CharField = CharField(max_length=100)
    category: ForeignKey = ForeignKey(AppCategory, CASCADE)
    description: TextField = TextField(default='')
    icon: ImageField = ImageField(blank=True, upload_to=icon_path)

    def __str__(self) -> str:
        return f'AppSubcategory(name={self.name}, category={self.category.name})'
    

class AppAgeRating(Model):
    min_age: IntegerField = IntegerField(unique=True)

    def to_display_str(self) -> str:
        """Return app age rating in form 'minimal_age+', for example '0+'."""
        return f'{self.min_age}+'
    
    def __str__(self) -> str:
        return f'AppAgeRating(min_age={self.min_age})'
    

class AppDeveloper(Model):
    id: TextField = TextField(editable=False, primary_key=True, default=generate_id)
    name: CharField = CharField(max_length=256, unique=True)
    description: TextField = TextField(default='')
    avatar: ImageField = ImageField(blank=True, upload_to=app_developer_path)

    def __str__(self) -> str:
        return f'AppDeveloper(name={self.name})'


class App(Model):
    id: TextField = TextField(editable=False, primary_key=True, default=generate_id)
    name: CharField = CharField(max_length=256)
    """App name."""
    description: TextField = TextField()
    """App description."""
    icon: ImageField = ImageField(upload_to=app_path, blank=True)
    rating: FloatField = FloatField(editable=False, default=0.0)
    """App rating from 0.0 to 5.0."""
    estimations_count: PositiveBigIntegerField = PositiveBigIntegerField(editable=False, default=0)
    """Amount of estimations."""
    downloads: PositiveBigIntegerField = PositiveBigIntegerField(editable=False, default=0)
    """Amount of unique downloads."""
    views: PositiveBigIntegerField = PositiveBigIntegerField(editable=False, default=0)
    """Amount of unique views."""
    size: FloatField = FloatField()
    """Size of the app in bytes."""
    age_rating: ForeignKey = ForeignKey(AppAgeRating, PROTECT)
    """App age rating."""
    subcategory: ForeignKey = ForeignKey(AppSubcategory, PROTECT)
    """Subcategory of the app."""
    developer: ForeignKey = ForeignKey(AppDeveloper, CASCADE)
    """App developer."""

    def __str__(self) -> str:
        return f'App(name={self.name})'


class AppEstimation(Model):
    app: ForeignKey = ForeignKey(App, CASCADE)
    """App that is estimated."""
    author: ForeignKey = ForeignKey(settings.AUTH_USER_MODEL, CASCADE)
    """User that left the estimation."""
    estimation: FloatField = FloatField()
    """Estimation from 0.0 to 5.0."""
    published_at: DateTimeField = DateTimeField()
    """Date and time of estimation published."""
    content: TextField = TextField()
    """Text content of the estimation."""


class AppPreviewImage(Model):
    app: ForeignKey = ForeignKey(App, CASCADE)
    place: IntegerField = IntegerField()
    source: ImageField = ImageField(default=None, upload_to=app_preview_image_path)


class Achievement(Model):
    id: TextField = TextField(editable=False, primary_key=True, default=generate_id)
    title: CharField = CharField(max_length=256)
    description: TextField = TextField()
    icon: ImageField = ImageField(blank=True, upload_to=achievement_path)
