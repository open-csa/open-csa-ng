from django.forms import ModelForm
from csa.models.user import UserProfile, User, Consumer


class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserProfileEditForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']


class ConsumerEditForm(ModelForm):
    class Meta:
        model = Consumer
        fields = ['preferred_delivery_location']
        labels = {
            'preferred_delivery_location': 'Προτιμιτέο σημείο παράδοσης'
        }
