from registration.forms import RegistrationForm
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from csa.models.core import DeliveryLocation


class RegistrationForm(RegistrationForm):
    first_name = forms.CharField(label='Όνομα')
    last_name = forms.CharField(label='Επώνυμο')
    phone_number = PhoneNumberField(
        label='Τηλέφωνο',
        widget=PhoneNumberInternationalFallbackWidget)
    preferred_delivery_location = forms.ModelChoiceField(
        queryset=DeliveryLocation.objects.all(),
        label='Προτιμητέο σημείο παράδοσης')
