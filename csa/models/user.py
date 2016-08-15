from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from registration.signals import user_registered


class Producer(models.Model):
    pass

    def __str__(self):
        return self.profile.user.username


class Consumer(models.Model):
    preferred_delivery_location = models.ForeignKey('DeliveryLocation')

    def __str__(self):
        return self.profile.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile')

    phone_number = PhoneNumberField()

    producer = models.OneToOneField(
        Producer,
        on_delete=models.CASCADE,
        related_name='profile',
        blank=True,
        null=True)

    consumer = models.OneToOneField(
        Consumer,
        on_delete=models.CASCADE,
        related_name='profile',
        blank=True,
        null=True)

    def __str__(self):
        return self.user.username


# TODO: put this in a better place
def user_registered_callback(sender, user, request, **kwargs):
    # fix this hack that avoids cirqular deps
    from csa.models.core import DeliveryLocation
    for attr in ['first_name', 'last_name']:
        setattr(user, attr, request.POST[attr])

    user.save()

    # set user profile
    profile = UserProfile(user=user)
    profile.phone_number = request.POST['phone_number']
    preferred_delivery_location = DeliveryLocation.objects.get(
        pk=request.POST['preferred_delivery_location'])

    consumer = Consumer.objects.create(
        preferred_delivery_location=preferred_delivery_location)
    profile.consumer = consumer
    profile.save()

user_registered.connect(user_registered_callback)
