from csa.models.finance import Payment, PaymentByHand
from csa.models.accounting import Transaction, LedgerEntry, Account
from csa.utils import get_company_user


def get_user_account(user, account_type):
    return Account.objects.get_or_create(user=user, type=account_type)[0]


def get_account_amount(user, account_type):
    account = get_user_account(user, account_type)
    amount = 0

    for entry in LedgerEntry.objects.filter(account=account):
        if entry.type == LedgerEntry.TYPE_DEBIT:
            amount -= entry.amount
        elif entry.type == LedgerEntry.TYPE_CREDIT:
            amount += entry.amount
        else:
            raise Exception

    return amount


def get_user_balance(user):
    return get_account_amount(user, Account.TYPE_LIABILITY_USER_BALANCE)


def user_deposit_by_hand(user, amount):
    company_user = get_company_user()
    user_deposits_acc = get_user_account(
        user,
        Account.TYPE_LIABILITY_USER_BALANCE)

    company_asset_account = get_user_account(
        company_user,
        Account.TYPE_ASSET_BANK_ACCOUNT)

    transaction = Transaction.objects.create(
        type=Transaction.TYPE_CONSUMER_PURCHASE,
        description='{username}'.format(username=user.username),
        amount=amount)

    ledger_entries = [
        LedgerEntry.objects.create(
            type=LedgerEntry.TYPE_CREDIT,
            account=user_deposits_acc,
            amount=amount,
            transaction=transaction),
        LedgerEntry.objects.create(
            type=LedgerEntry.TYPE_DEBIT,
            account=company_asset_account,
            amount=amount,
            transaction=transaction)
    ]

    payment = Payment.objects.create(
        type=Payment.TYPE_DEPOSIT,
        status=Payment.STATUS_COMPLETE,
        method=Payment.METHOD_BY_HAND,
        transaction=transaction,
        user=user,
        amount=amount)

    payment_by_hand = PaymentByHand.objects.create(payment=payment)

    return payment_by_hand
