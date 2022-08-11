from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
import uuid

class User(AbstractUser):
    """Model representing a user. Inherits from django user model."""

    followers = fields.ArrayField(models.IntegerField(), default=list)
    following = fields.ArrayField(models.IntegerField(), default=list)

    unseen_posts = fields.ArrayField(models.UUIDField(), default=list)