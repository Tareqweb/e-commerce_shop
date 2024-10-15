from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from dashboard.models import (
	ProductSlider, 
	MobileApps,
	AboutUs,
	FAQ,
	PrivacyPolicy,
	TermsOfUse,
	RefundReturnPolicy,
	ContactUs
	)

def home(request):
	template_name = "home.html"
	sliders = ProductSlider.objects.all().order_by("-id")
	context = {
		"sliders":sliders,
	}
	return render(request,template_name,context)


def about_us(request):
	template_name = "pages.html"
	xobject = AboutUs.objects.last()
	context = {
		"xobject":xobject,
		"title":"About Us",
	}
	return render(request,template_name,context)


def faq_us(request):
	template_name = "faq.html"
	faqs = FAQ.objects.all()
	context = {
		"faqs":faqs,
		"title":"FAQ",
	}
	return render(request,template_name,context)

def privacy_policy(request):
	template_name = "pages.html"
	xobject = PrivacyPolicy.objects.last()
	context = {
		"xobject":xobject,
		"title":"Privacy Policy",
	}
	return render(request,template_name,context)

def terms_of_use(request):
	template_name = "pages.html"
	xobject = TermsOfUse.objects.last()
	context = {
		"xobject":xobject,
		"title":"Terms Of Use",
	}
	return render(request,template_name,context)

def refund_return_policy(request):
	template_name = "pages.html"
	xobject = RefundReturnPolicy.objects.last()
	context = {
		"xobject":xobject,
		"title":"Refund Return Policy",
	}
	return render(request,template_name,context)


def contact_us(request):
	template_name = "contact_us.html"
	xobject = ContactUs.objects.last()
	context = {
		"xobject":xobject,
		"title":"Contact Us",
	}
	return render(request,template_name,context)


def send_messages(request):
	if request.method == "POST":
		name = request.POST.get("name")
		email = request.POST.get("email")
		phone = request.POST.get("phone")
		subject = request.POST.get("subject")
		message = request.POST.get("message")
		from_email = "noreply@bizoytech.com"
		to_email = []
		to_email.append(email)
		message_body = "Name: {}\nEnail: {}\nMessage: {}".format(name, email, message)
		send_mail(subject, message_body, from_email, to_email)
		messages.success(request, 'Message Sent')

	return redirect("/contact-us/")




