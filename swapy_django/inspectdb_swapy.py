# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Administrador(models.Model):
    pkfk_id_doc = models.OneToOneField('Persona', models.DO_NOTHING, db_column='pkfk_id_doc', primary_key=True)  # The composite primary key (pkfk_id_doc, id_admin) found, that is not supported. The first column is selected.
    id_admin = models.ForeignKey('Persona', models.DO_NOTHING, db_column='id_admin', to_field='documento', related_name='administrador_id_admin_set')
    correo = models.CharField(max_length=30)
    contrasena = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'administrador'
        unique_together = (('pkfk_id_doc', 'id_admin'),)


class Categorias(models.Model):
    id_categoria = models.IntegerField(primary_key=True)
    n_categoria = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'categorias'


class Chats(models.Model):
    id_chat = models.IntegerField(primary_key=True)
    fk_id_doc = models.IntegerField()
    fk_id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='fk_id_usuario')
    estado_chat = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chats'


class Conversaciones(models.Model):
    id_conversacion = models.AutoField(primary_key=True)
    id_producto = models.IntegerField()
    id_iniciador = models.IntegerField()
    id_destinatario = models.IntegerField()
    ultimo_mensaje = models.CharField(max_length=255, blank=True, null=True)
    actualizado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'conversaciones'
        unique_together = (('id_producto', 'id_iniciador', 'id_destinatario'),)


class Denuncias(models.Model):
    id_denuncia = models.AutoField(primary_key=True)
    correo_denunciante = models.CharField(max_length=255)
    correo_denunciado = models.CharField(max_length=255)
    motivo = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'denuncias'


class Empleado(models.Model):
    pkfk_id_doc = models.OneToOneField('Persona', models.DO_NOTHING, db_column='pkfk_id_doc', primary_key=True)  # The composite primary key (pkfk_id_doc, id_empleado) found, that is not supported. The first column is selected.
    id_empleado = models.ForeignKey('Persona', models.DO_NOTHING, db_column='id_empleado', to_field='documento', related_name='empleado_id_empleado_set')
    correo = models.CharField(max_length=30)
    contrasena = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'empleado'
        unique_together = (('pkfk_id_doc', 'id_empleado'),)


class EmpleadoPerfil(models.Model):
    fk_id_empleado = models.BigIntegerField(primary_key=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    ciudad = models.CharField(max_length=60, blank=True, null=True)
    medio_transporte = models.CharField(max_length=40, blank=True, null=True)
    cuenta_pago = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleado_perfil'


class Entrega(models.Model):
    id_entrega = models.AutoField(primary_key=True)
    fk_id_intercambio = models.ForeignKey('Intercambio', models.DO_NOTHING, db_column='fk_id_intercambio')
    fk_id_empleado = models.BigIntegerField(blank=True, null=True)
    solicitante = models.CharField(max_length=100, blank=True, null=True)
    direccion_recogida = models.CharField(max_length=255)
    direccion_entrega = models.CharField(max_length=255)
    hora_limite = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=9)
    confirmacion_origen = models.IntegerField()
    confirmacion_destino = models.IntegerField()
    intentos_fallidos = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'entrega'


class Faqs(models.Model):
    id_faq = models.AutoField(primary_key=True)
    pregunta = models.TextField()
    respuesta = models.TextField()
    categoria = models.CharField(max_length=100)
    orden = models.IntegerField(blank=True, null=True)
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faqs'


class Imagenes(models.Model):
    id_img = models.IntegerField(primary_key=True)
    img_producto = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imagenes'


class Impulsar(models.Model):
    cod_impulso = models.IntegerField(primary_key=True)
    pago = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'impulsar'


class Intercambio(models.Model):
    id_intercambio = models.IntegerField(primary_key=True)
    fk_id_chat = models.ForeignKey(Chats, models.DO_NOTHING, db_column='fk_id_chat')
    n_producto_publicado = models.CharField(max_length=35, blank=True, null=True)
    n_producto_ofertado = models.CharField(max_length=35, blank=True, null=True)
    fecha_cierre = models.DateField(blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20)
    fk_id_empleado = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'intercambio'


class Intercambios(models.Model):
    id_intercambio = models.AutoField(primary_key=True)
    id_producto = models.IntegerField()
    id_solicitante = models.IntegerField()
    id_propietario = models.IntegerField()
    confirmado_solicitante = models.IntegerField()
    confirmado_propietario = models.IntegerField()
    direccion_recogida = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    descripcion_lugar = models.TextField()
    descripcion_producto = models.TextField()
    estado = models.CharField(max_length=30)
    fk_id_empleado = models.BigIntegerField(blank=True, null=True)
    estado_entrega = models.CharField(max_length=9, blank=True, null=True)
    hora_limite = models.TimeField(blank=True, null=True)
    confirmacion_origen = models.IntegerField()
    confirmacion_destino = models.IntegerField()
    intentos_fallidos = models.IntegerField()
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    creado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'intercambios'


class Mensajes(models.Model):
    id_mensaje = models.IntegerField(primary_key=True)
    fk_id_doc = models.IntegerField()
    fk_id_usuario = models.IntegerField()
    fk_id_chat = models.ForeignKey(Chats, models.DO_NOTHING, db_column='fk_id_chat')
    contenido_mensaje = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora_envio = models.DateTimeField(blank=True, null=True)
    estado_mensaje = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mensajes'


class MensajesChat(models.Model):
    id_mensaje_chat = models.AutoField(primary_key=True)
    id_conversacion = models.ForeignKey(Conversaciones, models.DO_NOTHING, db_column='id_conversacion')
    id_usuario = models.IntegerField()
    tipo = models.CharField(max_length=20)
    contenido = models.TextField()
    creado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'mensajes_chat'


