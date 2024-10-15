from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from .views import api_user_registration_view

urlpatterns = [
    path('login/', obtain_auth_token, name="api-login"),
    path('registration/', api_user_registration_view, name="api-registration")
]