import locale
from django import template
from django.core.urlresolvers import reverse
from csa import utils
import csa.settings
from csa.finance.payments import get_user_balance


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


@register.simple_tag()
def absurl(view_name, *args, **kwargs):
    return csa.settings.SITE_URL + reverse(view_name, args=args, kwargs=kwargs)


@register.filter()
def balance(user):
    return currency(get_user_balance(user))
