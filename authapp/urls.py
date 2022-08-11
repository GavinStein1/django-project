from django.urls import path

from . import views


app_name = 'authapp'
urlpatterns = [
    path('create-user', views.create_user, name="create-user"),
    ]
