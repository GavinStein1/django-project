from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.views import generic
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import Post
from .forms import NewPostForm
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

    if request.method == "POST":
        data = request.POST
        usr = User.objects.get(username=user)
        if data["follow"] == "follow":
            request.user.following.append(usr.pk)
            usr.followers.append(request.user.pk)
            request.user.save()
            usr.save()
            # return HttpResponseRedirect(reverse("home:user-profile", args=(user,)))
        if data["follow"] == "unfollow":
            request.user.following.remove(usr.pk)
            usr.followers.remove(request.user.pk)
            request.user.save()
            usr.save()
            # return HttpResponseRedirect(reverse("home:user-profile", args=(user,)))

    profile_user = User.objects.get(username=user)
    if request.user.pk not in profile_user.followers:
        follow = False
    else:
        follow = True

    posts = Post.objects.filter(user__pk=profile_user.pk)
    context = {
        "profile_user": profile_user,
        "posts": posts,
        "follow": follow,
    }
    return render(request, 'home/profile.html', context)


def get_follower_count(user):
    return len(user.followers)


def get_following_count(user):
    return len(user.following)


def feed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    posts_id = request.user.unseen_posts
    posts = []
    for post_id in posts_id:
        posts.append(Post.objects.get(id=post_id))
    posts.reverse()
    request.user.unseen_posts = []
    request.user.save()

    context = {
        "posts": posts,
    }

    return render(request, 'home/feed.html', context)


def new_post(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            image = Image.open(data["image"])
            message = check_image(image)
            if message is None:
                post = Post()
                post.user = request.user
                post.caption = data["caption"]
                post.pub_date = timezone.now()
                try:
                    image.save("media/posts/{}.{}".format(post.id, image.format), format=image.format)
                except Exception as e:
                    print(e)
                    return HttpResponse("Failed to upload image")

                post.file_path = "media/posts/{}.{}".format(post.id, image.format)
                post.save()

                for follower in request.user.followers:
                    usr = User.objects.get(pk=follower)
                    usr.unseen_posts.append(post.id)
                    usr.save()
                return HttpResponseRedirect(reverse("home:home"))
            else:
                context = {
                    "err_message": message,
                    "form": NewPostForm(),
                }
                return render(request, 'home/new_post.html', context)

        else:
            message = "Error parsing form"
            context = {
                "err_message": message,
                "form": NewPostForm,
            }
            return render(request, 'home/new_post.html', context)

    else:
        form = NewPostForm()
        context = {
            "form": form,
        }
        return render(request, 'home/new_post.html', context)


def check_image(img):
    try:
        formats = [
            "PNG",
            "JPEG",
            "HEIC",
            "jpg",
            "jpeg",
        ]

        if img.format not in formats:
            return "Invalid format"

        #check image dimensions (must be square)
        # TODO: implement cropping functionality
        dimensions = img.size
        if dimensions[0] != dimensions[1]:
            print(dimensions)
            return "Photo not square"
        else:
            return None
    except Exception:
        return "Error processing image"
