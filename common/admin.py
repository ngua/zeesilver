from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from solo.admin import SingletonModelAdmin
from .models import User, Carousel, Slide


class SlideInline(admin.StackedInline):
    model = Slide


@admin.register(Carousel)
class CarouselAdmin(SingletonModelAdmin):
    inlines = (SlideInline,)


admin.site.register(Slide)
admin.site.register(User, UserAdmin)
