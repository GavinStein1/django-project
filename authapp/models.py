from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
import uuid

class User(AbstractUser):
    """Model representing a user. Inherits from django user model."""

    # followers = fields.ArrayField(models.IntegerField(), default=list)
    # following = fields.ArrayField(models.IntegerField(), default=list)
    #
    # unseen_posts = fields.ArrayField(models.UUIDField(), default=list)
    #
    # profile_pic = models.FilePathField(path="/media/profiles/default.jpg")
    # bio = models.CharField(max_length=240)

class UserData(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    followers = fields.ArrayField(models.IntegerField(), default=list)
    following = fields.ArrayField(models.IntegerField(), default=list)

    unseen_posts = fields.ArrayField(models.UUIDField(), default=list)

    profile_pic = models.FilePathField(path="/media/profiles/default.jpg", default="/media/profiles/default.jpg")
    bio = models.CharField(max_length=240)
