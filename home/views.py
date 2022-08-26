from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from PIL import Image

from .models import Post, Comment
from .forms import NewPostForm, EditProfileForm, ModelPostForm, CommentForm
from authapp.models import User, UserData


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
    post_comments = {}
    for post in posts:
        post_comments[post.id] = []
        for comment in post.comments:
            post_comments[post.id].append(Comment.objects.get(pk=comment))

    follower_count = len(get_followers(request.user))
    following_count = len(get_following(request.user))
    user_data = get_user_data(request.user)
    comment_form = CommentForm()
    context = {
        'user_data': user_data,
        'posts': posts,
        'num_followers': follower_count,
        'num_following': following_count,
        'comments': post_comments,
        'comment_form': comment_form
    }
    return render(request, 'home/home.html', context)


def user_followers(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("{}/profile".format(user))

    followers_pk = get_followers(request.user)
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

    following_pk = get_following(request.user)
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
        profile_usr_data = get_user_data(usr)
        request_user_data = get_user_data(request.user)
        if data["follow"] == "follow":
            request_user_data.following.append(usr.pk)
            profile_usr_data.followers.append(request.user.pk)
            request_user_data.save()
            profile_usr_data.save()
            # return HttpResponseRedirect(reverse("home:user-profile", args=(user,)))
        if data["follow"] == "unfollow":
            request_user_data.following.remove(usr.pk)
            profile_usr_data.followers.remove(request.user.pk)
            request_user_data.save()
            profile_usr_data.save()
            # return HttpResponseRedirect(reverse("home:user-profile", args=(user,)))
    try:
        profile_user = User.objects.get(username=user)
    except Exception as e:
        return HttpResponseNotFound(e)

    if request.user.pk not in get_user_data(profile_user).followers:
        follow = False
    else:
        follow = True

    posts = Post.objects.filter(user__pk=profile_user.pk)
    post_comments = {}
    for post in posts:
        post_comments[post.id] = []
        for comment in post.comments:
            post_comments[post.id].append(Comment.objects.get(pk=comment))
    user_data = get_user_data(profile_user)
    context = {
        "profile_user": profile_user,
        "user_data": user_data,
        "posts": posts,
        "follow": follow,
        "comments": post_comments,
    }
    return render(request, 'home/profile.html', context)


def get_followers(user):
    user_data = get_user_data(user)
    return user_data.followers


def get_following(user):
    user_data = get_user_data(user)
    return user_data.following


def feed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    user_data = get_user_data(request.user)
    posts_id = user_data.unseen_posts
    posts = []
    for post_id in posts_id:
        posts.append(Post.objects.get(id=post_id))
    posts.reverse()
    user_data.unseen_posts = []
    user_data.save()

    user_data = []
    for post in posts:
        user_data.append(UserData.objects.get(user=post.user))

    context = {
        "posts": posts,
        # "user_data": user_data,  # TODO: add profile pics next to posts in feed
    }

    return render(request, 'home/feed.html', context)


def new_post(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = ModelPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.pub_date = timezone.now()
            image = Image.open(post.image)
            message = check_image(image)
            if message is None:
                post.image.name = '{}.{}'.format(post.id, image.format)
                post.save()

                for follower in get_user_data(request.user).followers:
                    usr = User.objects.get(pk=follower)
                    usr_data = get_user_data(usr)
                    usr_data.unseen_posts.append(post.id)
                    usr_data.save()
                return HttpResponseRedirect(reverse("home:home"))
            else:
                context = {
                    "err_message": message,
                    "form": ModelPostForm(),
                }
                return render(request, 'home/new_post.html', context)

        else:
            message = "Error parsing form"
            context = {
                "err_message": message,
                "form": ModelPostForm,
            }
            return render(request, 'home/new_post.html', context)

    else:
        form = ModelPostForm()
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
            return "Photo not square"
        else:
            return None
    except Exception:
        return "Error processing image"


def get_user_data(user):
    user_data = UserData.objects.get(user=user)
    return user_data


def edit_profile(request, user):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if user != request.user.username:
        return HttpResponseRedirect("{}/profile".format(user))

    posts = Post.objects.filter(user__pk=request.user.pk)
    user_data = UserData.objects.get(user=request.user)

    p = list(range(len(posts)))
    select_options = []
    for x in p:
        select_options.append((str(x), str(x)))

    if request.method == "POST":
        form = EditProfileForm(select_options, request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            user = request.user
            user_data = get_user_data(user)

            if data['bio'] != '':
                user_data.bio = data['bio']
                user_data.save()

            if 'posts' in data.keys():
                for i in data['posts']:
                    post = list(posts)[int(i)]
                    post_id = post.id
                    for follower in user_data.followers:
                        follower_user_data = get_user_data(User.objects.get(pk=follower))
                        if post_id in follower_user_data.unseen_posts:
                            follower_user_data.unseen_posts.remove(post_id)
                            follower_user_data.save()
                    post.delete()

            if data['profile_pic'] is not None:
                image = Image.open(data["profile_pic"])
                message = check_image(image)
                if message is None:
                    user_data.profile_image = data["profile_pic"]
                    user_data.profile_image.name = '{}.{}'.format(request.user.username, image.format)
                    user_data.save()

            return HttpResponseRedirect("/")

        else:
            print(form.errors.as_data())
            return HttpResponse("Failed to save changes")

    form = EditProfileForm(select_options)

    context = {
        "posts": posts,
        "user_data": user_data,
        "form": form,
    }

    return render(request, "home/edit_profile.html", context)


def add_comment(request, post_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    post = Post.objects.get(id=post_id)
    post_user = post.user
    post_user_data = UserData.objects.get(user=post_user)

    if request.user.pk not in post_user_data.followers and request.user.pk != post_user.pk:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.pub_date = timezone.now()
            comment.save()

            post.comments.append(comment.pk)
            post.save()
            return HttpResponseRedirect(request.META.HTTP_REFERER)


def search_results(request, query):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    users = User.objects.filter(username__contains=query)
    user_data = []
    for user in users:
        try:
            user_data.append(get_user_data(user))
        except UserData.DoesNotExist:
            continue

    context = {
        "users": users,
        "users_data": user_data,
    }

    return render(request, "home/search_results.html", context)

