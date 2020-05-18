from django.shortcuts import render
from listings.models import Category


def index(request):
    examples = Category.objects.get_example_listings()
    context = {
        'examples': examples
    }
    return render(request, 'common/index.html', context=context)
