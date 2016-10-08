from csa.models import accounting
import csa.finance.utils
import csa.utils
from csa.models.accounting import Account, LedgerEntry


class LedgerEntryData:
    def __init__(self, type, reason, user, account_type, amount):
        self.type = type
        self.reason = reason
        self.user = user
        self.account_type = account_type
        self.amount = amount


def create_transaction(*, type, amount, entries):
    transaction = accounting.Transaction.objects.create(
        type=type,
        amount=amount)

    total_debits = 0
    total_credits = 0

    for entry in entries:
        if entry.type == LedgerEntry.TYPE_DEBIT:
            total_debits += entry.amount
        else:
            total_credits += entry.amount

        accounting.LedgerEntry.objects.create(
            type=entry.type,
            reason=entry.reason,
            account=csa.finance.utils.get_user_account(
                entry.user,
                entry.account_type),
            transaction=transaction,
            amount=entry.amount)

    if total_debits != total_credits:
        raise Exception('total_debits != total_credits')

    return transaction


def create_two_entry_transaction(
        *,
        type,
        amount,
        debit_user,
        debit_account_type,
        debit_reason,
        credit_user,
        credit_account_type,
        credit_reason):

    return create_transaction(
        type=accounting.Transaction.TYPE_BALANCE_DEPOSIT,
        amount=amount,
        entries=[
            LedgerEntryData(
                type=LedgerEntry.TYPE_CREDIT,
                user=credit_user,
                account_type=credit_account_type,
                amount=amount,
                reason=credit_reason),
            LedgerEntryData(
                type=LedgerEntry.TYPE_DEBIT,
                user=debit_user,
                account_type=debit_account_type,
                amount=amount,
                reason=debit_reason)
        ])


def balance_deposit(user, amount):
    return create_two_entry_transaction(
        type=accounting.Transaction.TYPE_BALANCE_DEPOSIT,
        credit_user=user,
        credit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
        credit_reason=LedgerEntry.REASON_BALANCE_DEPOSIT,
        debit_user=csa.utils.get_company_user(),
        debit_account_type=Account.TYPE_ASSET_CASH,
        debit_reason=LedgerEntry.REASON_BALANCE_DEPOSIT,
        amount=amount)


def balance_withdraw(user, amount):
    return create_two_entry_transaction(
        type=accounting.Transaction.TYPE_BALANCE_WITHDRAW,
        credit_user=csa.utils.get_company_user(),
        credit_account_type=Account.TYPE_ASSET_CASH,
        credit_reason=LedgerEntry.REASON_BALANCE_WITHDRAW,
        debit_user=user,
        debit_account_type=Account.TYPE_LIABILITY_USER_BALANCE,
        debit_reason=LedgerEntry.REASON_BALANCE_WITHDRAW,
        amount=amount)


def products_purchase_order_item(order_item, amount_uncut, refund=False):
    consumer = order_item.order.user
    company = csa.utils.get_company_user()
    amount = order_item.total_price()
    producer = order_item.product_stock.producer

    transaction_cut_amount = csa.finance.utils.transaction_cut(amount_uncut)

    entries = [
        LedgerEntryData(
            user=consumer,
            type=LedgerEntry.TYPE_DEBIT,
            account_type=Account.TYPE_LIABILITY_USER_BALANCE,
            amount=amount_uncut + transaction_cut_amount,
            reason=LedgerEntry.REASON_PRODUCTS_PURCHASE),
        LedgerEntryData(
            user=producer,
            type=LedgerEntry.TYPE_CREDIT,
            account_type=Account.TYPE_LIABILITY_USER_BALANCE,
            amount=amount_uncut - transaction_cut_amount,
            reason=LedgerEntry.REASON_PRODUCTS_PURCHASE),
        LedgerEntryData(
            user=company,
            type=LedgerEntry.TYPE_CREDIT,
            account_type=Account.TYPE_REVENUE_TRANSACTION_CUT,
            amount=transaction_cut_amount * 2,
            reason=LedgerEntry.REASON_TRANSACTION_CUT),
    ]

    if refund:
        transaction_type = accounting.Transaction.TYPE_PRODUCTS_PURCHASE_REFUND
        # reverse all entries to be refunds
        for entry in entries:
            if entry.type == LedgerEntry.TYPE_DEBIT:
                entry.type = LedgerEntry.TYPE_CREDIT
            else:
                entry.type = LedgerEntry.TYPE_DEBIT

            if entry.reason == LedgerEntry.REASON_PRODUCTS_PURCHASE:
                entry.reason = LedgerEntry.REASON_PRODUCTS_PURCHASE_REFUND
            elif entry.reason == LedgerEntry.REASON_TRANSACTION_CUT:
                entry.reason = LedgerEntry.REASON_TRANSACTION_CUT_REFUND
            else:
                raise Exception
    else:
        transaction_type = accounting.Transaction.TYPE_PRODUCTS_PURCHASE

    return create_transaction(
        type=transaction_type,
        amount=amount,
        entries=entries)


def products_purchase(order):
    for order_item in order.items.all():
        products_purchase_order_item(
            order_item,
            amount_uncut=order_item.total_price_uncut())
