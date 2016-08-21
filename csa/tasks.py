from celery import shared_task
from csa.orders import OrdersManager
from django.db import transaction


@shared_task
# not sure what happens with tasks and transactions. better safe than sorry
@transaction.atomic
def ensure_order_periods():
    OrdersManager.ensure_order_periods()
