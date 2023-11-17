from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Avg, Sum, Count
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import Empresas, Protocolosseleccionados, TitulosRequisitos
from .models import Protocolos, ItemsEvaluacion, ResultadosEvaluacion, Evaluaciones, Oportunidadmejora
from .forms import OportunidadmejoraForm, EmpresaForm
from django.http import JsonResponse
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import json
from django.core import serializers
from decimal import Decimal

User = get_user_model()


@login_required
def llenar_datos_empresa(request):
    # Verifica si el usuario tiene el rol de empresa contratista
    if request.user.rol == 'empresa_contratista':
        # Verifica si ya se han llenado los datos de la empresa
        if request.user.empresa:
            return HttpResponse('Los datos de la empresa ya han sido llenados.', status=400)

        if request.method == 'POST':
            # Procesa el formulario cuando se envía
            form = EmpresaForm(request.POST)
            if form.is_valid():
                # Guarda los datos de la empresa en la base de datos
                empresa_data = form.cleaned_data
                empresa_data['id_empresa'] = request.user.id
                empresa = Empresas.objects.create(**empresa_data)

                # Asocia la empresa con el usuario
                request.user.empresa = empresa
                request.user.is_company = True
                request.user.save()

                return redirect('profile')  # Redirige a la vista del perfil después de llenar los datos
        else:
            # Muestra el formulario para llenar los datos de la empresa
            form = EmpresaForm()

        return render(request, 'llenar_datos_empresa.html', {'empresa_form': form})  # Ajuste aquí

    # Si el usuario no es una empresa contratista, puedes manejarlo de acuerdo a tus requerimientos
    else:
        return HttpResponse('Acceso no autorizado', status=403)


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

        # Obtener todas las evaluaciones relacionadas con el protocolo seleccionado
        evaluaciones = Evaluaciones.objects.filter(id_protocolo=protocolo_seleccionado.protocolo)

        # Eliminar los resultados de evaluación relacionados con las evaluaciones
        ResultadosEvaluacion.objects.filter(id_evaluacion__in=evaluaciones).delete()

        # Luego, eliminar el protocolo seleccionado
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

                with transaction.atomic():
                    for item_evaluacion in ItemsEvaluacion.objects.filter(id_protocolo=protocolo_seleccionado.protocolo.id_protocolo):
                        # Obtener las fechas específicas para cada item_evaluacion
                        fecha_inicio_item = request.POST.get(f'fecha_inicio_{item_evaluacion.id_item}')
                        fecha_termino_item = request.POST.get(f'fecha_termino_{item_evaluacion.id_item}')

                        # Verificar si hay información de fechas antes de crear una evaluación
                        if fecha_inicio_item and fecha_termino_item:
                            # Crear una nueva evaluación
                            evaluacion = Evaluaciones.objects.create(
                                id_empresa=empresa,
                                id_protocolo=protocolo_seleccionado.protocolo,
                                id_item_evaluacion=item_evaluacion,
                                fecha_inicio_evaluacion=fecha_inicio_item,
                                fecha_termino_evaluacion=fecha_termino_item,
                            )

                porcentaje_total_cumplimiento = 0
                total_items = 0
                items_cumplidos = 0
                items_no_cumplidos = 0
                items_no_aplicaron = 0

                for item_evaluacion in ItemsEvaluacion.objects.filter(id_protocolo
                                                                      =protocolo_seleccionado.protocolo.id_protocolo):
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
                    porcentaje_promedio_cumplimiento = (
                            porcentaje_total_cumplimiento / (total_items - cantidad_items_no_aplican))
                else:
                    porcentaje_promedio_cumplimiento = None

                if porcentaje_promedio_cumplimiento is not None:
                    porcentaje_promedio_cumplimiento = round(porcentaje_promedio_cumplimiento, 2)

                # Actualizamos el estado del protocolo seleccionado
                protocolo_seleccionado.estado = "completado" if items_cumplidos > 0 else "pendiente"
                protocolo_seleccionado.save()

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

                # Redirige a la lista de protocolos seleccionados
                return redirect('protocolos_seleccionados')

        else:
            items_evaluacion = ItemsEvaluacion.objects.filter(id_protocolo=protocolo_seleccionado.protocolo.id_protocolo)
            oportunidades_mejora = Oportunidadmejora.objects.filter(id_item__in=items_evaluacion)
            oportunidadmejora_form = OportunidadmejoraForm()

            return render(request, 'autoevaluacion.html', {
                'protocolo_seleccionado': protocolo_seleccionado,
                'items_evaluacion': items_evaluacion,
                'oportunidades_mejora': oportunidades_mejora,
                'protocolo_nombre': protocolo_seleccionado.protocolo.nombre,
                'form': oportunidadmejora_form,
            })

    except Protocolosseleccionados.DoesNotExist:
        return HttpResponse('El protocolo seleccionado no existe', status=404)