class Persona(models.Model):
    fkpk_id_doc = models.OneToOneField('TDoc', models.DO_NOTHING, db_column='fkpk_id_doc', primary_key=True)  # The composite primary key (fkpk_id_doc, documento) found, that is not supported. The first column is selected.
    documento = models.BigIntegerField()
    primer_nombre = models.CharField(max_length=15)
    segundo_nombre = models.CharField(max_length=15, blank=True, null=True)
    primer_apellido = models.CharField(max_length=12)
    segundo_apellido = models.CharField(max_length=12, blank=True, null=True)
    fk_id_recuperar_cuenta = models.ForeignKey('RecuperarCuenta', models.DO_NOTHING, db_column='fk_id_recuperar_cuenta')

    class Meta:
        managed = False
        db_table = 'persona'
        unique_together = (('fkpk_id_doc', 'documento'),)


class ProblemasFrecuentes(models.Model):
    id_problema = models.IntegerField(primary_key=True)
    titulo_problema = models.CharField(max_length=45, blank=True, null=True)
    solucion = models.CharField(max_length=45, blank=True, null=True)
    fk_id_doc = models.ForeignKey(Administrador, models.DO_NOTHING, db_column='fk_id_doc')
    fk_id_admin = models.ForeignKey(Administrador, models.DO_NOTHING, db_column='fk_id_admin', to_field='id_admin', related_name='problemasfrecuentes_fk_id_admin_set')

    class Meta:
        managed = False
        db_table = 'problemas_frecuentes'


class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=50)
    valor_estimado = models.IntegerField(blank=True, null=True)
    desc_producto = models.TextField(blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    fk_id_categoria = models.ForeignKey(Categorias, models.DO_NOTHING, db_column='fk_id_categoria')
    fk_cod_impulso = models.ForeignKey(Impulsar, models.DO_NOTHING, db_column='fk_cod_impulso', blank=True, null=True)
    fk_id_doc = models.IntegerField()
    fk_id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='fk_id_usuario')
    estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'productos'


class ProductosHasImagenes(models.Model):
    pkfk_id_producto = models.OneToOneField(Productos, models.DO_NOTHING, db_column='pkfk_id_producto', primary_key=True)  # The composite primary key (pkfk_id_producto, pkfk_id_img) found, that is not supported. The first column is selected.
    pkfk_id_img = models.ForeignKey(Imagenes, models.DO_NOTHING, db_column='pkfk_id_img')

    class Meta:
        managed = False
        db_table = 'productos_has_imagenes'
        unique_together = (('pkfk_id_producto', 'pkfk_id_img'),)


class Publicaciones(models.Model):
    usuario_id = models.PositiveIntegerField()
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    valor_minimo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    descripcion_deseado = models.TextField(blank=True, null=True)
    categoria_deseada = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publicaciones'


class RecuperarCuenta(models.Model):
    id_recuperar_cuenta = models.IntegerField(primary_key=True)
    codigo_verif = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recuperar_cuenta'


class ReportePerfil(models.Model):
    id_reporte = models.IntegerField(primary_key=True)
    motivo = models.CharField(max_length=45, blank=True, null=True)
    fk_id_doc = models.ForeignKey(Administrador, models.DO_NOTHING, db_column='fk_id_doc')
    fk_id_admin = models.ForeignKey(Administrador, models.DO_NOTHING, db_column='fk_id_admin', to_field='id_admin', related_name='reporteperfil_fk_id_admin_set')

    class Meta:
        managed = False
        db_table = 'reporte_perfil'


class TDoc(models.Model):
    id_doc = models.IntegerField(primary_key=True)
    tipo_doc = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 't_doc'


class Usuario(models.Model):
    pkfk_id_doc = models.ForeignKey(TDoc, models.DO_NOTHING, db_column='pkfk_id_doc')
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=50)
    numero_documento = models.CharField(max_length=30, blank=True, null=True)
    contrasena = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    codigo_verificacion = models.CharField(max_length=10, blank=True, null=True)
    otp_expira = models.DateTimeField(blank=True, null=True)
    verificado = models.CharField(max_length=5, blank=True, null=True)
    premium = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=60, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=255, blank=True, null=True)
    categorias = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'


class UsuarioDenuncias(models.Model):
    id_denuncia = models.AutoField(primary_key=True)
    id_usuario_denunciante = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario_denunciante')
    id_usuario_denunciado = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario_denunciado', related_name='usuariodenuncias_id_usuario_denunciado_set', blank=True, null=True)
    tipo_denuncia = models.CharField(max_length=100, db_collation='utf8mb4_unicode_ci')
    descripcion = models.TextField(db_collation='utf8mb4_unicode_ci')
    respuesta = models.TextField(db_collation='utf8mb4_unicode_ci', blank=True, null=True)
    estado = models.CharField(max_length=11, db_collation='utf8mb4_unicode_ci', blank=True, null=True)
    fecha_creacion = models.DateTimeField()
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_denuncias'


class UsuarioPreguntas(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    pregunta = models.TextField(db_collation='utf8mb4_unicode_ci')
    respuesta = models.TextField(db_collation='utf8mb4_unicode_ci', blank=True, null=True)
    estado = models.CharField(max_length=10, db_collation='utf8mb4_unicode_ci', blank=True, null=True)
    fecha_creacion = models.DateTimeField()
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_preguntas'


class UsuarioPremium(models.Model):
    id_premium = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(Usuario, models.DO_NOTHING, db_column='id_usuario')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    plan = models.CharField(max_length=50, db_collation='utf8mb4_unicode_ci', blank=True, null=True)
    estado = models.CharField(max_length=9, db_collation='utf8mb4_unicode_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_premium'
