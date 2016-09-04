import locale
from django import template
from csa import utils


register = template.Library()
# use system locale
locale.setlocale(locale.LC_ALL, '')


@register.simple_tag(takes_context=True)
def active(context, url_name):
    if context.request.resolver_match.url_name == url_name:
        return 'active'
    return ''


@register.filter()
def currency(value):
    return utils.human_readable_cents(value)