@login_required
def profile(request):
    if request.user.is_authenticated:
        # Verifica si el usuario tiene el rol de empresa contratista
        if request.user.rol == 'empresa_contratista':
            if request.method == 'POST':
                # Verifica si ya se han llenado los datos de la empresa
                if not request.user.empresa:
                    # Si no se han llenado los datos, redirige al usuario al formulario
                    return redirect('llenar_datos_empresa')

                # Procesa cualquier acción POST adicional (como la eliminación de un protocolo)
                # y redirige nuevamente a la vista profile
                return redirect('profile')

            # Carga los resultados de la evaluación para la empresa actual
            resultados = ResultadosEvaluacion.objects.filter(id_evaluacion__id_empresa=request.user.id)

            # Crea una lista de nombres de protocolos utilizando una comprensión de lista
            protocolo_nombres = [request.session.get(f'protocolo_nombre_{resultado.id_evaluacion.id_evaluacion}')
                                 for resultado in resultados]

            # Renderiza la plantilla y pasa los resultados y el nombre del protocolo al contexto
            return render(request, 'profile.html', {'resultados': resultados, 'protocolo_nombres': protocolo_nombres})

        # Verifica si el usuario tiene el rol de mandatario
        elif request.user.rol == 'mandatario':
            # Redirige a la vista del mandatario
            return redirect('vista_mandatario')  # Ajusta el nombre de la vista según sea necesario

        # Si el usuario no es una empresa contratista ni un mandatario, puedes manejarlo de acuerdo a tus requerimientos
        else:
            return HttpResponse('Acceso no autorizado', status=403)
    else:
        # Maneja el caso si el usuario no está autenticado
        # Puedes redirigirlo o mostrar un mensaje de error
        return HttpResponse('Debes iniciar sesión para ver esta página', status=401)


def guardar_respuestas(request):
    if request.method == 'POST':
        # Procesa y guarda las respuestas en la base de datos
        # ...
        return HttpResponse('Respuestas guardadas exitosamente')


def guardar_plan_de_accion(request, id_item):
    if request.method == 'POST':
        oportunidadmejora_form = OportunidadmejoraForm(request.POST)
        if oportunidadmejora_form.is_valid():
            oportunidadmejora = oportunidadmejora_form.save(commit=False)
            oportunidadmejora.id_item = get_object_or_404(ItemsEvaluacion, pk=id_item)

            porcentaje = oportunidadmejora.porcentajeavance
            if porcentaje is not None and not 1 <= porcentaje <= 100:
                response_data = {
                    'success': False,
                    'message': 'Porcentaje de avance debe estar entre 1 y 100.',
                }
            else:
                oportunidadmejora.save()
                response_data = {
                    'success': True,
                    'message': 'Los datos se han guardado exitosamente.',
                }
        else:
            response_data = {
                'success': False,
                'errors': oportunidadmejora_form.errors,
            }

        return JsonResponse(response_data)


def obtener_plan_de_accion(request, id_item):
    if request.method == 'GET':
        planes_de_accion = Oportunidadmejora.objects.filter(id_item=id_item)
        data = [{
            'id_oportunidad': plan.id_oportunidad,
            'actividad': plan.actividad,
            'porcentajeavance': plan.porcentajeavance,
            'responsable': plan.responsable,
            'fechainicio': plan.fechainicio,
            'fechatermino': plan.fechatermino,
        } for plan in planes_de_accion]

        return JsonResponse(data, safe=False)


def obtener_detalle_plan_de_accion(request, plan_id):
    if request.method == 'GET':
        plan = get_object_or_404(Oportunidadmejora, id_oportunidad=plan_id)
        data = {
            'id_oportunidad': plan.id_oportunidad,
            'actividad': plan.actividad,
            'porcentajeavance': plan.porcentajeavance,
            'responsable': plan.responsable,
            'fechainicio': plan.fechainicio,
            'fechatermino': plan.fechatermino,
        }
        return JsonResponse(data)


@require_http_methods(["PUT"])
def actualizar_plan_de_accion(request, plan_id):
    try:
        plan_existente = get_object_or_404(Oportunidadmejora, id_oportunidad=plan_id)

        # Leer los datos del cuerpo de la solicitud como JSON
        data = json.loads(request.body.decode('utf-8'))

        plan_existente.actividad = data.get('actividad')
        plan_existente.porcentajeavance = data.get('porcentajeavance')
        plan_existente.responsable = data.get('responsable')
        plan_existente.fechainicio = data.get('fechainicio')
        plan_existente.fechatermino = data.get('fechatermino')

        plan_existente.save()

        return JsonResponse({'message': 'Plan actualizado correctamente'})
    except Exception as e:
        return JsonResponse({'message': f'Error al actualizar el plan: {str(e)}'}, status=500)


@require_http_methods(["DELETE"])
def eliminar_plan_de_accion(request, plan_id):
    try:
        plan = get_object_or_404(Oportunidadmejora, id_oportunidad=plan_id)
        plan.delete()
        return JsonResponse({'message': 'Plan eliminado correctamente'})
    except Exception as e:
        return JsonResponse({'message': f'Error al eliminar el plan: {str(e)}'}, status=500)


def vista_mandatario(request):
    if request.user.is_authenticated:
        # Verifica si el usuario tiene el rol de mandatario
        if request.user.rol == 'mandatario':
            # Obtén los resultados de evaluación de todas las empresas contratistas
            resultados_empresas = ResultadosEvaluacion.objects.all()

            # Renderiza la plantilla y pasa los resultados de evaluación al contexto
            return render(request, 'gantts.html', {'resultados_empresas': resultados_empresas})

        # Si el usuario no es un mandatario, puedes manejarlo de acuerdo a tus requerimientos
        else:
            return HttpResponse('Acceso no autorizado', status=403)
    else:
        # Maneja el caso si el usuario no está autenticado
        # Puedes redirigirlo o mostrar un mensaje de error
        return HttpResponse('Debes iniciar sesión para ver esta página', status=401)