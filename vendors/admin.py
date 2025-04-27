from django.contrib import admin
from .models import VendorService, VendorBooking

admin.site.register(VendorService)
admin.site.register(VendorBooking)
