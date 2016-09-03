from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from csa import models as m


@login_required
def read(request, order_id):
    order = m.core.Order.objects.get(pk=order_id)
    return render(request, 'orders/read.html', {
        'order': order
    })


@login_required
def list(request):
    orders = m.core.Order.objects.filter(user=request.user).all()
    return render(request, 'orders/list.html', {
        'orders': orders
    })


@login_required
def list_for_producer(request):
    order_items = (
        m.core.OrderItem.objects
        .select_related('product_stock')
        .select_related('product_stock__producer')
        .filter(product_stock__producer=request.user)
    )

    return render(request, 'orders/list-for-producer.html', {
        'order_items': order_items
    })
