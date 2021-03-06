import itertools
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
            form_kwargs = {
                'initial': {'stock_id': stock.id},
                'min_quantity': stock.min_quantity,
                'quantities': stock.available_quantities.all()
            }

            if stock.is_stockable and stock.quantity > 0:
                form_kwargs['max_quantity'] = stock.quantity

            stock.cart_add_form = AddProductForm(**form_kwargs)

    products = sorted(products, key=lambda p: p.categories.all()[0])
    return render(request, 'products/index.html', {
        'products': products
    })
