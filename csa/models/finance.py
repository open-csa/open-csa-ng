from django.db import models
from csa.models.user import User
from csa.models.accounting import Transaction


class Payment(models.Model):
    TYPE_DEPOSIT = 1
    TYPE_WITHDRAWAL = 2
    TYPES = (
        (TYPE_DEPOSIT, 'Deposit'),
        (TYPE_WITHDRAWAL, 'Widthdrawal')
    )

    STATUS_PENDING = 1
    STATUS_COMPLETE = 2
    STATUS_FAILED = 3
    STATUSES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed')
    )

    METHOD_BY_HAND = 1
    METHODS = (
        (METHOD_BY_HAND, 'By hand'),
    )

    user = models.ForeignKey(User)
    transaction = models.OneToOneField(Transaction)
    status = models.IntegerField(choices=STATUSES)
    method = models.IntegerField(choices=METHODS)
    type = models.IntegerField(choices=TYPES)


class PaymentByHand(models.Model):
    payment = models.OneToOneField(Payment)
