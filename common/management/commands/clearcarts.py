from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from cart.cart import Cart


class Command(BaseCommand):
    """
    This command deletes expired sessions and clear any associated carts
    before deletion. It is intended to replace Django's built-in
    `clearsessions` management command. An alternative would be performing both
    tasks independently, however clearing carts on sessions would require
    modifiying SessionStore objects outside of the view/response context.
    """
    help = 'Clears expired sessions and their associated carts'

    def handle(self, *args, **options):
        sessions = Session.objects.filter(expire_date__lte=timezone.now())
        for session in sessions:
            session_data = session.get_decoded()
            cart = Cart(session_data)
            cart.clear()
            session.delete()
        self.stdout.write(self.style.SUCCESS(
            'Successfully cleared expired sessions and associated carts'
        ))
