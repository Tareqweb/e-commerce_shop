from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import (authenticate, get_user_model, login, logout)
User = get_user_model()

from vendors.models import Vendor


class CreateVendor(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'full_name',
            'company_name',
            'email',
            'phone',
            'mobile',
            'country',
            'state',
            'city',
            'address',
            'zipcode'
        ]


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Incorrect username/password combination being used. Please try again.")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect passsword")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
            if not user.is_active and user.vendor:
                raise forms.ValidationError("This vendor is not longer active.")
        return super(UserLoginForm, self).clean(*args, **kwargs)


def ForbiddenUsernamesValidator(value):
    forbidden_usernames = ['admin', 'settings', 'news', 'about', 'help', 'signin', 'signup',
                           'signout', 'terms', 'privacy', 'cookie', 'new', 'login', 'logout', 'administrator',
                           'join', 'account', 'username', 'root', 'blog', 'user', 'users', 'billing', 'subscribe',
                           'reviews', 'review', 'blog', 'blogs', 'edit', 'mail', 'email', 'home', 'job', 'jobs',
                           'contribute', 'newsletter', 'shop', 'profile', 'register', 'auth', 'authentication',
                           'campaign', 'config', 'delete', 'remove', 'forum', 'forums', 'download', 'downloads',
                           'contact', 'blogs', 'feed', 'faq', 'intranet', 'log', 'registration', 'search',
                           'explore', 'rss', 'support', 'status', 'static', 'media', 'setting', 'css', 'js',
                           'follow', 'activity', 'library']
    if value.lower() in forbidden_usernames:
        raise ValidationError("This is a reserved word.")


def InvalidUsernameValidator(value):
    if '@' in value or '+' in value or '-' in value:
        raise ValidationError("Enter a valid username.")


def UniqueEmailValidator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this Email already exists.')


def UniqueUsernameIgnoreCaseValidator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('User with this Username already exists.')


class UserRegisterForm(forms.ModelForm):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = [
            'username',
            # 'first_name',
            # 'last_name',
            'email',
            'password',
            'confirm_password'
        ]

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].validators.append(ForbiddenUsernamesValidator)
        self.fields['username'].validators.append(InvalidUsernameValidator)
        self.fields['username'].validators.append(UniqueUsernameIgnoreCaseValidator)
        self.fields['email'].validators.append(UniqueEmailValidator)

    def clean(self):
        super(UserRegisterForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(['Passwords don\'t match'])
        return self.cleaned_data
