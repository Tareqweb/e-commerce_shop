from .models import Category, SubCategory, ProductCategory
from dashboard.models import MobileApps
def categories(request):
	return {
		'apps': MobileApps.objects.last(),
		'categories': Category.objects.all().order_by("position")
	}