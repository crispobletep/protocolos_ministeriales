from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Avg, Sum, Count
from django.contrib.auth.forms import UserCreationForm
from .models import Empresas, Protocolosseleccionados, TitulosRequisitos
from .models import Protocolos, ItemsEvaluacion, ResultadosEvaluacion, Evaluaciones, Oportunidadmejora
from .forms import OportunidadmejoraForm, EmpresaForm
from django.http import JsonResponse
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


@login_required
def llenar_datos_empresa(request):
    if request.method == 'POST':
        empresa_form = EmpresaForm(request.POST)
        if empresa_form.is_valid():
            empresa = empresa_form.save(commit=False)
            empresa.save()

            # Asigna la empresa al usuario actual
            request.user.empresa = empresa
            request.user.is_company = True  # Establece is_company como True
            request.user.save()

            return redirect('profile')
    else:
        empresa_form = EmpresaForm()

    return render(request, 'llenar_datos_empresa.html', {'empresa_form': empresa_form})


@login_required
def seleccionar_protocolo(request):
    if not request.user.is_company:
        # Si el usuario no es una empresa, redirige al formulario de llenado de empresa
        return redirect('llenar_datos_empresa')  # Ajusta la URL a la correcta

    if request.method == 'POST':
        # Resto del código para seleccionar protocolos
        protocolos_seleccionados_ids = request.POST.getlist('protocolos[]')
        protocolos_seleccionados_ids = [p_id for p_id in protocolos_seleccionados_ids if p_id.isnumeric()]

        # Verifica los valores
        print("Protocolos seleccionados IDs:", protocolos_seleccionados_ids)

        # Verifica si hay duplicados en los IDs seleccionados
        if len(protocolos_seleccionados_ids) != len(set(protocolos_seleccionados_ids)):
            return JsonResponse({'error': 'No se pueden seleccionar protocolos duplicados'}, status=400)

        # Obtén los protocolos seleccionados desde la base de datos
        protocolos = Protocolos.objects.filter(id_protocolo__in=protocolos_seleccionados_ids)

        # Guarda los protocolos seleccionados en la tabla ProtocolosSeleccionados
        for protocolo in protocolos:
            Protocolosseleccionados.objects.create(protocolo=protocolo, estado='incompleto')

        return redirect('protocolos_seleccionados')
    else:
        # Resto del código para mostrar los protocolos disponibles
        protocolos = Protocolos.objects.all()
        return render(request, 'seleccionar_protocolo.html', {'protocolos': protocolos})


def protocolos_seleccionados(request):
    protocolos_seleccionados_query = Protocolosseleccionados.objects.all()
    return render(request, 'protocolos_seleccionados.html', {
        'protocolos_seleccionados_list': protocolos_seleccionados_query
    })


def eliminar_protocolo(request, pk):
    try:
        protocolo_seleccionado = Protocolosseleccionados.objects.get(pk=pk)
        # Elimina el protocolo seleccionado
        protocolo_seleccionado.delete()

        # Después de eliminar, muestra un mensaje de éxito
        messages.success(request, '¡Protocolo seleccionado eliminado exitosamente!')

    except Protocolosseleccionados.DoesNotExist:
        messages.error(request, 'El protocolo seleccionado no existe')

    return redirect('protocolos_seleccionados')


