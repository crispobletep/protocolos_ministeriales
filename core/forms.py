from django import forms
from .models import Empresas
from .models import Protocolos, Evaluaciones
from .models import Oportunidadmejora


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = [
            'razon_social',
            'nombre_experto_prevencion_riesgos',
            'nro_trabajadores_empresa',
            'numero_de_contrato',
            'gerencia',
            'superintendencia',
            'nombre_admin_contrato_antucoya',
            'nombre_admin_contrato_empresa_contratista',
            'correo_admin_ec',
        ]


class OportunidadmejoraForm(forms.ModelForm):
    id_item_seleccionado = forms.IntegerField(widget=forms.HiddenInput())  # Campo oculto para almacenar el id_item

    class Meta:
        model = Oportunidadmejora
        fields = ['id_item_seleccionado', 'actividad', 'porcentajeavance', 'responsable', 'fechainicio', 'fechatermino']
        widgets = {
            'actividad': forms.TextInput(),
            'porcentajeavance': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
            'fechainicio': forms.DateInput(attrs={'type': 'date'}),
            'fechatermino': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_porcentajeavance(self):
        porcentaje = self.cleaned_data['porcentajeavance']
        if porcentaje < 1 or porcentaje > 100:
            raise forms.ValidationError("El porcentaje debe estar entre 1 y 100.")
        return porcentaje
