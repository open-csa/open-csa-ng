from django import forms
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from csa.models.user import User
from csa.finance.payments import user_deposit_by_hand
import csa.comms.mail


class DepositByHandForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2)

    def clean_amount(self):
        # convert to cents
        return self.cleaned_data['amount'] * 100


@staff_member_required
def deposit_by_hand(request, user_id):
    selected_user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        form = DepositByHandForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment = user_deposit_by_hand(selected_user, amount)
            # send email too
            csa.comms.mail.send_balance_deposit_mail(
                selected_user, payment)
            return redirect('admin:csa_consumer_changelist')
    else:
        form = DepositByHandForm()

    return render(request, 'admin/user/deposit_by_hand.html', {
        'form': form,
        'selected_user': selected_user
    })
