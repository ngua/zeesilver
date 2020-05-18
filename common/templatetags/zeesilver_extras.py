from django import template


register = template.Library()


@register.inclusion_tag('common/tags/materials.html')
def materials(listing):
    return {'listing': listing}


@register.inclusion_tag('common/tags/add_or_view.html')
def add_or_view(listing, size='fa-lg'):
    return {'listing': listing, 'size': size}


@register.inclusion_tag('common/tags/legend.html')
def legend(text, *classes):
    return {
        'text': text,
        'classes': classes
    }


@register.inclusion_tag('common/tags/filter_options.html', takes_context=True)
def filter_options(context, heading, **kwargs):
    return {
        'categories': context['categories_in_stock'],
        'current_category': context['current_category'],
        'current_price': context['current_price'],
        'current_order': context['current_order'],
        'prices': context['prices'],
        'page_obj': context['page_obj'],
        'heading': heading,
        'option': kwargs['option']
    }


@register.simple_tag
def filter_href(category, price, order, page):
    return (
        f'?category={category}&price__lte={price}'
        f'&order_by={order}&page={page}'
    )


@register.simple_tag
def search_pagination_href(q, page=1):
    return f'?q={q}&page={page}'


@register.inclusion_tag('common/tags/jumbotron.html')
def jumbotron(heading, lead, text=''):
    return {
        'heading': heading,
        'lead': lead,
        'text': text
    }


@register.filter
def quote(value):
    return f'"{value}"'
