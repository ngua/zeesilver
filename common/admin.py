from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Merchant


class MerchantInline(admin.StackedInline):
    model = Merchant
    can_delete = False
    verbose_name_plural = 'merchant'


class UserAdmin(UserAdmin):
    inlines = (MerchantInline,)

    def get_inlines(self, request, obj):
        if obj.is_merchant:
            return self.inlines
        return []


admin.site.register(User, UserAdmin)
