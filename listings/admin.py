from django.contrib import admin
from .models import Category, Listing, Material


admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Listing)
