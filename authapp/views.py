from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login

from .forms import NewUserForm
from .models import User

# Create your views here.


def create_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if check_user_data(data):

                user = User.objects.create_user(data["username"], data["email"], data["password"])

                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user.save()
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                return HttpResponseRedirect("/create-user")
    else:
        form = NewUserForm()
        context = {
            "form": form,
        }
        return render(request, "authapp/create_user.html", context)


def check_user_data(data):
    if data["password"] != data["password_again"]:
        print("passwords don't match")
        return False

    username = data["username"]

    check_list = User.objects.filter(username=username)
    if len(check_list) != 0:
        print("username exists")
        return False

    return True