from django.db import models
from django.contrib.auth.models import User
# Create your models here.

STATE_LIST_CHOICES = (
	("","Select State"),
	("AL","Alabama"),
	("AK","Alaska"),
	("AZ","Arizona"),
	("AR","Arkansas"),
	("CA","California"),
	("CO","Colorado"),
	("CT","Connecticut"),
	("DE","Delaware"),
	("DC","District Of Columbia"),
	("FL","Florida"),
	("GA","Georgia"),
	("HI","Hawaii"),
	("ID","Idaho"),
	("IL","Illinois"),
	("IN","Indiana"),
	("IA","Iowa"),
	("KS","Kansas"),
	("KY","Kentucky"),
	("LA","Louisiana"),
	("ME","Maine"),
	("MD","Maryland"),
	("MA","Massachusetts"),
	("MI","Michigan"),
	("MN","Minnesota"),
	("MS","Mississippi"),
	("MO","Missouri"),
	("MT","Montana"),
	("NE","Nebraska"),
	("NV","Nevada"),
	("NH","New Hampshire"),
	("NJ","New Jersey"),
	("NM","New Mexico"),
	("NY","New York"),
	("NC","North Carolina"),
	("ND","North Dakota"),
	("OH","Ohio"),
	("OK","Oklahoma"),
	("OR","Oregon"),
	("PA","Pennsylvania"),
	("RI","Rhode Island"),
	("SC","South Carolina"),
	("SD","South Dakota"),
	("TN","Tennessee"),
	("TX","Texas"),
	("UT","Utah"),
	("VT","Vermont"),
	("VA","Virginia"),
	("WA","Washington"),
	("WV","West Virginia"),
	("WI","Wisconsin"),
	("WY","Wyoming")
	)

COUNTRY_CHOICES = (
	("United States","United States"),
	)

class Vendor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=200)
	company_name = models.CharField(max_length=200)
	company_social_link = models.CharField(max_length=250, null=True, blank=True)
	email = models.EmailField()
	phone = models.CharField(max_length=200)
	mobile = models.CharField(max_length=200)
	country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, default="United States")
	state = models.CharField(max_length=200, choices=STATE_LIST_CHOICES)
	city = models.CharField(max_length=200)
	address = models.TextField()
	zipcode = models.CharField(max_length=200)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.full_name

	def get_name(self):
		return self.full_name


class VendorDocument(models.Model):
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	document = models.FileField(upload_to="vendor_document")

	def __str__(self):
		return self.title

