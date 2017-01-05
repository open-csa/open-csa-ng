import operator
import csa.settings
from csa.models.accounting import LedgerEntry, Account


# TODO: investigate if rounding is safe first
def transaction_cut(amount, _round=False, percent=None):
    if percent is None:
        percent = csa.settings.CSA_TRANSACTION_CUT_PERCENT

    amount = amount * percent
    if _round:
        # round integer by one digit, so 156 becomes 160
        amount = round(amount, -1)

    return amount


def get_account_amount(account, reverse=False):
    amount = 0

    if reverse:
        debit_op = operator.add
        credit_op = operator.sub
    else:
        debit_op = operator.sub
        credit_op = operator.add

    for entry in LedgerEntry.objects.filter(account=account):
        if entry.type == LedgerEntry.TYPE_DEBIT:
            amount = debit_op(amount, entry.amount)
        elif entry.type == LedgerEntry.TYPE_CREDIT:
            amount = credit_op(amount, entry.amount)
        else:
            raise Exception

    return amount


def get_user_account_amount(user, account_type, reverse=False):
    account = get_user_account(user, account_type)
    return get_account_amount(account, reverse)


def get_user_account(user, account_type):
    account, created = Account.objects.get_or_create(
        user=user,
        type=account_type)

    return account
