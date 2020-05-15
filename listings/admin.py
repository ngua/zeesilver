from django.contrib import admin
from .models import Category, Listing, Material


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sold', 'price')
    list_filter = ('category', 'sold', 'materials')

    class Meta:
        ordering = ('-created',)


admin.site.register(Category)
admin.site.register(Material)
