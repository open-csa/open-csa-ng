from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.db.models import F
from django.contrib import messages
from csa.orders import OrdersManager
from csa import models as m
from csa import utils


@login_required
def index(request):
    cart = utils.get_user_cart(request.user.id)

    return render(request, 'cart/index.html', {
        'cart': cart
    })


@login_required
@require_POST
def add(request):
    stock_id = int(request.POST['stock_id'])
    quantity = float(request.POST['quantity'])
    stock = m.core.ProductStock.objects.get(pk=stock_id)
    cart = utils.get_user_cart(request.user.id)
    item, created = cart.items.get_or_create(
        product_stock=stock,
        defaults={"quantity": quantity})
    # if the specific cart item was already present in
    # the cart, then just update the quantity
    if not created:
        item.quantity = F('quantity') + quantity
        item.save()

    return redirect('products-index')


@login_required
@require_POST
def clear(request):
    cart = utils.get_user_cart(request.user.id)
    m.core.CartItem.objects.filter(cart=cart).delete()
    return redirect('cart-index')


@login_required
@require_POST
def checkout(request):
    cart = utils.get_user_cart(request.user)
    order = OrdersManager.checkout(cart)
    messages.success(request, 'Επιτυχής καταχώρηση παραγγελίας')
    return redirect('orders-read', order_id=order.pk)


@login_required
@require_POST
def remove_item(request, cart_item_id):
    num_deleted = m.core.CartItem.objects.filter(id=cart_item_id).delete()
    if num_deleted == 0:
        messages.error(
            request,
            'Το συγκεκριμένο προϊόν δε βρέθηκε στο καλάθι σας')
    else:
        messages.success(
            request,
            'Επιτυχής αφαίρεση προϊόντος απο το καλάθι σας')

    return redirect('cart-index')
