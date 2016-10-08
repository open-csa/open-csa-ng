from csa.models.finance import Payment, PaymentByHand
from csa.models.accounting import Account
from csa.finance import transactions
import csa.finance.utils


def get_user_balance(user):
    return csa.finance.utils.get_user_account_amount(
        user,
        Account.TYPE_LIABILITY_USER_BALANCE)


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


def user_withdraw_by_hand(user, amount):
    transaction = transactions.balance_withdraw(user, amount)
    payment = Payment.objects.create(
        type=Payment.TYPE_WITHDRAW,
        status=Payment.STATUS_COMPLETE,
        method=Payment.METHOD_BY_HAND,
        transaction=transaction,
        user=user)

    payment_by_hand = PaymentByHand.objects.create(payment=payment)
    return payment_by_hand
