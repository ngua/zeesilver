from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import SquareConfig


@admin.register(SquareConfig)
class SquareConfigAdmin(SingletonModelAdmin):
    """
    Set all fields to read-only to ensure that instance can only be changed
    through views
    """
    fields = ['created', 'expires', 'active']

    def has_change_permission(self, request, obj=None):
        return False
