from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    path('', views.home, name="home"),
    path('user/<str:user>/followers', views.user_followers, name="user-followers"),
    path('user/<str:user>/following', views.user_following, name="user-following"),
    path('user/<str:user>', views.user_home, name="user-home"),
    path('user/<str:user>/profile', views.user_profile, name="user-profile"),
    path('user/<str:user>/new-post', views.new_post, name="new-post"),
    path('feed', views.feed, name="feed")
]
