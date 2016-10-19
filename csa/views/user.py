from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import mail_admins
from registration.backends.hmac.views import RegistrationView
import registration.signals
from csa.forms import user as user_forms


class CSARegistrationView(RegistrationView):
    """Override email context."""
    def get_email_context(self, *args, **kwargs):
        ctx = super().get_email_context(*args, **kwargs)
        setting = settings.CSA_USER_REGISTRATION_MODERATION
        ctx['CSA_USER_REGISTRATION_MODERATION'] = setting
        return ctx


# TODO: not the best file to place this but whatever
@receiver(registration.signals.user_registered)
def new_user_mail_admins(sender, user, request, **kwargs):
    mail_admins(
        subject='Νέος χρήστης: ' + user.get_full_name(),
        message='Γιουυπιιιι!!')


@login_required
def edit(request):
    user = request.user
    data = request.POST or None

    forms = [
        user_forms.UserEditForm(
            data,
            instance=user),
        user_forms.UserProfileEditForm(
            data,
            instance=user.profile),
        user_forms.ConsumerEditForm(
            data,
            instance=user.profile.consumer)
    ]

    # if all forms are valid, save them
    if all(f.is_valid() for f in forms):
        for f in forms:
            f.save()

        messages.success(request, 'Επιτυχής αλλαγή στοιχείων')
        return redirect('user-edit')

    return render(request, 'user/edit.html', {
        'forms': forms
    })
