import locale
from datetime import datetime
import pytz
import csa.models as m


def datetime_now():
    return datetime.now(pytz.utc)


def get_user_by_username(username):
    return m.user.User.objects.get(username=username)


def get_company_user():
    return m.user.User.objects.get(username='admin')


def get_user_cart(user_id):
    return m.core.Cart.objects.get_or_create(user_id=user_id)[0]


def human_readable_cents(amount):
    return locale.currency(amount / 100, grouping=True)
