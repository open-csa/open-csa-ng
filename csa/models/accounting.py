
from django.db import models
from csa.models.user import User


class Account(models.Model):
    class Meta:
        unique_together = (('type', 'user'),)

    TYPE_ASSET_CASH = 1
    TYPE_LIABILITY_USER_BALANCE = 2
    TYPE_REVENUE_TRANSACTION_CUT = 3

    TYPES = (
        (TYPE_ASSET_CASH, 'Asset Cash'),
        (TYPE_LIABILITY_USER_BALANCE, 'Liability User Balance'),
        (TYPE_REVENUE_TRANSACTION_CUT, 'Revenue Transaction Cut'),
    )

    type = models.IntegerField(choices=TYPES)
    user = models.ForeignKey(User)


class Transaction(models.Model):
    TYPE_BALANCE_DEPOSIT = 1
    TYPE_PRODUCTS_PURCHASE = 2
    TYPE_PRODUCTS_PURCHASE_REFUND = 3
    TYPE_BALANCE_WITHDRAW = 4

    TYPES = (
        (TYPE_BALANCE_DEPOSIT, 'Balance Deposit'),
        (TYPE_BALANCE_WITHDRAW, 'Balance Withdraw'),
        (TYPE_PRODUCTS_PURCHASE, 'Products Purchase'),
        (TYPE_PRODUCTS_PURCHASE_REFUND, 'Products Purchase Refund'),
    )

    type = models.IntegerField(choices=TYPES)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LedgerEntry(models.Model):
    class Meta:
        unique_together = (('transaction', 'account'))

    TYPE_DEBIT = 1
    TYPE_CREDIT = 2
    TYPES = (
        (TYPE_DEBIT, 'Debit'),
        (TYPE_CREDIT, 'Credit')
    )

    REASON_BALANCE_DEPOSIT = 1
    REASON_TRANSACTION_CUT = 2
    REASON_TRANSACTION_CUT_REFUND = 3
    REASON_BALANCE_WITHDRAW = 4
    REASON_PRODUCTS_PURCHASE = 5
    REASON_PRODUCTS_PURCHASE_REFUND = 5

    REASONS = (
        (REASON_BALANCE_DEPOSIT, 'Balance Deposit'),
        (REASON_BALANCE_WITHDRAW, 'Balance Withdraw'),
        (REASON_TRANSACTION_CUT, 'Transaction Cut'),
        (REASON_TRANSACTION_CUT_REFUND, 'Transaction Cut Refund'),
        (REASON_PRODUCTS_PURCHASE, 'Products Purchase'),
        (REASON_PRODUCTS_PURCHASE_REFUND, 'Products Purchase Refund'),
    )

    type = models.IntegerField(choices=TYPES)
    reason = models.IntegerField(choices=REASONS)
    account = models.ForeignKey(Account)
    transaction = models.ForeignKey(Transaction)
    amount = models.PositiveIntegerField()
