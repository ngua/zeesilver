def cancel_order(instance, cart, key, session):
    """
    Calls soft delete method of Order instance and clears session cart
    """
    cart.clear()
    instance.soft_delete()
    del session[key]
