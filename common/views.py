from collections import namedtuple
from django.shortcuts import render
from listings.models import Category


def index(request):
    items = [
        ['earrings', '100% pure Sterling silver.'],
        ['necklace', '100% hand-crafted.'],
        ['pendant', '100% unique.'],
        ['bracelets', 'Order now!']
    ]
    CarouselItem = namedtuple('CarouselItem', ['img', 'caption'])
    carousel = [
        CarouselItem(*item) for item in items
    ]
    examples = Category.objects.get_example_listings()
    context = {
        'carousel': carousel,
        'examples': examples
    }
    return render(request, 'common/index.html', context=context)
