from collections import namedtuple
from djmoney.money import Money
from listings.models import Category


def in_stock(request):
    return {
        'categories_in_stock': Category.objects.in_stock()
    }


def price_points(request):
    return {
        'prices': [Money(i, 'USD') for i in range(100, 400, 100)]
    }


def carousel(request):
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
    return {
        'carousel': carousel
    }
