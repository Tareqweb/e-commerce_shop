from .models import SiteLogoAndTitle, ContactUs

def site_settings(request):
	return {
		'site_title': SiteLogoAndTitle.objects.last(),
		'contactus': ContactUs.objects.last()
	}