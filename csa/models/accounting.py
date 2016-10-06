from django.db import models
from csa.models.user import User


class Account(models.Model):
    class Meta:
        unique_together = (('type', 'user'),)

    # TODO: change this to "POCKET" account or something
    TYPE_ASSET_BANK_ACCOUNT = 1
    TYPE_LIABILITY_USER_BALANCE = 2

    TYPES = (
        (TYPE_ASSET_BANK_ACCOUNT, 'Asset Bank Account'),
        (TYPE_LIABILITY_USER_BALANCE, 'Liability User Balance'),
    )

    type = models.IntegerField(choices=TYPES)
    user = models.ForeignKey(User)


class Transaction(models.Model):
    TYPE_BALANCE_DEPOSIT = 1
    TYPE_PRODUCTS_PURCHASE = 2
    TYPE_PRODUCTS_REFUND = 3
    TYPE_TRANSACTION_CUT = 4
    TYPE_TRANSACTION_CUT_REFUND = 5
    TYPE_BALANCE_WITHDRAW = 6

    TYPES = (
        (TYPE_BALANCE_DEPOSIT, 'Balance Deposit'),
        (TYPE_BALANCE_WITHDRAW, 'Balance Withdraw'),
        (TYPE_PRODUCTS_PURCHASE, 'Products Purchase'),
        (TYPE_PRODUCTS_REFUND, 'Products Refund'),
        (TYPE_TRANSACTION_CUT, 'Transaction Cut'),
        (TYPE_TRANSACTION_CUT_REFUND, 'Transaction Cut Refund'),
    )

    type = models.IntegerField(choices=TYPES)
    amount = models.PositiveIntegerField()


class LedgerEntry(models.Model):
    class Meta:
        unique_together = (('transaction', 'account'))

    TYPE_DEBIT = 1
    TYPE_CREDIT = 2
    TYPES = (
        (TYPE_DEBIT, 'Debit'),
        (TYPE_CREDIT, 'Credit')
    )

    type = models.IntegerField(choices=TYPES)
    account = models.ForeignKey(Account)
    transaction = models.ForeignKey(Transaction)
    amount = models.PositiveIntegerField()
