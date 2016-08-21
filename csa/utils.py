from csa.models.user import User
from csa.models.core import Cart
from datetime import datetime
import pytz


def datetime_now():
    return datetime.now(pytz.utc)


def get_user_by_username(username):
    return User.objects.get(username=username)


def get_company_user():
    return User.objects.get(pk=1)


def get_user_cart(user_id):
    return Cart.objects.get_or_create(user_id=user_id)[0]
