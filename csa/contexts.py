from csa.finance.payments import get_user_balance


def registration_moderation(request):
    return {
        'CSA_USER_REGISTRATION_MODERATION': True
    }


def user_balance(request):
    ctx = {}

    if request.user.is_authenticated:
        ctx['user_balance'] = get_user_balance(request.user)

    return ctx
