from django import forms
from .models import CustomUser


class SignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    email = forms.EmailField(label="Correo electrónico")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    ROLES = [
        ('empresa_contratista', 'Empresa Contratista'),
        ('mandatario', 'Mandatario'),
    ]

    # Error de indentación en la línea siguiente
    rol = forms.ChoiceField(choices=ROLES, required=True,
                            help_text='Requerido. Ingrese una dirección de correo electrónico válida.')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'nombre', 'rol']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2



