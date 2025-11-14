from django.db import models
from django.db.models import CharField, TextField

class Task(models.Model):
    title: CharField = CharField('Название', max_length=50)
    task: TextField = TextField('Описание')

    def __str__(self) -> str:
        return self.title
    