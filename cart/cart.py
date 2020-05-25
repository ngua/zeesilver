from django.conf import settings


class ListingUnavailable(Exception):
    pass


class Cart:
    # Used to retrieve an existing session cart, if any
    KEY = getattr(settings, 'CART_KEY', 'CART')

    def __init__(self, session):
        self.session = session  # Django request.session object
        self._items = {}  # Maps Listing pks to their prices
        if self.KEY in self.session:
            # If the key is already in the session, the cart exists and
            # must be rebuilt from the serialized items stored as its value
            pks = self.session[self.KEY]
            self._rebuild_cart(pks)

    def __iter__(self):
        for item in self.items:
            instance = self.query_db(item)
            yield instance

    def __contains__(self, item):
        return item in self.items

    def __repr__(self):  # pragma: no cover
        return f"Cart('{self.items}')"

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

    def _rebuild_cart(self, serialized_cart):
        """
        If the cart has been stored in the session, rebuild the cart using
        the Listing instance pks stored therein
        """
        pks = serialized_cart
        if not pks:
            return
        for pk in pks:
            instance = self.query_db(pk)
            self.add(instance, existing=True)

    def update(self):
        """
        Stores a representation of the cart in the session and updates it.
        This method should be called whenever cart items are modified in some
        way, in order to maintain an up-to-date cart representation in the
        session
        Calling `session.modified` is not necessary here, as one of its keys is
        directly modified
        """
        self.session[self.KEY] = self.serialize()

    def query_db(self, pk):
        """
        Retrieves the Listing instance associated with the pk passed as a
        parameter
        """
        from listings.models import Listing
        return Listing.objects.get(pk=pk)

    def add(self, instance, existing=False):
        """
        To add individual Listing instances to the cart's items. It first
        performs some checks - if the the instance's pk is already in the
        cart, it simply returns; if the instance is sold AND does not exist
        in the cart's serialized representation as indicated by the `existing`
        kwarg, it raises an exception that will ultimately percolate up into a
        404 error on the client side; finally, if the Listing instance is not
        in the serialized cart, it is marked as sold; the listing is then added
        to the cart's items
        Since each Listing instance is unique, checking that it is not
        already sold is necessary
        """
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
        """
        If the Listing instance's pk is not in in the cart's items, simply
        returns to avoid unnecessary db call and Celery search_vector update
        task. Otherwise unmarks the items as sold and removes the associated
        key from the cart's item dictionary
        """
        if instance.pk not in self.items:
            return
        instance.sold = False
        instance.save()
        self._items.pop(instance.pk)
        self.update()

    def clear(self):
        """
        Removes all items in the cart by calling the `remove` method for each
        item. This is necessary since each item will have to be marked as
        unsold, which requires a db call
        """
        items = self._items.copy()
        for item in items:
            instance = self.query_db(item)
            self.remove(instance)
        self.update()

    def serialize(self):
        """
        Produces a list of Listing instance pks. This will be stored as a
        representation of the cart in the session in order to rebuild the cart
        on subsequent requests. Can't use the `items` attribute directly,
        since dict keys can't be pickled. It only serializes instance pks as
        Money objects cannot be pickled
        """
        return [item for item in self._items]
