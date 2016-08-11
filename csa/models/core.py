from django.db import models
from csa.models.user import User
from csa.models.utils import CSACharField

# TODO: split this module into actual pieces


class DeliveryLocation(models.Model):
    name = CSACharField(unique=True)
    address = CSACharField()

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    # set proper plural name
    class Meta:
        verbose_name_plural = "product categories"

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    name = CSACharField(unique=True)
    description = CSACharField(blank=True)

    def __str__(self):
        return self.name


class ProductMeasureUnit(models.Model):
    name = CSACharField()

    def __str__(self):
        return self.name


# TODO: how to handle container size?
class Product(models.Model):
    categories = models.ManyToManyField(ProductCategory)
    name = CSACharField(unique=True)
    description = models.TextField()
    unit = models.ForeignKey(ProductMeasureUnit)

    def __str__(self):
        return self.name


# TODO: keep log of these for stats of price changes
class ProductStock(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='stocks',
        on_delete=models.CASCADE)

    producer = models.OneToOneField(User, on_delete=models.CASCADE)
    variety = CSACharField()
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    # extra description for specific product from producer
    description = models.TextField()
    supported_delivery_locations = models.ManyToManyField(DeliveryLocation)


class CartAndOrderCommon(models.Model):
    class Meta:
        abstract = True

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(CartAndOrderCommon):
    user = models.OneToOneField(User)


class Order(CartAndOrderCommon):
    user = models.ForeignKey(User)


class CartAndOrderItem(models.Model):
    class Meta:
        abstract = True

    product_stock = models.ForeignKey(ProductStock)
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(CartAndOrderItem):
    class Meta:
        # one product per cart, that's why we have quantity
        unique_together = (('product_stock', 'cart'),)

    cart = models.ForeignKey(Cart, related_name='items')

    def total_price(self):
        return self.quantity * self.product_stock.price


class OrderItem(CartAndOrderItem):
    class Meta:
        unique_together = (('product_stock', 'order'),)

    # TODO: on_delete what?
    # TODO: product or product stock? crutial logic decision
    # TODO: copy product item details here. this is permanent order
    order = models.ForeignKey(Order, related_name='items')
