from django.shortcuts import render
from listings.models import Category
from .models import Carousel


def index(request):
    examples = Category.objects.get_example_listings()
    # Carousel is a singleton model
    carousel = Carousel.get_solo()
    context = {'examples': examples, 'carousel': carousel}
    return render(request, 'common/index.html', context=context)


# Errors


def handler_404(request, exception):
    status = 404
    return render(request, 'errors/404.html', {'status': status})


def handler_403(request, exception):
    status = 403
    return render(request, 'errors/403.html', {'status': status})


def handler_500(request):
    status = 500
    return render(request, 'errors/500.html', {'status': status})
