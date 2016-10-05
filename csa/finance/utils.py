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


def account_balance(account):
    balance = 0

    for entry in LedgerEntry.objects.filter(account=account):
        if entry.type == LedgerEntry.TYPE_DEBIT:
            balance -= entry.amount
        elif entry.type == LedgerEntry.TYPE_CREDIT:
            balance += entry.amount
        else:
            raise Exception

    return balance


def get_user_account(user, account_type):
    account, created = Account.objects.get_or_create(
        user=user,
        type=account_type)

    return account
