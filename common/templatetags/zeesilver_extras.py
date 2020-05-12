from django import template


register = template.Library()



@register.inclusion_tag('common/tags/materials.html')
def materials(listing):
    return {'listing': listing}


@register.inclusion_tag('common/tags/add_to_cart.html')
def add_to_cart(listing):
    return {'listing': listing}
