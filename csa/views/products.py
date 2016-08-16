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
        .filter(stocks__is_available=True)
        .all())

    for product in products:
        for stock in product.stocks.all():
            # if the product is stockable create a form with limit
            # on the quantity
            if stock.is_stockable and stock.quantity > 0:
                stock.cart_add_form = AddProductForm(
                    max_limit=stock.quantity,
                    initial={'stock_id': stock.id})
            else:
                stock.cart_add_form = AddProductForm(
                    initial={'stock_id': stock.id})

    return render(request, 'products/index.html', {
        'products': products
    })
