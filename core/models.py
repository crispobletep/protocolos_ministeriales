from django.db import models


class Empresas(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    nombre_experto_prevencion_riesgos = models.CharField(max_length=255, blank=True, null=True)
    nro_trabajadores_empresa = models.IntegerField(blank=True, null=True)
    numero_de_contrato = models.CharField(db_column='Numero_de_Contrato', max_length=255, blank=True, null=True)  # Field name made lowercase.
    gerencia = models.CharField(db_column='Gerencia', max_length=255, blank=True, null=True)  # Field name made lowercase.
    superintendencia = models.CharField(db_column='Superintendencia', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nombre_admin_contrato_antucoya = models.CharField(db_column='Nombre_Admin_Contrato_Antucoya', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nombre_admin_contrato_empresa_contratista = models.CharField(db_column='Nombre_Admin_Contrato_Empresa_Contratista', max_length=255, blank=True, null=True)  # Field name made lowercase.
    correo_admin_ec = models.CharField(db_column='Correo_Admin_EC', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'empresas'


class Protocolos(models.Model):
    id_protocolo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=125)
    estado = models.CharField(max_length=25, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'protocolos'


class ItemsEvaluacion(models.Model):
    id_item = models.AutoField(primary_key=True)
    id_protocolo = models.IntegerField(blank=True, null=True)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    item = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    item_a_evaluar = models.TextField(blank=True, null=True)
    marco_legal = models.TextField(blank=True, null=True)
    evidencia = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'items_evaluacion'


class Evaluaciones(models.Model):
    id_evaluacion = models.AutoField(primary_key=True)
    id_item_evaluacion = models.ForeignKey('ItemsEvaluacion', models.DO_NOTHING, db_column='id_item', blank=True, null=True)
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa', blank=True, null=True)
    id_protocolo = models.ForeignKey('Protocolos', models.DO_NOTHING, db_column='id_protocolo', blank=True, null=True)
    fecha_inicio_evaluacion = models.DateField(blank=True, null=True)
    fecha_termino_evaluacion = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'evaluaciones'


class Oportunidadmejora(models.Model):
    id_oportunidad = models.AutoField(primary_key=True)
    id_item = models.ForeignKey(ItemsEvaluacion, models.DO_NOTHING, db_column='id_item', blank=True, null=True)
    actividad = models.CharField(max_length=255, blank=True, null=True)
    porcentajeavance = models.IntegerField(blank=True, null=True)
    responsable = models.CharField(max_length=255, blank=True, null=True)
    fechainicio = models.DateField(blank=True, null=True)
    fechatermino = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'oportunidadmejora'


class Protocolosseleccionados(models.Model):
    id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    protocolo = models.ForeignKey(Protocolos, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'protocolosseleccionados'


class ResultadosEvaluacion(models.Model):
    id_resultado = models.AutoField(primary_key=True)
    porcentaje_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    items_cumplidos = models.IntegerField(blank=True, null=True)
    items_no_cumplidos = models.IntegerField(blank=True, null=True)
    items_no_aplicaron = models.IntegerField(blank=True, null=True)
    id_evaluacion = models.ForeignKey(Evaluaciones, models.DO_NOTHING, db_column='id_evaluacion')

    class Meta:
        managed = True
        db_table = 'resultados_evaluacion'


class TitulosRequisitos(models.Model):
    id_titulo = models.AutoField(primary_key=True)
    numero_item = models.CharField(max_length=255, blank=True, null=True)
    nombre_grupo = models.CharField(max_length=255, blank=True, null=True)
    id_protocolo = models.ForeignKey(Protocolos, models.DO_NOTHING, db_column='id_protocolo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'titulos_requisitos'


class UsuarioEmpresa(models.Model):
    id_relacion = models.AutoField(primary_key=True)
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_empresa'


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255)
    apellido_paterno_usuario = models.CharField(max_length=255)
    apellido_materno_usuario = models.CharField(max_length=255, blank=True, null=True)
    email_usuario = models.CharField(max_length=255)
    clave_usuario = models.CharField(max_length=255)
    rol = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = 'usuarios'
