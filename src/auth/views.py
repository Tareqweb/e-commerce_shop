import functools
import warnings

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login, logout,
    update_session_auth_hash
)
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_text
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import is_safe_url, urlsafe_base64_decode

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.utils.translation import ugettext as _
from .forms import UserLoginForm, UserRegisterForm, CreateVendor
import uuid
from django.core.mail import send_mail
# from accounts.forms import CreateProfile
# from accounts.models import Profile


UserModel = get_user_model()

def deprecate_current_app(func):
    """
    Handle deprecation of the current_app parameter of the views.
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            warnings.warn(
                "Passing `current_app` as a keyword argument is deprecated. "
                "Instead the caller of `{0}` should set "
                "`request.current_app`.".format(func.__name__),
                RemovedInDjango20Warning
            )
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)
    return inner


@deprecate_current_app
def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        # try:
        #     is_vendor = user.vendor
        # except Exception as e:
        #     is_vendor = False
        # if is_vendor:
        #     return redirect("/dashboard/")
        return redirect("/")
    context = {
        "form": form,
    }
    return render(request, "registration/login.html", context)

@deprecate_current_app
def vendor_login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        try:
            is_vendor = request.user.vendor
        except Exception as e:
            is_vendor = False
        if is_vendor:
            return redirect("/dashboard/vendor/")
        return redirect("/")
    context = {
        "form": form,
    }
    return render(request, "registration/vendor_login.html", context)


@deprecate_current_app
def admin_login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        try:
            is_vendor = request.user.vendor
        except Exception as e:
            is_vendor = False
        if is_vendor:
            return redirect("/dashboard/vendor/")
        return redirect("/")
    context = {
        "form": form,
    }
    return render(request, "registration/admin_login.html", context)


def vendor_register_view(request):
    form = UserRegisterForm(request.POST or None)
    vendor_form = CreateVendor(request.POST or None)
    if form.is_valid() and vendor_form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        vendor = vendor_form.save(commit=False)
        vendor.user = user
        vendor.active = True
        vendor.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)

        try:
            subject = "FnfBuy: Registration"
            from_email = "noreply@bizoytech.com"
            to_email = []
            to_email.append(vendor.email)
            message_body = "Welcome to FnFuy,\nCongratulations, you have successfully registered!"
            send_mail(subject, message_body, from_email, to_email)
        except Exception as e:
            print(e)


        return redirect("/dashboard/vendor/")
    else:
        print(form.errors)

    context = {
        "form": form,
        "vendor_form":vendor_form,
    }
    return render(request, "registration/vendor_registration.html", context)



def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)

        try:
            subject = "FnfBuy: Registration"
            from_email = "noreply@bizoytech.com"
            to_email = []
            to_email.append(user.email)
            message_body = "Welcome to FnFuy,\nCongratulations, you have successfully registered!"
            send_mail(subject, message_body, from_email, to_email)
        except Exception as e:
            print(e)

        return redirect("/")

    context = {
        "form": form,
    }
    return render(request, "registration/registration.html", context)


# def change_password(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)
#             messages.success(request, _('Your password was successfully updated!'))
#             return redirect('/')
#         else:
#             messages.error(request, _('Please correct the error below.'))
#     else:
#         form = PasswordChangeForm(request.user)
#     context = {
#         "form": form,
#     }
#     return render(request, "registration/change_password.html", context)


@deprecate_current_app
def logout_view(request):
    logout(request)
    return redirect("/")


# PasswordResetConfirmView() View didn't work that why we use custom
@never_cache
@deprecate_current_app
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    # warnings.warn("The password_reset_confirm() view is superseded by the "
    #               "class-based PasswordResetConfirmView().",
    #               RemovedInDjango21Warning, stacklevel=2)
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template_name, context)




from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


