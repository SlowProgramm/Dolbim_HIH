from django.db.models import CharField, TextField, Model, IntegerField, PositiveBigIntegerField, FloatField, ImageField, DateTimeField, ForeignKey, CASCADE, PROTECT
from django.contrib.auth.models import User

def icon_path(_, filename: str) -> str:
    return f'icons/{filename}'


def app_developer_path(instance: 'AppDeveloper', filename: str) -> str:
    return f'app_developer_id{instance.id}/{filename}'


def app_path(instance: 'App', filename: str) -> str:
    # Используем имя приложения вместо ID
    return f'app_icons/{instance.name}/{filename}'

def app_preview_image_path(instance: 'AppPreviewImage', filename: str) -> str:
    return app_path(instance.app, f'preview_images/{filename}')


class Task(Model):
    title: CharField = CharField('Название', max_length=50)
    task: TextField = TextField('Описание')

    def __str__(self) -> str:
        return self.title


# Категории, подкатегории, возрастные рейтинги, разработчики, приложения, достижения

class AppCategory(Model):
    name: CharField = CharField(max_length=100, unique=True)
    description: TextField = TextField()
    icon: ImageField = ImageField(upload_to=icon_path)

    def __str__(self) -> str:
        return f'AppCategory(name={self.name})'


class AppSubcategory(Model):
    name: CharField = CharField(max_length=100)
    category: ForeignKey = ForeignKey(AppCategory, CASCADE)
    description: TextField = TextField()
    icon: ImageField = ImageField(upload_to=icon_path)

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
    name: CharField = CharField(max_length=256, unique=True)
    description: TextField = TextField()
    avatar: ImageField = ImageField(upload_to=app_developer_path)

    def __str__(self) -> str:
        return f'AppDeveloper(name={self.name})'

class App(Model):
    name: CharField = CharField(max_length=256)
    """App name."""
    description: TextField = TextField()
    """App description."""
    icon: ImageField = ImageField(upload_to=app_path)
    rating: FloatField = FloatField(default=0.0)
    """App rating from 0.0 to 5.0."""
    estimations_count: PositiveBigIntegerField = PositiveBigIntegerField(default=0)
    """Amount of estimations."""
    downloads: PositiveBigIntegerField = PositiveBigIntegerField(default=0)
    """Amount of unique downloads."""
    views: PositiveBigIntegerField = PositiveBigIntegerField(default=0)
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
    author: ForeignKey = ForeignKey(User, CASCADE)
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
    source: ImageField = ImageField(upload_to=app_preview_image_path)
