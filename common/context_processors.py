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
