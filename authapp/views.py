from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail

from .forms import NewUserForm
from .models import User, UserData
from .tokens import account_activation_token
from insta import settings

# Create your views here.


def create_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            existing_users = User.objects.filter(email=form.cleaned_data.get('email'))
            if len(existing_users) != 0:
                return HttpResponse('Account exists with this email')

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'

            message = render_to_string('authapp/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = [form.cleaned_data.get('email')]
            email_from = settings.EMAIL_HOST_USER
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            send_mail(mail_subject, message, email_from, to_email)
            # email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            context = {}
            errs = form.errors.as_data()
            username_err = errs.get('username')
            if username_err is not None:
                username_err = str(username_err[0])
                context['username_error_message'] = username_err
            email_err = errs.get('email')
            if email_err is not None:
                email_err = str(email_err[0])
                context['email_error_message'] = email_err
            password1_err = errs.get('password1')
            if password1_err is not None:
                password1_err = str(password1_err[0])
                context['password1_error_message'] = password1_err
            password2_err = errs.get('password2')
            if password2_err is not None:
                password2_err = str(password2_err[0])
                context['password2_error_message'] = password2_err

            context['form'] = NewUserForm()
            return render(request, "authapp/create_user.html", context)
    else:
        form = NewUserForm()
        context = {
            "form": form,
        }
        return render(request, "authapp/create_user.html", context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Create UserData instance for the user
        user_data = UserData(user=user)
        user_data.save()
        login(request, user)
        return HttpResponseRedirect("/")
    else:
        return HttpResponse('Activation link is invalid!')


def check_user_data(data):
    if data["password"] != data["password_again"]:
        return "Passwords don't match"

    username = data["username"]

    check_list = User.objects.filter(username=username)
    if len(check_list) != 0:
        return "Username exists"

    return None