from django import forms
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import csa.models as m
from csa.orders import OrdersManager
from csa import utils


class FinalizeOrderItemForm(forms.Form):
    order_item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity_fulfilled = forms.FloatField(
        label='',
        min_value=0,
        required=False)


FinalizeOrderItemFormSet = forms.formset_factory(
    FinalizeOrderItemForm)


@staff_member_required
def finalize(request, order_period_id):
    # check if order period is already finalized
    # or if order period is not over yet
    order_period = OrdersManager.get_order_period(order_period_id)
    now = utils.datetime_now()
    possible_errors = (
        (
            order_period.status == m.core.OrderPeriod.STATUS_FINALIZED,
            'Η επιλεγμένη περίοδος παραγγελιών έχει ήδη οριστικοποιηθεί'
        ),
        (
            order_period.ends_at > now,
            'Η επιλεγμένη περίοδος παραγγελιών δεν έχει τελειώσει ακόμα'
        )
    )

    errors = [error for error in possible_errors if error[0]]
    for error in errors:
        messages.error(request, error[1])

    if errors:
        return redirect('admin:csa_orderperiod_changelist')

    # TODO: logic flow here is weird
    formset = None
    if request.method == 'POST':
        formset = FinalizeOrderItemFormSet(request.POST)
        if formset.is_valid():
            fulfillment_data = [
                (data['order_item_id'], data['quantity_fulfilled'])
                for data in formset.cleaned_data
                if data['quantity_fulfilled'] is not None
            ]

            is_finalized = OrdersManager.set_order_items_fulfillment(
                order_period_id, fulfillment_data)

            messages.success(
                request,
                'Επιτυχής καταχώρηση δεδομένων οριστικοποίησης')

            if is_finalized:
                messages.success(
                    request,
                    'Η περίοδος παραγγελιών οριστικοποιήθηκε')

            return redirect('admin:csa_orderperiod_changelist')

    order_items = OrdersManager.get_unfulfilled_order_items(order_period_id)

    if not formset:
        formset_initial = [
            {'order_item_id': order_item.id}
            for order_item in order_items
        ]

        formset = FinalizeOrderItemFormSet(initial=formset_initial)

    # group by producer
    # can't do defaultdict here because jinja doesn't like them
    # noqa see http://stackoverflow.com/questions/4764110/django-template-cant-loop-defaultdict
    producer_order_items = {}
    for order_item, form in zip(order_items, formset):
        producer = order_item.product_stock.producer
        order_item.form = form

        if producer not in producer_order_items:
            producer_order_items[producer] = []

        producer_order_items[producer].append(order_item)

    return render(request, 'admin/order_item/finalize.html', {
        'producer_order_items': producer_order_items,
        'formset': formset
    })


# class DepositByHandForm(forms.Form):
#     amount = forms.FloatField()


# def deposit_by_hand(request, user_id):
#     selected_user = User.objects.get(pk=user_id)
#     if request.method == 'POST':
#         form = DepositByHandForm(request.POST)
#         if form.is_valid():
#             amount = form.cleaned_data['amount']
#             user_deposit_by_hand(selected_user, amount)
#             # TODO: dont hardcode this
#             return redirect('/admin/csa/consumer/')
#     else:
#         form = DepositByHandForm()

#     return render(request, 'admin/user/deposit_by_hand.html', {
#         'form': form,
#         'selected_user': selected_user
#     })
