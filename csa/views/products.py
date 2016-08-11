from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from csa.models.core import Product
from csa.forms.cart import AddProductForm


@login_required
def index(request):
    # fetch products that support this delivery location only
    consumer = request.user.profile.consumer
    pref_delivery_loc = consumer.preferred_delivery_location
    products = (
        Product.objects.prefetch_related('stocks')
        .filter(stocks__supported_delivery_locations=pref_delivery_loc)
        .all())

    for product in products:
        for stock in product.stocks.all():
            stock.cart_add_form = AddProductForm(
                initial={'stock_id': stock.id})

    return render(request, 'products/index.html', {
        'products': products
    })
