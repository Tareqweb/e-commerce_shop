"""hishop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from home.views import (
    home, 
    about_us, 
    faq_us,
    privacy_policy,
    terms_of_use,
    refund_return_policy,
    contact_us,
    send_messages
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/v1/', include('products.api.urls')),
    path('api/v1/auth/', include('auth.api.urls')),
    path('api/v1/orders/', include('orders.api.urls')),
    path('api/v1/myaccount/', include('myaccount.api.urls')),
    path('', home, name='home'),
    path('about-us/', about_us, name='about_us'),
    path('faq/', faq_us, name='faq_us'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-of-use/', terms_of_use, name='terms_of_use'),
    path('contact-us/', contact_us, name='contact_us'),
    path('refund-return-policy/', refund_return_policy, name='refund_return_policy'),
    path('send_messages/', send_messages, name='send_messages'),
    path('', include('products.urls')),
    path('', include('orders.urls')),
    path('', include('dashboard.urls')),
    path('', include('myaccount.urls')),
    path('', include('vendors.urls')),
    path('account/', include("auth.urls"))
]

if settings.DEBUG:
    # test mode
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
