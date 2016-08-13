from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import F
from csa import models
from csa import utils


@login_required
def index(request):
    cart = utils.get_user_cart(request.user.id)

    return render(request, 'cart/index.html', {
        'cart': cart
    })


@login_required
def add(request):
    stock_id = int(request.POST['stock_id'])
    stock = models.core.ProductStock.objects.get(pk=stock_id)
    cart = utils.get_user_cart(request.user.id)
    item, created = cart.items.get_or_create(
        product_stock=stock,
        defaults={"quantity": 1})
    if not created:
        item.quantity = F('quantity') + 1
        item.save()

    return redirect('products-index')


@login_required
def clear(request):
    if request.method != 'POST':
        # TODO: raise appropriate exception
        raise Exception

    cart = utils.get_user_cart(request.user.id)
    models.core.CartItem.objects.filter(cart=cart).delete()
    return redirect('cart-index')
