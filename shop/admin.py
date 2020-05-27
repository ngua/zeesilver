from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'number', 'name', 'email', 'address', 'total', 'status', 'created'
    )
    list_filter = ('status', 'created')

    def listings(self, obj):
        return ', '.join(obj.listing_set.all())

    def has_add_permission(self, request):
        return False

    class Meta:
        ordering = ('-created',)
