from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import CustomUser
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        return redirect('/profile')  # Redirigir al perfil si el usuario ya está autenticado
    return render(request, 'home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            try:
                # Intenta crear un nuevo usuario
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                messages.success(request, '¡Registro exitoso! Ahora estás conectado.')
                return redirect('/signin')
            except Exception as e:
                # Manejar errores, por ejemplo, si el correo electrónico ya está en uso.
                messages.error(request, f'Error en el registro: {str(e)}')
        else:
            # Manejar errores de validación del formulario
            messages.error(request, 'Error en el formulario de registro. Por favor, corrige los errores.')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def signin(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)  # Autenticación del usuario

            if user is not None:
                login(request, user)
                messages.success(request, '¡Inicio de sesión exitoso!')
                return redirect('/profile')  # Redirigir al perfil después del inicio de sesión exitoso
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
        else:
            messages.error(request, 'Error en el formulario de inicio de sesión. Por favor, corrige los errores.')

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('home')  # Redirigir a la página de inicio si el usuario no está autenticado
    return render(request, 'profile.html')


def signout(request):
    logout(request)
    return redirect('home')  # Redirigir a la página de inicio después de cerrar sesión
