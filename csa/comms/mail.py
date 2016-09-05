from templated_email import send_templated_mail
import csa.settings


def _send_templated_mail(template_name, user, context=None):
    if context is None:
        context = {
            'user': user
        }
    else:
        context['user'] = user

    send_to = user.email
    return send_templated_mail(
        template_name=template_name,
        from_email=csa.settings.CSA_EMAIL_FROM,
        recipient_list=(send_to,),
        context=context,
        template_prefix='comms/mail/',
        template_suffix='')


def send_order_confirmation_mail(user, order):
    return _send_templated_mail('order_confirmation', user, {
        'order': order
    })


def send_producer_new_order_mail(user, order_items):
    return _send_templated_mail('producer_order_notification', user, {
        'order_items': order_items,
        'delivery_location': order_items[0].order.delivery_location
    })


def send_balance_deposit_mail(user, payment):
    return _send_templated_mail('user_balance_deposit', user, {
        'payment': payment
    })


def send_order_item_fulfillment_change_mail(
        user, order_item, paid_quantity, transaction):
    return _send_templated_mail('order_item_fulfillment_change', user, {
        'order_item': order_item,
        'paid_quantity': paid_quantity,
        'transaction': transaction
    })
