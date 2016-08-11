from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from csa.forms import user as user_forms


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
