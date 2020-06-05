from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from ckeditor.widgets import CKEditorWidget
from solo.admin import SingletonModelAdmin
from .models import UserProxy, Carousel, Slide


admin.site.unregister(FlatPage)


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


class SlideInline(admin.StackedInline):
    model = Slide


@admin.register(Carousel)
class CarouselAdmin(SingletonModelAdmin):
    inlines = (SlideInline,)


admin.site.register(Slide)
admin.site.register(UserProxy, UserAdmin)
