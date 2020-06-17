from django.contrib import admin
from .models import Category, Listing, Material


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sold', 'price', 'display_materials')
    list_filter = ('category', 'sold', 'materials')
    readonly_fields = ('order', 'slug')

    def display_materials(self, obj):
        """
        `list_display` can't display m2m relations
        """
        return ', '.join([
            str(material) for material in obj.materials.all()
        ])

    display_materials.short_description = 'Materials'

    class Meta:
        ordering = ('-created',)


admin.site.register(Category)
admin.site.register(Material)
