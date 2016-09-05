from django.db import models
from csa.models.user import User
from csa.models.utils import CSACharField

# TODO: split this module into actual pieces


class DeliveryLocation(models.Model):
    name = CSACharField(unique=True)
    address = CSACharField()

    # by extension only weekly deliveries are available
    # zero index weekday
    delivery_weekday = models.IntegerField()
    delivery_time = models.TimeField()
    # expressed in seconds
    delivery_duration = models.IntegerField()
    orders_deadline_weekday = models.IntegerField()
    orders_deadline_time = models.TimeField()

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

    producer = models.ForeignKey(User, on_delete=models.CASCADE)
    variety = CSACharField()
    price = models.PositiveIntegerField()
    # availability and stock related variables
    # default case, this item is available but not stockable
    is_available = models.BooleanField(default=True)
    is_stockable = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)
    # extra description for specific product from producer
    description = models.TextField()
    supported_delivery_locations = models.ManyToManyField(DeliveryLocation)

    def __str__(self):
        return 'ProductStock(id={id})'.format(id=self.id)


class OrderPeriod(models.Model):
    class Meta:
        unique_together = ('delivery_location', 'starts_at')

    STATUS_PENDING = 1
    STATUS_NO_MORE_ORDERS = 2
    STATUS_FINALIZED = 3
    STATUS_CANCELED = 4
    STATUSES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_NO_MORE_ORDERS, 'No more orders'),
        (STATUS_FINALIZED, 'Finalized'),
        (STATUS_CANCELED, 'Canceled')
    )

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    delivery_location = models.ForeignKey(DeliveryLocation)
    status = models.IntegerField(choices=STATUSES)

    def __str__(self):
        # probably time is not so relevant
        return '{start}—{end}—{status}'.format(
            start=self.starts_at.date(),
            end=self.ends_at.date(),
            status=self.get_status_display())


class CartAndOrderCommon(models.Model):
    class Meta:
        abstract = True

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())


class Cart(CartAndOrderCommon):
    user = models.OneToOneField(User)


class Order(CartAndOrderCommon):
    user = models.ForeignKey(User)
    order_period = models.ForeignKey(OrderPeriod)
    delivery_location = models.ForeignKey(DeliveryLocation)

    def __str__(self):
        return 'Order(id={id})'.format(id=self.id)


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

    order = models.ForeignKey(Order, related_name='items')
    product_stock_price = models.PositiveIntegerField()

    # this is filled later when the administrator describes the fulfillment
    # result
    quantity_fulfilled = models.FloatField(null=True)

    def total_price(self):
        if self.quantity_fulfilled is None:
            quantity = self.quantity
        else:
            quantity = self.quantity_fulfilled

        return quantity * self.product_stock_price
