import locale
from urllib.parse import urlencode
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from related_admin import RelatedFieldAdmin as ModelAdmin
from csa.finance.payments import get_user_balance
import csa.models as m
from csa import utils


admin.site.site_header = 'Διαχείρηση CSA'
admin.site.index_title = 'Λειτουργίες'
admin.site.site_title = 'Διαχeίρηση CSA'


def foreign_key_link(model_name, key, label=None):
    if label is None:
        label = model_name

    def _foreign_key_link(self, obj):
        link = reverse(
            "admin:csa_{model_name}_change".format(model_name=model_name),
            args=(getattr(obj, key + '_id'),))
        foreign_obj = getattr(obj, key)
        return mark_safe('<a href="{href}"">{label}</a>'.format(
            href=link,
            label=str(foreign_obj)))

    _foreign_key_link.short_description = label
    return _foreign_key_link


def one_to_many_link(model_name, key, label=None):
    if label is None:
        label = model_name

    def _one_to_many_link(self, obj):
        link = reverse("admin:csa_{model_name}_changelist".format(
                model_name=model_name))

        link = '{link}?{qs}'.format(
            link=link,
            qs=urlencode({
                '{key}__id__exact'.format(key=key): obj.id
            }))

        return mark_safe('<a href="{href}">{label}</a>'.format(
            href=link,
            label=label))

    _one_to_many_link.short_description = label
    return _one_to_many_link


class UserProfileInline(admin.StackedInline):
    model = m.user.UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(m.user.User)
admin.site.register(m.user.User, UserProfileAdmin)


@admin.register(m.core.Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'description', 'unit')


@admin.register(m.core.ProductStock)
class ProductStockAdmin(ModelAdmin):
    list_display = (
        'product',
        'producer_full_name',
        'is_available',
        'is_stockable',
        'quantity',
        'price')

    def producer_full_name(self, product_stock):
        return product_stock.producer.get_full_name()


class UserBaseModelAdmin(ModelAdmin):
    inlines = [UserProfileInline]
    list_display = (
        'user_full_name',
        'profile__phone_number',
        'profile__user__email',
        'balance')

    def balance(self, user):
        balance = get_user_balance(user.profile.user)
        return utils.human_readable_cents(balance)

    def user_full_name(self, user):
        return user.profile.user.get_full_name()


@admin.register(m.user.Producer)
class Producer(UserBaseModelAdmin):
    pass


@admin.register(m.user.Consumer)
class Consumer(UserBaseModelAdmin):
    actions = ['deposit_by_hand']

    def deposit_by_hand(self, request, queryset):
        user = queryset[0].profile.user
        return redirect(
            'admin-user-deposit-by-hand',
            user_id=user.id)


@admin.register(m.core.Order)
class Order(ModelAdmin):
    list_display = (
        'id',
        'user',
        'order_period',
        'total_price',
        'items_link',
        'created_at')

    items_link = one_to_many_link('orderitem', 'order', label='items')


@admin.register(m.core.OrderItem)
class OrderItem(ModelAdmin):
    list_display = (
        'id',
        'order_link',
        'product_stock_link',
        'quantity',
        'total_price',
        'created_at'
    )

    order_link = foreign_key_link('order', 'order')
    product_stock_link = foreign_key_link(
        'productstock',
        'product_stock',
        label='product stock')


@admin.register(m.core.OrderPeriod)
class OrderPeriod(ModelAdmin):
    list_display = (
        'id',
        'starts_at',
        'ends_at',
        'delivery_location_link',
        'status')
    actions = ('finalize',)

    delivery_location_link = foreign_key_link(
        'deliverylocation',
        'delivery_location',
        label='delivery location')

    def finalize(self, request, queryset):
        return redirect(
            'admin-order-period-finalize',
            order_period_id=queryset[0].id)


@admin.register(m.accounting.Transaction)
class Transaction(ModelAdmin):
    list_display = (
        'id',
        'type',
        'amount_currency')

    def amount_currency(self, transaction):
        return utils.human_readable_cents(transaction.amount)


# register simple models
for model in [
        m.core.DeliveryLocation,
]:
    admin.site.register(model)
