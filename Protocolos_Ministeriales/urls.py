from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.home, name='home'),
    path('signin/', accounts_views.signin, name='signin'),
    path('signout/', accounts_views.signout, name='signout'),
    path('signup/', accounts_views.signup, name='signup'),
    path('llenar_datos_empresa/', core_views.llenar_datos_empresa, name='llenar_datos_empresa'),
    path('autoevaluacion/<int:protocolo_id>/', core_views.autoevaluacion, name='autoevaluacion'),
    path('seleccionar_protocolo/', core_views.seleccionar_protocolo, name='seleccionar_protocolo'),
    path('protocolos_seleccionados/', core_views.protocolos_seleccionados, name='protocolos_seleccionados'),
    path('eliminar_protocolo/<int:pk>/', core_views.eliminar_protocolo, name='eliminar_protocolo'),
    path('profile/', core_views.profile, name='profile'),
    path('guardar_plan_de_accion/<int:id_item>/', core_views.guardar_plan_de_accion, name='guardar_plan_de_accion'),
    path('obtener_plan_de_accion/<int:id_item>/', core_views.obtener_plan_de_accion, name='obtener_plan_de_accion'),
    path('obtener_detalle_plan_de_accion/<int:plan_id>/', core_views.obtener_detalle_plan_de_accion,
         name='obtener_detalle_plan_de_accion'),
    path('actualizar_plan_de_accion/<int:plan_id>/', core_views.actualizar_plan_de_accion,
         name='actualizar_plan_de_accion'),
    path('eliminar_plan_de_accion/<int:plan_id>/', core_views.eliminar_plan_de_accion, name='eliminar_plan_de_accion'),
]
