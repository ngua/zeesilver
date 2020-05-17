from .cart import Cart

def cart(request):
    cart = Cart(request.session)
    return {
        'cart': cart
    }
