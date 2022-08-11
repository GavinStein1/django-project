from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.views import generic
from django.urls import reverse

from .models import Post
from authapp.models import User


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("user/" + request.user.username)
    template = loader.get_template("home/home.html")
    return HttpResponse(template.render({}, request))


def user_home(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("{}/profile".format(user))

    posts = Post.objects.filter(user__pk=request.user.pk)
    follower_count = get_follower_count(request.user)
    following_count = get_following_count(request.user)
    context = {
        'posts': posts,
        'num_followers': follower_count,
        'num_following': following_count,
    }
    return render(request, 'home/home.html', context)


def user_followers(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("{}/profile".format(user))

    followers_pk = request.user.followers
    followers = []
    for pk in followers_pk:
        followers.append(User.objects.get(pk=pk).username)
    context = {
        "followers": followers,
        "num_followers": len(followers),
    }
    return render(request, 'home/followers.html', context)


def user_following(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("{}/profile".format(user))

    following_pk = request.user.following
    following = []
    for pk in following_pk:
        following.append(User.objects.get(pk=pk).username)
    context = {
        "following": following,
        "num_following": len(following),
    }

    return render(request, 'home/following.html', context)


def user_profile(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user == request.user.username:
        return HttpResponseRedirect(reverse("home:user-home", args=(user,)))

    # TODO: Check request.user is in user's followers (ensure privacy).
    # If request.user not in user's followers, show restricted page. Else show user profile
    profile_user = User.objects.get(username=user)
    if request.user.pk not in profile_user.followers:
        return HttpResponse("You do not follow this user")

    posts = Post.objects.filter(user__pk=profile_user.pk)
    context = {
        "profile_user": profile_user,
        "posts": posts,
    }
    return render(request, 'home/profile.html', context)


def get_follower_count(user):
    return len(user.followers)


def get_following_count(user):
    return len(user.following)


def feed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    posts = request.user.unseen_posts

    context = {
        "posts": posts,
    }

    return render(request, 'home/feed.html', context)


def new_post(request, user):

    return render(request, 'home/new_post.html', {})