@login_required
def autoevaluacion(request, protocolo_id):
    try:
        protocolo_seleccionado = Protocolosseleccionados.objects.get(id=protocolo_id)

        if request.method == 'POST':
            if request.user.is_company and hasattr(request.user, 'empresa'):
                empresa = request.user.empresa
                evaluacion = Evaluaciones.objects.create(
                    id_empresa=empresa,
                    id_protocolo=protocolo_seleccionado.protocolo,
                    fecha_inicio_evaluacion=datetime.date.today(),
                    fecha_termino_evaluacion=datetime.date.today(),
                )

                porcentaje_total_cumplimiento = 0
                total_items = 0
                items_cumplidos = 0
                items_no_cumplidos = 0
                items_no_aplicaron = 0

                for item_evaluacion in protocolo_seleccionado.protocolo.itemsevaluacion_set.all():
                    cumplimiento = request.POST.get(f'aplica_{item_evaluacion.id_item}')
                    porcentaje_str = request.POST.get(f'porcentaje_{item_evaluacion.id_item}')

                    if cumplimiento == 'N/A':
                        items_no_aplicaron += 1
                    else:
                        total_items += 1

                        if cumplimiento == 'Si':
                            items_cumplidos += 1
                            if porcentaje_str:
                                porcentaje_cumplimiento = float(porcentaje_str)
                                porcentaje_total_cumplimiento += porcentaje_cumplimiento
                        elif cumplimiento == 'No':
                            items_no_cumplidos += 1
                            if porcentaje_str:
                                porcentaje_cumplimiento = float(porcentaje_str)
                                porcentaje_total_cumplimiento += porcentaje_cumplimiento

                cantidad_items_no_aplican = items_no_aplicaron

                if total_items - cantidad_items_no_aplican > 0:
                    porcentaje_promedio_cumplimiento = porcentaje_total_cumplimiento / (
                                total_items - cantidad_items_no_aplican)
                else:
                    porcentaje_promedio_cumplimiento = None

                if porcentaje_promedio_cumplimiento is not None:
                    porcentaje_promedio_cumplimiento = round(porcentaje_promedio_cumplimiento, 2)

                resultados_evaluacion = ResultadosEvaluacion.objects.create(
                    id_evaluacion=evaluacion,
                    porcentaje_cumplimiento=porcentaje_promedio_cumplimiento,
                    items_cumplidos=items_cumplidos,
                    items_no_cumplidos=items_no_cumplidos,
                    items_no_aplicaron=items_no_aplicaron,
                    # Agrega otros campos según tus necesidades
                )

                evaluacion.porcentaje_cumplimiento = porcentaje_promedio_cumplimiento
                evaluacion.save()

                # Almacena el protocolo seleccionado en la sesión con la clave única
                request.session[f'protocolo_nombre_{evaluacion.id_evaluacion}'] = protocolo_seleccionado.protocolo.nombre

                protocolo_seleccionado.estado = "completado"
                protocolo_seleccionado.save()

                return redirect('protocolos_seleccionados')

        else:
            items_evaluacion = protocolo_seleccionado.protocolo.itemsevaluacion_set.all()

            oportunidades_mejora_query = Oportunidadmejora.objects.filter(
                id_item__in=items_evaluacion
            )

            return render(request, 'autoevaluacion.html', {
                'protocolo_seleccionado': protocolo_seleccionado,
                'items_evaluacion': items_evaluacion,
                'oportunidades_mejora': oportunidades_mejora_query,
                'protocolo_nombre': protocolo_seleccionado.protocolo.nombre,
            })

    except Protocolosseleccionados.DoesNotExist:
        return HttpResponse('El protocolo seleccionado no existe', status=404)


@login_required
def profile(request):
    if request.user.is_authenticated:
        # Verifica si el usuario es una empresa
        if request.user.is_company:
            # Carga los resultados de la evaluación
            resultados = ResultadosEvaluacion.objects.filter(id_evaluacion__id_empresa=request.user.empresa)

            # Crea una lista de nombres de protocolos utilizando una comprensión de lista
            protocolo_nombres = [request.session.get(f'protocolo_nombre_{resultado.id_evaluacion.id_evaluacion}') for
                                 resultado in resultados]

            # Renderiza la plantilla y pasa los resultados y el nombre del protocolo al contexto
            return render(request, 'profile.html', {'resultados': resultados, 'protocolo_nombres': protocolo_nombres})
        else:
            # Si el usuario no es una empresa, puede ver su perfil sin resultados
            return render(request, 'profile.html', {'resultados': None})
    else:
        # Maneja el caso si el usuario no está autenticado
        # Puedes redirigirlo o mostrar un mensaje de error
        return HttpResponse('Debes iniciar sesión para ver esta página', status=401)


def guardar_respuestas(request):
    if request.method == 'POST':
        # Procesa y guarda las respuestas en la base de datos
        # ...
        return HttpResponse('Respuestas guardadas exitosamente')


def crear_plan_accion(request, item_id):
    item = get_object_or_404(ItemsEvaluacion, pk=item_id)

    # Recuperar protocolo_seleccionado de la sesión
    protocolo_seleccionado = request.session.get('protocolo_seleccionado')

    if request.method == 'POST':
        form = OportunidadmejoraForm(request.POST)
        if form.is_valid():
            plan_accion = form.save(commit=False)
            plan_accion.id_item = item
            plan_accion.save()

            # Redirigir de regreso a la página de autoevaluación con el protocolo seleccionado
            return redirect('autoevaluacion', protocolo_id=protocolo_seleccionado.id)

    else:
        form = OportunidadmejoraForm()

    return render(request, 'crear_plan_de_accion.html', {'form': form, 'item': item})


def obtener_plan_de_accion(request, oportunidad_id):
    oportunidad = get_object_or_404(Oportunidadmejora, pk=oportunidad_id)
    data = {
        'actividad': oportunidad.actividad,
        'porcentaje_avance': oportunidad.porcentaje_avance,
        'responsable': oportunidad.responsable,
        'fecha_inicio': oportunidad.fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_termino': oportunidad.fecha_termino.strftime('%Y-%m-%d'),
    }
    return JsonResponse(data)


def guardar_plan_de_accion(request):
    if request.method == 'POST':
        # Procesa y guarda el plan de acción en la base de datos
        # ...
        return JsonResponse({'message': 'Plan de acción guardado exitosamente'})