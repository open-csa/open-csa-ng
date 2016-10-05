import itertools
import csa.models as m
import csa.finance.utils
import csa.utils
from csa.models.accounting import Account


def create_transaction(
        *,
        type,
        amount,
        debit_user,
        debit_account_type,
        credit_user,
        credit_account_type):
    debit_account = csa.finance.utils.get_user_account(
        debit_user,
        debit_account_type)
    credit_account = csa.finance.utils.get_user_account(
        credit_user,
        credit_account_type)

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
        debit_user=csa.utils.get_company_user(),
        debit_account_type=Account.TYPE_ASSET_BANK_ACCOUNT,
        amount=amount)


def products_purchase(order):
    # group order items by producer
    consumer = order.user
    company = csa.utils.get_company_user()

    order_items = sorted(
        order.items.all(),
        key=lambda order_item: order_item.product_stock.producer.id)

    order_items_by_producer = itertools.groupby(
        order_items,
        key=lambda order_item: order_item.product_stock.producer)

    for producer, order_items in order_items_by_producer:
        amount = sum(item.total_price_uncut() for item in order_items)
        create_transaction(
            type=m.accounting.Transaction.TYPE_PRODUCTS_PURCHASE,
            amount=amount,
            credit_user=producer,
            credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
            debit_user=consumer,
            debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE)

        # producer transaction cut
        transaction_cut_amount = csa.finance.utils.transaction_cut(
            amount)

        create_transaction(
            type=m.accounting.Transaction.TYPE_TRANSACTION_CUT,
            amount=transaction_cut_amount,
            credit_user=company,
            credit_account_type=Account.TYPE_ASSET_BANK_ACCOUNT,
            debit_user=producer,
            debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE)

    # consumer transaction cut
    transaction_cut_amount = csa.finance.utils.transaction_cut(
        order.total_price_uncut())

    create_transaction(
        type=m.accounting.Transaction.TYPE_TRANSACTION_CUT,
        amount=transaction_cut_amount,
        credit_user=company,
        credit_account_type=m.accounting.Account.TYPE_ASSET_BANK_ACCOUNT,
        debit_user=consumer,
        debit_account_type=m.accounting.Account.TYPE_LIABILITY_USER_BALANCE)


def order_item_fulfillment_changed(order_item, diff_quantity):
    producer = order_item.product_stock.producer
    consumer = order_item.order.user
    company = csa.utils.get_company_user()

    if diff_quantity > 0:
        order_transaction_type = (
            m.accounting.Transaction.TYPE_PRODUCTS_PURCHASE)
        order_credit_user = producer
        order_debit_user = consumer
        cut_transaction_type = m.accounting.Transaction.TYPE_TRANSACTION_CUT
        cut_credit_user = company
        cut_credit_account = m.accounting.Account.TYPE_ASSET_BANK_ACCOUNT
        cut_debit_user = consumer
        cut_debit_account = m.accounting.Account.TYPE_LIABILITY_USER_BALANCE
        producer_cut_credit_user = company
        producer_cut_debit_user = producer
    else:
        order_transaction_type = m.accounting.Transaction.TYPE_PRODUCTS_REFUND
        order_credit_user = consumer
        order_debit_user = producer
        cut_transaction_type = (
            m.accounting.Transaction.TYPE_TRANSACTION_CUT_REFUND)
        cut_credit_user = consumer
        cut_credit_account = m.accounting.Account.TYPE_LIABILITY_USER_BALANCE
        cut_debit_user = company
        cut_debit_account = m.accounting.Account.TYPE_ASSET_BANK_ACCOUNT
        producer_cut_credit_user = producer
        producer_cut_debit_user = company

    order_amount = abs(diff_quantity) * order_item.product_stock_price
    transaction_cut = csa.finance.utils.transaction_cut(order_amount)

    # create order transaction
    create_transaction(
        type=order_transaction_type,
        amount=order_amount,
        credit_user=order_credit_user,
        credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
        debit_user=order_debit_user,
        debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE)

    # create consumer transaction cut transaction
    create_transaction(
        type=cut_transaction_type,
        amount=transaction_cut,
        credit_user=cut_credit_user,
        credit_account_type=cut_credit_account,
        debit_user=cut_debit_user,
        debit_account_type=cut_debit_account)

    # create producer transaction cut transaction
    create_transaction(
        type=cut_transaction_type,
        amount=transaction_cut,
        credit_user=producer_cut_credit_user,
        credit_account_type=cut_credit_account,
        debit_user=producer_cut_debit_user,
        debit_user_account=cut_debit_account)
