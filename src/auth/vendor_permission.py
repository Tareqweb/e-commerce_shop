from functools import wraps
from django.http import Http404
from vendors.models import Vendor


def vendor_permission_requird(function):
	@wraps(function)
	def wrap(request, *args, **kwargs):
		try:
			vendor = Vendor.objects.get(user=request.user)
		except Exception as e:
			raise Http404("Only Vendor can access")

		if vendor:
			return function(request, *args, **kwargs)
		else:
			raise Http404("Only Vendor can access")
	return wrap


def super_user_permission_requird(function):
	@wraps(function)
	def wrap(request, *args, **kwargs):
		try:
			super_user = True if request.user.is_superuser else False
		except Exception as e:
			raise Http404("Only Admin can access")

		if super_user:
			return function(request, *args, **kwargs)
		else:
			raise Http404("Only Admin can access")
	return wrap


def super_user_and_vendor_permission_requird(function):
	@wraps(function)
	def wrap(request, *args, **kwargs):
		try:
			if request.user.is_superuser or request.user.vendor:
				access = True
		except Exception as e:
			raise Http404("Only vendor or Admin can access")

		if access:
			return function(request, *args, **kwargs)
		else:
			raise Http404("Only vendor or Admin can access")
	return wrap



