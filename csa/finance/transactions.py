import itertools
import csa.models as m
from csa.models.accounting import Account
from csa import utils


def get_user_account(user, account_type):
    account, created = Account.objects.get_or_create(
        user=user,
        type=account_type)

    return account


def create_transaction(
        *,
        type,
        amount,
        debit_user,
        debit_account_type,
        credit_user,
        credit_account_type):
    debit_account = get_user_account(debit_user, debit_account_type)
    credit_account = get_user_account(credit_user, credit_account_type)

    transaction = m.accounting.Transaction.objects.create(
        type=type,
        amount=amount)

    ledger_entries = [
        m.accounting.LedgerEntry.objects.create(
            type=m.accounting.LedgerEntry.TYPE_CREDIT,
            account=credit_account,
            amount=amount,
            transaction=transaction),
        m.accounting.LedgerEntry.objects.create(
            type=m.accounting.LedgerEntry.TYPE_DEBIT,
            account=debit_account,
            amount=amount,
            transaction=transaction)
    ]

    return transaction


def balance_deposit(user, amount):
    return create_transaction(
        type=m.accounting.Transaction.TYPE_BALANCE_DEPOSIT,
        credit_user=user,
        credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
        debit_user=utils.get_company_user(),
        debit_account_type=Account.TYPE_ASSET_BANK_ACCOUNT,
        amount=amount)


def _order_item_key_producer(order_item):
    return order_item.product_stock.producer.id


def products_purchase(order):
    # group order items by producer
    consumer = order.user
    order_items = sorted(order.items.all(), key=_order_item_key_producer)
    order_items_by_producer = itertools.groupby(
        order_items,
        key=_order_item_key_producer)

    for producer, order_items in order_items_by_producer:
        amount = sum(item.total_price() for item in order_items)
        transaction = create_transaction(
            type=m.accounting.Transaction.TYPE_PRODUCTS_PURCHASE,
            amount=amount,
            credit_user=producer,
            credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
            debit_user=consumer,
            debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE
        )


def order_item_fulfillment_changed(order_item, diff_quantity):
    producer = order_item.product_stock.producer
    consumer = order_item.order.user

    if diff_quantity > 0:
        transaction_type = m.accounting.Transaction.TYPE_PRODUCTS_PURCHASE
        credit_user = producer
        debit_user = consumer
    else:
        transaction_type = m.accounting.Transaction.TYPE_PRODUCTS_REFUND
        credit_user = consumer
        debit_user = producer

    amount = abs(diff_quantity) * order_item.product_stock.price
    create_transaction(
        type=transaction_type,
        amount=amount,
        credit_user=credit_user,
        credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
        debit_user=debit_user,
        debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE)
