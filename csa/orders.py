"""MAGIC"""
from dateutil.relativedelta import relativedelta
from collections import namedtuple
from csa import models as m
from csa import utils
from csa import exceptions

OrderPeriodSpan = namedtuple('OrderPeriodSpan', ['starts_at', 'ends_at'])


class OrdersManager:
    @classmethod
    def get_non_empty_carts(cls):
        # TODO: query only for non empty
        return (
            cart for cart in m.core.Cart.objects.all()
            if cart.items.values
        )

    @classmethod
    def ensure_order_periods(cls):
        delivery_locations = m.core.DeliveryLocation.objects.all()
        for loc in delivery_locations:
            cls.ensure_order_periods_for_delivery_location(loc)

    @classmethod
    def get_next_delivery(cls, delivery_location):
        """Get the next delivery datetime for the given delivery location."""

        starts_at = cls.get_next_datetime_in_future(
            delivery_location.delivery_weekday,
            delivery_location.delivery_time)

        return OrderPeriodSpan(
            starts_at=starts_at,
            ends_at=starts_at + relativedelta(weeks=1))

    @classmethod
    def get_next_deadline(cls, delivery_location):
        starts_at = cls.get_next_datetime_in_future(
            delivery_location.orders_deadline_weekday,
            delivery_location.orders_deadline_time)

        return OrderPeriodSpan(
            starts_at=starts_at,
            ends_at=starts_at + relativedelta(weeks=1))

    @classmethod
    def get_current_order_period(cls, delivery_location):
        next_delivery_span = cls.get_next_delivery(delivery_location)
        starts_at = next_delivery_span.starts_at - relativedelta(weeks=1)

        order_period, created = m.core.OrderPeriod.objects.get_or_create(
            delivery_location=delivery_location,
            starts_at=starts_at,
            defaults={
                # TODO: this can be after the deadline too, handle that
                'status': m.core.OrderPeriod.STATUS_PENDING,
                'ends_at': next_delivery_span.starts_at
            })

        return order_period

    @classmethod
    def ensure_order_periods_for_delivery_location(cls, delivery_location):
        last_order_period = cls.get_current_order_period(delivery_location)

        # see if last order needs to be set to NO_MORE_ORDERS
        cls.check_no_more_orders(last_order_period)

        # fill holes with canceled order periods if needed
        # get next delivery (in future)
        cls.fill_order_period_holes(
            delivery_location,
            last_order_period,
            last_order_period.starts_at)

    @classmethod
    def get_next_datetime_in_future(cls, weekday, time):
        now = utils.datetime_now()
        if now.weekday() == weekday and now.time() < time:
            now += relativedelta(weeks=1)

        dt = now + relativedelta(
            weekday=weekday)

        return dt.replace(
            hour=time.hour,
            minute=time.minute)

    @classmethod
    def check_no_more_orders(cls, order_period):
        # this applies only to pending order periods
        if order_period.status != m.core.STATUS_PENDING:
            return

        delivery_location = order_period.delivery_location
        orders_deadline_at = cls.get_next_datetime_in_future(
            delivery_location.orders_deadline_weekday,
            delivery_location.orders_deadline_time)

        if orders_deadline_at < utils.datetime_now():
            order_period.status = m.core.OrderPeriod.STATUS_NO_MORE_ORDERS
            order_period.save()

    @classmethod
    def fill_order_period_holes(
            cls, delivery_location, last_order_period, until_at):
        tmp_date = last_order_period.ends_at
        while tmp_date < until_at:
            next_week = tmp_date + relativedelta(weeks=1)
            m.core.OrderPeriod.objects.update_or_create(
                delivery_location=delivery_location,
                starts_at=tmp_date,
                ends_at=next_week,
                defaults={
                    'status': m.core.OrderPeriod.STATUS_CANCELED
                })
            tmp_date = next_week

    # TODO: this isn't used
    # @classmethod
    # def carts_to_orders(cls, associated_order_period):
    #     """
    #     Converts all carts to orders.
    #     """
    #     for cart in cls.get_non_empty_carts():
    #         order = m.core.Order.objects.create(
    #             comment=cart.comment,
    #             user=cart.user,
    #             order_period=associated_order_period)
    #         # TODO: crazy db ops here
    #         for item in cart.items.all():
    #             order.items.create(
    #                 product_stock=item.product_stock,
    #                 quantity=item.quantity,
    #                 order=order)

    #         # now empty cart
    #         m.core.CartItem.objects.filter(cart=cart).delete()

    @classmethod
    def cancel_order_period(cls, order_period):
        # TODO: crazy db ops here
        # instead we can delete all CartItems and also get back the deleted
        # records (need to see how django ORM does that) and then we can
        # perform extra operations on top of these, like notify users.
        if order_period.status != m.core.OrderPeriod.STATUS_PENDING:
            raise ValueError('can only cancel pending order periods')

        order_period.status = m.core.OrderPeriod.STATUS_CANCELED

        carts = cls.get_non_empty_carts()
        for cart in carts:
            m.core.CartItem.objects.filter(cart=cart).delete()
            # TODO: notify users

    @classmethod
    def checkout(cls, cart):
        cart_items = cart.items.all()
        if not cart_items:
            raise exceptions.CartIsEmptyError('cart is empty')

        delivery_location = (
            cart.user.profile.consumer
            .preferred_delivery_location)

        order_period = cls.get_current_order_period(delivery_location)
        order = m.core.Order.objects.create(
            comment=cart.comment,
            user=cart.user,
            order_period=order_period)

        # TODO: crazy db ops here
        for item in cart_items:
            order.items.create(
                product_stock=item.product_stock,
                quantity=item.quantity,
                order=order)

        # now empty cart
        m.core.CartItem.objects.filter(cart=cart).delete()

        return order
