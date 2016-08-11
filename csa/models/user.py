from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from registration.signals import user_registered


class Producer(models.Model):
    pass

    def __str__(self):
        return self.profile.user.username


class Consumer(models.Model):
    preferred_delivery_location = models.OneToOneField('DeliveryLocation')

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


def user_registered_callback(sender, user, request, **kwargs):
    profile = UserProfile(user=user)
    for attr in ['first_name', 'last_name', 'phone_number']:
        setattr(profile, attr, request.POST[attr])

    profile.save()

user_registered.connect(user_registered_callback)
