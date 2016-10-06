from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from csa import models as m


@login_required
def list(request):
    payments = m.finance.Payment.objects.filter(user=request.user).all()
    return render(request, 'payments/list.html', {
        'payments': payments
    })
