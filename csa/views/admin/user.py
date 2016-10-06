from django import forms
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from csa.models.user import User
from csa.finance import payments
import csa.comms.mail


class DepositByHandForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2)

    def clean_amount(self):
        # convert to cents
        return self.cleaned_data['amount'] * 100


@staff_member_required
def deposit_by_hand(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        form = DepositByHandForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment = payments.user_deposit_by_hand(user, amount)
            # send email too
            csa.comms.mail.send_balance_deposit_mail(
                user, payment)
            return redirect('admin:csa_consumer_changelist')
    else:
        form = DepositByHandForm()

    return render(request, 'admin/user/payment_by_hand.html', {
        'form': form,
        'user': user,
        'payment_type': 'deposit',
    })


@staff_member_required
def withdraw_by_hand(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        # user deposit form, it's the same thing
        form = DepositByHandForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment = payments.user_withdraw_by_hand(user, amount)
            # send email too
            csa.comms.mail.send_balance_withdraw_mail(user, payment)
            return redirect('admin:csa_consumer_changelist')
    else:
        form = DepositByHandForm()

    return render(request, 'admin/user/payment_by_hand.html', {
        'form': form,
        'user': user,
        'payment_type': 'withdrawal',
    })
