from copy import copy
from django.conf import settings


CART_KEY = getattr(settings, 'CART_KEY', 'CART')


class ListingUnavailable(Exception):
    pass


class Cart:
    def __init__(self, session):
        self.session = session
        self._items = {}
        self.key = CART_KEY
        if self.key in self.session:
            serialized_cart = self.session[self.key]
            self._rebuild_cart(serialized_cart)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        from listings.models import Listing
        for item in self.items:
            instance = Listing.objects.get(pk=item)
            yield instance

    def _rebuild_cart(self, serialized_cart):
        pks = serialized_cart
        if not pks:
            return
        for pk in pks:
            instance = self.query_db(pk)
            self.add(instance, existing=True)

    def query_db(self, pk):
        from listings.models import Listing
        return Listing.objects.get(pk=pk)

    def update(self):
        self.session[self.key] = self.serialize()
        self.session.modified = True

    def add(self, instance, existing=False):
        if instance.pk in self.items:
            return
        if instance.sold and not existing:
            raise ListingUnavailable(
                'This listing is not longer available'
            )
        if not existing:
            instance.sold = True
            instance.save()

        self._items.update({
            instance.pk: instance.price
        })
        self.update()

    def remove(self, instance):
        if instance.pk not in self.items:
            return
        instance.sold = False
        instance.save()
        self._items.pop(instance.pk)
        self.update()

    def clear(self):
        items = copy(self._items)
        for item in items:
            instance = self.query_db(item)
            self.remove(instance)
        self.update()

    def serialize(self):
        return [item for item in self._items]

    @property
    def count(self):
        return len(self._items)

    @property
    def total(self):
        return sum([price for price in self._items.values()])

    @property
    def is_empty(self):
        return not self._items

    @property
    def items(self):
        return self._items.keys()
