from django.shortcuts import render
from listings.models import Category
from .models import Carousel


def index(request):
    examples = Category.objects.get_example_listings()
    # Carousel is a singleton model
    carousel = Carousel.get_solo()
    context = {
        'examples': examples,
        'carousel': carousel
    }
    return render(request, 'common/index.html', context=context)
