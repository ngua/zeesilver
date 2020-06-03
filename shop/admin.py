import csv
from django.urls import reverse
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Order, Shipment, Payment


class CSVAdminMixin:
    """
    Mixin to generate CSV files for given qs
    """
    actions = ['export']

    def export(self, request, queryset):
        """
        Custom action to create CSV from qs
        """
        opts = self.opts
        # Create response object and set content header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="{opts.verbose_name}.csv"'
        )
        # Exclude related models from exported fields
        fields = [
            field for field in opts.get_fields()
            if not field.one_to_many and not field.one_to_one
        ]
        writer = csv.writer(response)
        writer.writerow([field.verbose_name for field in fields])
        for instance in queryset:
            writer.writerow([
                getattr(instance, field.name) for field in fields
            ])
        return response

    export.short_description = 'Export to CSV file'


class ShipmentInline(admin.TabularInline):
    """
    Create a Shipment instance from related order
    """
    model = Shipment
    fields = ('tracking',)
    show_change_link = True


class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ('receipt_number', 'receipt_url')
    readonly_fields = ('receipt_number', 'receipt_url')
    show_change_link = True


@admin.register(Order)
class OrderAdmin(CSVAdminMixin, admin.ModelAdmin):
    list_display = (
        'number', 'name', 'email', 'address', 'total', 'status',
        'created', 'items', 'invoice', 'receipt', 'tracking'
    )
    list_filter = ('status', 'created')
    inlines = [ShipmentInline, PaymentInline]

    def has_add_permission(self, request):
        return False

    @staticmethod
    def invoice(obj):
        url = reverse('shop:invoice', kwargs={'token': obj.token()})
        return format_html(
            '<a href={}>{}</a>', url, 'Invoice'
        )

    @staticmethod
    def receipt(obj):
        return format_html(
            '<a href={}>{}</a>', obj.payment.receipt_url, 'Receipt'
        )

    def tracking(self, obj):
        return obj.shipment.tracking

    invoice.short_description = 'Invoice'

    def items(self, obj):
        return ', '.join(
            [listing.name for listing in obj.listing_set.all()]
        )

    class Meta:
        ordering = ('-created',)


@admin.register(Shipment)
class ShipmentAdmin(CSVAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(CSVAdminMixin, admin.ModelAdmin):
    pass
