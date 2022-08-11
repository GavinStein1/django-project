from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


# Create your models here.

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('authapp.User', on_delete=models.CASCADE)
    file_path = models.FilePathField(path="")
    caption = models.CharField(max_length=240)
    likes = ArrayField(models.IntegerField(), default=list)



    def __str__(self):
        return str(self.id)
