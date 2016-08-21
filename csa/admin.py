from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django import forms
from related_admin import RelatedFieldAdmin as ModelAdmin
from csa.finance.payments import get_user_balance
import csa.models as m


admin.site.site_header = 'Διαχείρηση CSA'
admin.site.index_title = 'Λειτουργίες'
admin.site.site_title = 'Διαχeίρηση CSA'


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
    list_display = ('product', 'producer', 'quantity', 'price')


@admin.register(m.user.Producer)
class Producer(ModelAdmin):
    inlines = [UserProfileInline]
    list_display = (
        'profile__user__username',
        'profile__phone_number',
        'profile__user__email')


@admin.register(m.user.Consumer)
class Consumer(ModelAdmin):
    inlines = [UserProfileInline]
    actions = ['deposit_by_hand']
    list_display = (
        'profile__user__username',
        'profile__phone_number',
        'profile__user__email',
        'balance')

    class DepositByHandForm(forms.Form):
        ammount = forms.FloatField()

    def deposit_by_hand(self, request, queryset):
        return redirect('admin-user-deposit-by-hand', 1)

    def balance(self, consumer):
        return get_user_balance(consumer.profile.user)


# register simple models
for model in [
        m.core.OrderPeriod,
        m.core.DeliveryLocation,
        m.core.Order
]:
    admin.site.register(model)
