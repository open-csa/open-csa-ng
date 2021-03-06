from django.db import models
from csa.models.user import User
from csa.models.utils import CSACharField
import csa.finance.utils

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

    def __lt__(self, other):
        return self.id < other.id


class Product(models.Model):
    UNIT_BUNCH = 1
    UNIT_WEIGHT = 2

    UNITS = (
        (UNIT_BUNCH, 'Μάτσο'),
        (UNIT_WEIGHT, 'Κιλό'),
    )

    categories = models.ManyToManyField(ProductCategory)
    name = CSACharField(unique=True)
    description = models.TextField()
    unit = models.IntegerField(choices=UNITS)

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
    min_quantity = models.FloatField(null=True)
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

    def get_overhead_price(self, percent=None):
        return self.price + csa.finance.utils.transaction_cut(
            amount=self.price,
            percent=percent)


class AvailableQuantity(models.Model):
    class Meta:
        unique_together = ('product_stock', 'quantity')

    product_stock = models.ForeignKey(
        ProductStock,
        related_name='available_quantities')
    quantity = models.FloatField()


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

    def total_price_uncut(self):
        return sum(item.total_price_uncut() for item in self.items.all())


class Cart(CartAndOrderCommon):
    user = models.OneToOneField(User)


class Order(CartAndOrderCommon):
    class Meta:
        ordering = ['-created_at']

    user = models.ForeignKey(User)
    order_period = models.ForeignKey(OrderPeriod)
    delivery_location = models.ForeignKey(DeliveryLocation)
    transaction_cut_percent = models.FloatField()

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
        price_uncut = self.total_price_uncut()
        return price_uncut + csa.finance.utils.transaction_cut(price_uncut)

    def total_price_uncut(self):
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
        price_uncut = self.total_price_uncut()
        return price_uncut + csa.finance.utils.transaction_cut(
            price_uncut,
            percent=self.order.transaction_cut_percent)

    def total_price_uncut(self):
        if self.quantity_fulfilled is None:
            quantity = self.quantity
        else:
            quantity = self.quantity_fulfilled

        return quantity * self.product_stock.price
