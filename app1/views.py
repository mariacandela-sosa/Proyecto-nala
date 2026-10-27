from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def inicio(request):
    return render(request, 'app1/index.html')


def registro(request):
    if request.user.is_authenticated:
        return redirect('hola')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('hola')

    return render(request, 'app1/registro.html', {'form': form})