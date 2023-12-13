from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def change_password(request):
    #creating the view for changing your password when logged in.
    if request.method == 'POST':
        # initialize the correct form
        form = PasswordChangeForm(request.user, request.POST)
        # if form is filled out correctly save the form, give out an appropriate message for the user.
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Dein Passwort wurde erfolgreich geändert.')
            return redirect('change_password')
        else:
        # if form isn't filled out correctly give out an appropraite message for the user so that they can change their input.
            messages.error(request, 'Bitte korrigiere deine Fehler.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password/change_password.html', {
        'form': form
    })
