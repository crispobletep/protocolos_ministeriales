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
    class Meta:
        model = Oportunidadmejora
        fields = ['id_item', 'actividad', 'porcentajeavance', 'responsable', 'fechainicio', 'fechatermino']