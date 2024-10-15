from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .views import (
	login_view,
    vendor_login_view,
	register_view,
    vendor_register_view,
    admin_login_view,
	logout_view, 
	# change_password,
    password_reset_confirm
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('vendor/login/', vendor_login_view, name='vendor_login'),
    path('admin/login/', admin_login_view, name='admin_login'),
    path('register/', register_view, name='register'),
    path('vendor/register/', vendor_register_view, name='vendor_register'),
    # path('password/change/', change_password, name='change_password'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
