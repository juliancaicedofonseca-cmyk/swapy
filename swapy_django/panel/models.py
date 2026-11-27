
from django.db import models


# ==========================================
# TIPOS DE DOCUMENTO
# ==========================================

class TDoc(models.Model):
    id_doc = models.IntegerField(primary_key=True)
    tipo_doc = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 't_doc'

    def __str__(self):
        return self.tipo_doc


# ==========================================
# USUARIOS REGISTRADOS EN SWAPY
# ==========================================

class Usuario(models.Model):
    pkfk_id_doc = models.ForeignKey(
        TDoc,
        models.DO_NOTHING,
        db_column='pkfk_id_doc'
    )
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
    premium = models.BooleanField(blank=True, null=True)
    nombre = models.CharField(max_length=60, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=255, blank=True, null=True)
    categorias = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'

    def __str__(self):
        return self.correo


# ==========================================
# CLIENTES PREMIUM
# ==========================================

class UsuarioPremium(models.Model):
    id_premium = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario'
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    plan = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_premium'


# ==========================================
# DENUNCIAS DE USUARIOS
# ==========================================

class UsuarioDenuncias(models.Model):
    id_denuncia = models.AutoField(primary_key=True)
    id_usuario_denunciante = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario_denunciante'
    )
    id_usuario_denunciado = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario_denunciado',
        related_name='denuncias_recibidas',
        blank=True,
        null=True
    )
    tipo_denuncia = models.CharField(
        max_length=100,
        db_collation='utf8mb4_unicode_ci'
    )
    descripcion = models.TextField(db_collation='utf8mb4_unicode_ci')
    respuesta = models.TextField(
        db_collation='utf8mb4_unicode_ci',
        blank=True,
        null=True
    )
    estado = models.CharField(
        max_length=11,
        db_collation='utf8mb4_unicode_ci',
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField()
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_denuncias'


# ==========================================
# PREGUNTAS ENVIADAS POR LOS USUARIOS
# ==========================================

class UsuarioPreguntas(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario'
    )
    pregunta = models.TextField(db_collation='utf8mb4_unicode_ci')
    respuesta = models.TextField(
        db_collation='utf8mb4_unicode_ci',
        blank=True,
        null=True
    )
    estado = models.CharField(
        max_length=10,
        db_collation='utf8mb4_unicode_ci',
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField()
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_preguntas'


# ==========================================
# PREGUNTAS FRECUENTES
# ==========================================

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


# ==========================================
# DENUNCIAS GENERALES
# ==========================================

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
        
        # ==========================================
# RECUPERACIÓN DE CUENTAS
# ==========================================
class RecuperarCuenta(models.Model):
    id_recuperar_cuenta = models.IntegerField(primary_key=True)
    codigo_verif = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recuperar_cuenta'

    def __str__(self):
        return str(self.id_recuperar_cuenta)
