from ..forms import UserRegisterForm
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login, logout,
    update_session_auth_hash
)
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def api_user_registration_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.data)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            new_user = authenticate(username=user.username, password=password)
            return Response({
                "status": "ok",
                })
        else:
            return Response({
                "status": "notok",
                })
    return Response({"status": "Bad Request"})