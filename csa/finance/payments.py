from csa.models.finance import Payment, PaymentByHand
from csa.models.accounting import LedgerEntry, Account
from csa.finance import transactions
import csa.finance.utils


def get_account_amount(user, account_type):
    account = transactions.get_user_account(user, account_type)
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
    account = csa.finance.utils.get_user_account(
        user,
        Account.TYPE_LIABILITY_USER_BALANCE)

    return csa.finance.utils.account_balance(account)


def user_deposit_by_hand(user, amount):
    transaction = transactions.balance_deposit(user, amount)

    payment = Payment.objects.create(
        type=Payment.TYPE_DEPOSIT,
        status=Payment.STATUS_COMPLETE,
        method=Payment.METHOD_BY_HAND,
        transaction=transaction,
        user=user)

    payment_by_hand = PaymentByHand.objects.create(payment=payment)
    return payment_by_hand
