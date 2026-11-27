import bcrypt
import secrets
import csv
import hashlib
import io
import unicodedata


from openpyxl import load_workbook
from functools import wraps
from django.utils import timezone
from datetime import date

from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db import connection, transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import (
    Usuario,
    TDoc,
    UsuarioDenuncias,
    UsuarioPreguntas,
)


# ==========================================
# GENERAR ID DE RECUPERACIÓN
# ==========================================

def generar_id_recuperacion(cursor):
    cursor.execute("""
        SELECT COALESCE(MAX(id_recuperar_cuenta), 0)
        FROM recuperar_cuenta
    """)

    ultimo_id = cursor.fetchone()[0]
    nuevo_id = ultimo_id + 1

    if nuevo_id > 2147483647:
        raise ValueError("Se alcanzó el límite de identificadores.")

    return nuevo_id


# ==========================================
# VERIFICAR CONTRASEÑAS PHP BCRYPT
# ==========================================

def verificar_contrasena(contrasena_ingresada, hash_guardado):
    try:
        hash_bytes = hash_guardado.encode("utf-8")

        if hash_bytes.startswith(b"$2y$"):
            hash_bytes = b"$2b$" + hash_bytes[4:]

        return bcrypt.checkpw(
            contrasena_ingresada.encode("utf-8"),
            hash_bytes
        )

    except (ValueError, TypeError, AttributeError):
        return False


# ==========================================
# PROTEGER LAS VISTAS ADMINISTRATIVAS
# ==========================================

def administrador_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.session.get("admin_autenticado"):
            return redirect("panel_login")

        if request.session.get("admin_rol", "").lower() != "administrador":
            request.session.flush()
            return redirect("panel_login")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================
# INICIO DE SESIÓN ADMINISTRATIVO
# ==========================================

def login_admin(request):

    error = None

    if request.method == "POST":

        correo = request.POST.get("correo", "").strip()
        contrasena = request.POST.get("contrasena", "")

        if not correo or not contrasena:
            error = "Completa todos los campos."

        else:
            usuario = Usuario.objects.filter(
                correo__iexact=correo
            ).first()

            if usuario is None:
                error = "Correo o contraseña incorrectos."

            elif not verificar_contrasena(
                contrasena,
                usuario.contrasena
            ):
                error = "Correo o contraseña incorrectos."

            elif (usuario.estado or "").lower() != "activo":
                error = "La cuenta no se encuentra activa."

            elif (usuario.rol or "").lower() != "administrador":
                error = "No tienes permisos para acceder al panel."

            else:
                request.session.flush()

                request.session["admin_autenticado"] = True
                request.session["admin_id"] = usuario.id_usuario
                request.session["admin_correo"] = usuario.correo
                request.session["admin_rol"] = usuario.rol

                return redirect("panel_dashboard")

    return render(
        request,
        "panel/login.html",
        {"error": error}
    )


# ==========================================
# ACCESO DIRECTO DESDE EL LOGIN PHP
# ==========================================

def sso_desde_php(request):
    import base64
    import hmac
    import time
    from django.conf import settings

    token = request.GET.get("token", "")
    payload, _, firma = token.partition(".")

    esperada = hmac.new(
        settings.SWAPY_SSO_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if not payload or not hmac.compare_digest(esperada, firma):
        return redirect("panel_login")

    try:
        datos = base64.urlsafe_b64decode(
            payload + "=" * (-len(payload) % 4)
        ).decode()
        id_usuario, expira, nonce = datos.split("|")
        expira = int(expira)
    except (ValueError, UnicodeDecodeError):
        return redirect("panel_login")

    if expira < time.time():
        return redirect("panel_login")

    # Un solo uso por sesión de navegador
    if request.session.get("sso_nonce") == nonce:
        return redirect("panel_dashboard")

    usuario = Usuario.objects.filter(id_usuario=id_usuario).first()

    if (
        usuario is None
        or (usuario.estado or "").lower() != "activo"
        or (usuario.rol or "").lower() != "administrador"
    ):
        return redirect("panel_login")

    request.session.flush()
    request.session["admin_autenticado"] = True
    request.session["admin_id"] = usuario.id_usuario
    request.session["admin_correo"] = usuario.correo
    request.session["admin_rol"] = usuario.rol
    request.session["sso_nonce"] = nonce

    return redirect("panel_dashboard")


# ==========================================
# CERRAR SESIÓN
# ==========================================

@require_POST
def logout_admin(request):
    from django.conf import settings

    request.session.flush()
    # Cierra también la sesión PHP y vuelve a la página de inicio
    return redirect(settings.SWAPY_PHP_URL + "auth/logout")



# ==========================================
# PANEL PRINCIPAL - RESUMEN GENERAL
# ==========================================

@administrador_requerido
def dashboard(request):

    # ==========================================
    # PERSONAS REGISTRADAS
    # ==========================================

    total_usuarios = Usuario.objects.count()

    usuarios_activos = Usuario.objects.filter(
        estado__iexact="Activo"
    ).count()

    usuarios_inactivos = Usuario.objects.filter(
        estado__iexact="Inactivo"
    ).count()

    total_administradores = Usuario.objects.filter(
        rol__iexact="Administrador"
    ).count()

    total_empleados = Usuario.objects.filter(
        rol__iexact="Empleado"
    ).count()

    usuarios_verificados = Usuario.objects.filter(
        verificado__in=["SI", "1"]
    ).count()

    hoy = timezone.localdate()

    # ==========================================
    # PRODUCTOS, CATEGORÍAS Y SOLICITUDES
    # ==========================================

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT COUNT(*)
            FROM productos
        """)
        total_productos = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM categorias
        """)
        total_categorias = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COALESCE(SUM(valor_estimado), 0)
            FROM productos
            WHERE valor_estimado > 0
        """)
        valor_total_productos = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM intercambios
        """)
        total_solicitudes = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM intercambios
            WHERE DATE(creado_en) = %s
        """, [hoy])
        solicitudes_hoy = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM intercambios
            WHERE estado_entrega IN (
                'Pendiente',
                'Aceptada',
                'En_ruta'
            )
        """)
        solicitudes_pendientes = cursor.fetchone()[0] or 0

        # ==========================================
        # DENUNCIAS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_denuncias
            WHERE estado = 'pendiente'
        """)
        denuncias_pendientes = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_denuncias
            WHERE estado = 'en_revision'
        """)
        denuncias_en_revision = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_denuncias
        """)
        total_denuncias = cursor.fetchone()[0] or 0

        # ==========================================
        # PREGUNTAS DE USUARIOS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_preguntas
            WHERE estado = 'pendiente'
        """)
        preguntas_pendientes = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_preguntas
        """)
        total_preguntas = cursor.fetchone()[0] or 0

        # ==========================================
        # ÚLTIMAS SOLICITUDES
        # ==========================================

        cursor.execute("""
            SELECT
                i.id_intercambio,
                i.estado_entrega,
                i.creado_en,
                p.nombre_producto,
                COALESCE(
                    NULLIF(u.username, ''),
                    u.correo
                ) AS nombre_solicitante
            FROM intercambios i
            LEFT JOIN productos p
                ON p.id_producto = i.id_producto
            LEFT JOIN usuario u
                ON u.id_usuario = i.id_solicitante
            ORDER BY i.creado_en DESC
            LIMIT 5
        """)

        columnas = [
            columna[0]
            for columna in cursor.description
        ]

        ultimas_solicitudes = [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]

    # ==========================================
    # INFORMACIÓN PARA EL DASHBOARD
    # ==========================================

    contexto = {
        "correo": request.session.get("admin_correo"),

        # PERSONAS
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_inactivos,
        "total_administradores": total_administradores,
        "total_empleados": total_empleados,
        "usuarios_verificados": usuarios_verificados,

        # PRODUCTOS Y CATEGORÍAS
        "total_productos": total_productos,
        "total_categorias": total_categorias,
        "valor_total_productos": valor_total_productos,

        # SOLICITUDES
        "total_solicitudes": total_solicitudes,
        "solicitudes_hoy": solicitudes_hoy,
        "solicitudes_pendientes": solicitudes_pendientes,
        "ultimas_solicitudes": ultimas_solicitudes,

        # DENUNCIAS
        "total_denuncias": total_denuncias,
        "denuncias_pendientes": denuncias_pendientes,
        "denuncias_en_revision": denuncias_en_revision,

        # PREGUNTAS
        "total_preguntas": total_preguntas,
        "preguntas_pendientes": preguntas_pendientes,

        # FECHA
        "fecha_actual": hoy,
    }

    return render(
        request,
        "panel/dashboard.html",
        contexto
    )



# ==========================================
# PERSONAS REGISTRADAS
# ==========================================

@administrador_requerido
def personas(request):

    busqueda = request.GET.get("buscar", "").strip()

    usuarios = Usuario.objects.select_related(
        "pkfk_id_doc"
    ).all().order_by("-id_usuario")

    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(correo__icontains=busqueda) |
            Q(numero_documento__icontains=busqueda) |
            Q(rol__icontains=busqueda)
        )

    contexto = {
        "correo": request.session.get("admin_correo"),
        "usuarios": usuarios,
        "busqueda": busqueda,
    }

    return render(request, "panel/personas.html", contexto)


# ==========================================
# REGISTRAR PERSONAS
# ==========================================

@administrador_requerido
def crear_persona(request):

    error = None

    if request.method == "POST":

        tipo_documento = request.POST.get("tipo_documento", "").strip()
        numero_documento = request.POST.get("numero_documento", "").strip()

        primer_nombre = request.POST.get("primer_nombre", "").strip()
        segundo_nombre = request.POST.get("segundo_nombre", "").strip()
        primer_apellido = request.POST.get("primer_apellido", "").strip()
        segundo_apellido = request.POST.get("segundo_apellido", "").strip()

        username = request.POST.get("username", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        correo = request.POST.get("correo", "").strip()
        rol = request.POST.get("rol", "").strip()
        estado = request.POST.get("estado", "").strip()

        contrasena = request.POST.get("contrasena", "")
        confirmar = request.POST.get("confirmar_contrasena", "")

        if not all([
            tipo_documento,
            numero_documento,
            correo,
            rol,
            estado,
            contrasena,
            confirmar
        ]):
            error = "Completa todos los campos obligatorios."

        elif rol not in ["Administrador", "Empleado"]:
            error = "Solo se permiten Administrador y Empleado."

        elif estado not in ["Activo", "Inactivo"]:
            error = "El estado seleccionado no es válido."

        elif not TDoc.objects.filter(id_doc=tipo_documento).exists():
            error = "El tipo de documento seleccionado no es válido."

        elif not numero_documento.isdigit():
            error = "El documento debe contener solamente números."

        elif len(numero_documento) > 30:
            error = "El documento supera la longitud permitida."

        elif int(numero_documento) <= 0 or int(numero_documento) > 9223372036854775807:
            error = "El número de documento no es válido."

        if not error:
            try:
                validate_email(correo)
            except ValidationError:
                error = "Introduce un correo electrónico válido."

        if not error and len(correo) > 50:
            error = "El correo no puede superar los 50 caracteres."

        if not error and rol == "Empleado" and len(correo) > 30:
            error = "El correo de un empleado no puede superar los 30 caracteres."

        if not error and rol == "Empleado":

            if not primer_nombre or not primer_apellido:
                error = "El primer nombre y el primer apellido son obligatorios."

            elif len(primer_nombre) > 15 or len(segundo_nombre) > 15:
                error = "Los nombres no pueden superar los 15 caracteres."

            elif len(primer_apellido) > 12 or len(segundo_apellido) > 12:
                error = "Los apellidos no pueden superar los 12 caracteres."

        if not error and len(username) > 50:
            error = "El nombre de usuario no puede superar los 50 caracteres."

        if not error and len(telefono) > 20:
            error = "El teléfono no puede superar los 20 caracteres."

        if not error and len(contrasena) < 6:
            error = "La contraseña debe tener mínimo 6 caracteres."

        if not error and contrasena != confirmar:
            error = "Las contraseñas no coinciden."

        if not error and len(contrasena.encode("utf-8")) > 72:
            error = "La contraseña supera el límite permitido."

        if not error and Usuario.objects.filter(
            correo__iexact=correo
        ).exists():
            error = "Ya existe una persona registrada con ese correo."

        if not error and Usuario.objects.filter(
            numero_documento=numero_documento
        ).exists():
            error = "Ya existe una persona registrada con ese documento."

        if not error:
            try:
                with transaction.atomic():

                    tipo_doc = TDoc.objects.get(id_doc=tipo_documento)

                    hash_contrasena = bcrypt.hashpw(
                        contrasena.encode("utf-8"),
                        bcrypt.gensalt()
                    ).decode("utf-8")

                    Usuario.objects.create(
                        pkfk_id_doc=tipo_doc,
                        username=username or None,
                        telefono=telefono or None,
                        correo=correo,
                        numero_documento=numero_documento,
                        contrasena=hash_contrasena,
                        rol=rol,
                        estado=estado,
                        verificado="SI",
                        premium=False
                    )

                    if rol == "Empleado":
                        with connection.cursor() as cursor:

                            nuevo_id = generar_id_recuperacion(cursor)
                            codigo = secrets.randbelow(900000) + 100000

                            cursor.execute("""
                                INSERT INTO recuperar_cuenta (
                                    id_recuperar_cuenta,
                                    codigo_verif
                                )
                                VALUES (%s, %s)
                            """, [nuevo_id, codigo])

                            cursor.execute("""
                                INSERT INTO persona (
                                    fkpk_id_doc,
                                    documento,
                                    primer_nombre,
                                    segundo_nombre,
                                    primer_apellido,
                                    segundo_apellido,
                                    fk_id_recuperar_cuenta
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, [
                                tipo_doc.id_doc,
                                int(numero_documento),
                                primer_nombre,
                                segundo_nombre or None,
                                primer_apellido,
                                segundo_apellido or None,
                                nuevo_id
                            ])

                            cursor.execute("""
                                INSERT INTO empleado (
                                    pkfk_id_doc,
                                    id_empleado,
                                    correo,
                                    contrasena
                                )
                                VALUES (%s, %s, %s, %s)
                            """, [
                                tipo_doc.id_doc,
                                int(numero_documento),
                                correo,
                                hash_contrasena
                            ])

                return redirect("/panel/personas/?creado=1")

            except Exception as excepcion:
                print("ERROR AL REGISTRAR PERSONA:", excepcion)

                error = (
                    "No fue posible registrar la persona. "
                    "La operación fue cancelada. "
                    "Verifica los datos y las relaciones de la base de datos."
                )

    tipos_documento = TDoc.objects.all().order_by("id_doc")

    contexto = {
        "correo": request.session.get("admin_correo"),
        "tipos_documento": tipos_documento,
        "error": error,
    }

    return render(
        request,
        "panel/crear_persona.html",
        contexto
    )


# ==========================================
# EDITAR PERSONAS
# ==========================================

@administrador_requerido
def editar_persona(request, id_usuario):

    usuario = Usuario.objects.select_related(
        "pkfk_id_doc"
    ).filter(
        id_usuario=id_usuario
    ).first()

    if usuario is None:
        return redirect("/panel/personas/")

    error = None

    # El rol queda fijo después del registro.
    rol_original = (usuario.rol or "").strip()

    if rol_original not in ["Empleado", "Administrador"]:
        return redirect("/panel/personas/")

    datos_persona = {
        "primer_nombre": "",
        "segundo_nombre": "",
        "primer_apellido": "",
        "segundo_apellido": "",
    }

    # Consultar los datos personales del empleado.
    if rol_original == "Empleado":

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido
                FROM persona
                WHERE fkpk_id_doc = %s
                  AND documento = %s
            """, [
                usuario.pkfk_id_doc_id,
                usuario.numero_documento
            ])

            fila = cursor.fetchone()

            if fila:
                datos_persona = {
                    "primer_nombre": fila[0] or "",
                    "segundo_nombre": fila[1] or "",
                    "primer_apellido": fila[2] or "",
                    "segundo_apellido": fila[3] or "",
                }
            else:
                error = (
                    "No se encontraron los datos personales "
                    "relacionados con este empleado."
                )

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        correo = request.POST.get("correo", "").strip()
        estado = request.POST.get("estado", "").strip()
        contrasena = request.POST.get("contrasena", "")

        primer_nombre = request.POST.get(
            "primer_nombre", ""
        ).strip()

        segundo_nombre = request.POST.get(
            "segundo_nombre", ""
        ).strip()

        primer_apellido = request.POST.get(
            "primer_apellido", ""
        ).strip()

        segundo_apellido = request.POST.get(
            "segundo_apellido", ""
        ).strip()

        # VALIDACIONES GENERALES

        if not correo or not estado:
            error = "Completa los campos obligatorios."

        elif estado not in ["Activo", "Inactivo"]:
            error = "El estado seleccionado no es válido."

        if not error:
            try:
                validate_email(correo)
            except ValidationError:
                error = "Introduce un correo electrónico válido."

        if not error and len(correo) > 50:
            error = "El correo no puede superar los 50 caracteres."

        if not error and rol_original == "Empleado" and len(correo) > 30:
            error = "El correo de un empleado no puede superar los 30 caracteres."

        if not error and len(username) > 50:
            error = "El nombre de usuario no puede superar los 50 caracteres."

        if not error and len(telefono) > 20:
            error = "El teléfono no puede superar los 20 caracteres."

        # VALIDAR NOMBRES DEL EMPLEADO

        if not error and rol_original == "Empleado":

            if not primer_nombre or not primer_apellido:
                error = "El primer nombre y el primer apellido son obligatorios."

            elif len(primer_nombre) > 15 or len(segundo_nombre) > 15:
                error = "Los nombres no pueden superar los 15 caracteres."

            elif len(primer_apellido) > 12 or len(segundo_apellido) > 12:
                error = "Los apellidos no pueden superar los 12 caracteres."

        # VALIDAR CONTRASEÑA SI SE DESEA CAMBIAR

        if not error and contrasena:

            if len(contrasena) < 6:
                error = "La contraseña debe tener mínimo 6 caracteres."

            elif len(contrasena.encode("utf-8")) > 72:
                error = "La contraseña supera el límite permitido."

        # VALIDAR CORREO DUPLICADO

        if not error and Usuario.objects.filter(
            correo__iexact=correo
        ).exclude(
            id_usuario=usuario.id_usuario
        ).exists():
            error = "Ese correo ya está registrado por otra persona."

        if not error:

            try:
                with transaction.atomic():

                    # ACTUALIZAR TABLA USUARIO

                    usuario.username = username or None
                    usuario.telefono = telefono or None
                    usuario.correo = correo
                    usuario.estado = estado

                    campos_actualizados = [
                        "username",
                        "telefono",
                        "correo",
                        "estado",
                    ]

                    if contrasena:
                        usuario.contrasena = bcrypt.hashpw(
                            contrasena.encode("utf-8"),
                            bcrypt.gensalt()
                        ).decode("utf-8")

                        campos_actualizados.append("contrasena")

                    usuario.save(
                        update_fields=campos_actualizados
                    )

                    # ACTUALIZAR TABLAS RELACIONADAS DEL EMPLEADO

                    if rol_original == "Empleado":

                        with connection.cursor() as cursor:

                            # COMPROBAR QUE EXISTA EL REGISTRO EN PERSONA

                            cursor.execute("""
                                SELECT 1
                                FROM persona
                                WHERE fkpk_id_doc = %s
                                  AND documento = %s
                            """, [
                                usuario.pkfk_id_doc_id,
                                usuario.numero_documento
                            ])

                            if cursor.fetchone() is None:
                                raise ValueError(
                                    "No se encontró el registro personal del empleado."
                                )

                            # ACTUALIZAR NOMBRES Y APELLIDOS

                            cursor.execute("""
                                UPDATE persona
                                SET
                                    primer_nombre = %s,
                                    segundo_nombre = %s,
                                    primer_apellido = %s,
                                    segundo_apellido = %s
                                WHERE fkpk_id_doc = %s
                                  AND documento = %s
                            """, [
                                primer_nombre,
                                segundo_nombre or None,
                                primer_apellido,
                                segundo_apellido or None,
                                usuario.pkfk_id_doc_id,
                                usuario.numero_documento
                            ])

                            # COMPROBAR QUE EXISTA EL REGISTRO EN EMPLEADO

                            cursor.execute("""
                                SELECT 1
                                FROM empleado
                                WHERE pkfk_id_doc = %s
                                  AND id_empleado = %s
                            """, [
                                usuario.pkfk_id_doc_id,
                                usuario.numero_documento
                            ])

                            if cursor.fetchone() is None:
                                raise ValueError(
                                    "No se encontró el registro del empleado."
                                )

                            # ACTUALIZAR CORREO Y CONTRASEÑA

                            if contrasena:
                                cursor.execute("""
                                    UPDATE empleado
                                    SET correo = %s,
                                        contrasena = %s
                                    WHERE pkfk_id_doc = %s
                                      AND id_empleado = %s
                                """, [
                                    correo,
                                    usuario.contrasena,
                                    usuario.pkfk_id_doc_id,
                                    usuario.numero_documento
                                ])

                            else:
                                cursor.execute("""
                                    UPDATE empleado
                                    SET correo = %s
                                    WHERE pkfk_id_doc = %s
                                      AND id_empleado = %s
                                """, [
                                    correo,
                                    usuario.pkfk_id_doc_id,
                                    usuario.numero_documento
                                ])

                return redirect("/panel/personas/?editado=1")

            except Exception as excepcion:
                print("ERROR AL EDITAR PERSONA:", excepcion)

                error = (
                    "No fue posible actualizar la persona. "
                    "Los cambios fueron cancelados."
                )

    contexto = {
        "correo": request.session.get("admin_correo"),
        "usuario": usuario,
        "datos_persona": datos_persona,
        "error": error,
    }

    return render(
        request,
        "panel/editar_persona.html",
        contexto
    )


# ==========================================
# IMPORTACIÓN MASIVA: LECTURA DE ARCHIVOS
# ==========================================

CAMPOS_IMPORTACION = [
    "tipo_documento",
    "numero_documento",
    "primer_nombre",
    "segundo_nombre",
    "primer_apellido",
    "segundo_apellido",
    "username",
    "telefono",
    "correo",
    "rol",
    "estado",
    "contrasena",
]


def normalizar_encabezado(valor):
    valor = str(valor or "").strip().lower()
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(
        caracter for caracter in valor
        if not unicodedata.combining(caracter)
    )
    return valor.replace(" ", "_")


def leer_archivo_importacion(archivo):
    nombre = archivo.name.lower()
    contenido = archivo.read()

    if len(contenido) > 5 * 1024 * 1024:
        raise ValueError("El archivo no puede superar los 5 MB.")

    # LEER EXCEL
    if nombre.endswith(".xlsx"):
        libro = load_workbook(
            io.BytesIO(contenido),
            read_only=True,
            data_only=True
        )
        hoja = libro.active
        datos = list(hoja.iter_rows(values_only=True))
        libro.close()

    # LEER CSV Y TXT
    elif nombre.endswith((".csv", ".txt")):
        try:
            texto = contenido.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = contenido.decode("latin-1")

        muestra = texto[:4096]

        try:
            dialecto = csv.Sniffer().sniff(
                muestra,
                delimiters=",;\t"
            )
            delimitador = dialecto.delimiter
        except csv.Error:
            delimitador = "\t" if nombre.endswith(".txt") else ","

        datos = list(csv.reader(
            io.StringIO(texto),
            delimiter=delimitador
        ))

    else:
        raise ValueError(
            "Formato no permitido. Utiliza Excel (.xlsx), CSV o TXT."
        )

    if not datos:
        raise ValueError("El archivo está vacío.")

    encabezados = [
        normalizar_encabezado(valor)
        for valor in datos[0]
    ]

    if len(encabezados) != len(set(encabezados)):
        raise ValueError("El archivo contiene encabezados repetidos.")

    faltantes = [
        campo for campo in CAMPOS_IMPORTACION
        if campo not in encabezados
    ]

    if faltantes:
        raise ValueError(
            "Faltan estas columnas: " + ", ".join(faltantes)
        )

    registros = []

    for numero_fila, fila in enumerate(datos[1:], start=2):

        # IGNORAR FILAS VACÍAS
        if not fila or all(
            valor is None or str(valor).strip() == ""
            for valor in fila
        ):
            continue

        fila = list(fila)

        if len(fila) < len(encabezados):
            fila.extend([None] * (len(encabezados) - len(fila)))

        registro = {}

        for campo in CAMPOS_IMPORTACION:
            indice = encabezados.index(campo)
            valor = fila[indice] if indice < len(fila) else None

            # EVITAR NÚMEROS TERMINADOS EN .0
            if isinstance(valor, float) and valor.is_integer():
                valor = int(valor)

            registro[campo] = (
                str(valor).strip()
                if valor is not None
                else ""
            )

        registro["_fila"] = numero_fila
        registros.append(registro)

    if not registros:
        raise ValueError("No se encontraron registros para importar.")

    if len(registros) > 500:
        raise ValueError(
            "El archivo no puede contener más de 500 registros."
        )

    return contenido, registros


# ==========================================
# VALIDAR REGISTROS DE IMPORTACIÓN
# ==========================================

def validar_registros_importacion(registros):
    errores = []
    documentos_archivo = set()
    correos_archivo = set()

    tipos = list(TDoc.objects.all())

    for registro in registros:
        fila = registro["_fila"]

        tipo = registro["tipo_documento"]
        documento = registro["numero_documento"]
        correo = registro["correo"]
        rol = registro["rol"]
        estado = registro["estado"]
        contrasena = registro["contrasena"]

        registro["_tipo_doc"] = None

        # TIPO DE DOCUMENTO
        tipo_doc = next(
            (
                t for t in tipos
                if str(t.id_doc) == tipo
                or (t.tipo_doc or "").strip().lower() == tipo.lower()
            ),
            None
        )

        if tipo_doc is None:
            errores.append(
                f"Fila {fila}: tipo de documento no válido."
            )
        else:
            registro["_tipo_doc"] = tipo_doc

        # DOCUMENTO
        if not documento.isdigit():
            errores.append(
                f"Fila {fila}: el documento debe contener solo números."
            )
        elif (
            len(documento) > 30
            or int(documento) <= 0
            or int(documento) > 9223372036854775807
        ):
            errores.append(
                f"Fila {fila}: número de documento no válido."
            )

        # CORREO
        try:
            validate_email(correo)
        except ValidationError:
            errores.append(
                f"Fila {fila}: correo electrónico no válido."
            )

        if len(correo) > 50:
            errores.append(
                f"Fila {fila}: el correo supera los 50 caracteres."
            )

        if rol == "Empleado" and len(correo) > 30:
            errores.append(
                f"Fila {fila}: el correo del empleado supera los 30 caracteres."
            )

        # ROL Y ESTADO
        if rol not in ["Empleado", "Administrador"]:
            errores.append(
                f"Fila {fila}: solo se permiten Empleado y Administrador."
            )

        if estado not in ["Activo", "Inactivo"]:
            errores.append(
                f"Fila {fila}: estado no válido."
            )

        # NOMBRES DEL EMPLEADO
        if rol == "Empleado":
            if not registro["primer_nombre"] or not registro["primer_apellido"]:
                errores.append(
                    f"Fila {fila}: el empleado necesita primer nombre y primer apellido."
                )

            if (
                len(registro["primer_nombre"]) > 15
                or len(registro["segundo_nombre"]) > 15
            ):
                errores.append(
                    f"Fila {fila}: los nombres superan los 15 caracteres."
                )

            if (
                len(registro["primer_apellido"]) > 12
                or len(registro["segundo_apellido"]) > 12
            ):
                errores.append(
                    f"Fila {fila}: los apellidos superan los 12 caracteres."
                )

        # USERNAME Y TELÉFONO
        if len(registro["username"]) > 50:
            errores.append(
                f"Fila {fila}: username supera los 50 caracteres."
            )

        if len(registro["telefono"]) > 20:
            errores.append(
                f"Fila {fila}: teléfono supera los 20 caracteres."
            )

        # CONTRASEÑA
        if len(contrasena) < 6:
            errores.append(
                f"Fila {fila}: contraseña inferior a 6 caracteres."
            )

        if len(contrasena.encode("utf-8")) > 72:
            errores.append(
                f"Fila {fila}: contraseña supera el límite permitido."
            )

        # DUPLICADOS DENTRO DEL ARCHIVO
        correo_normalizado = correo.lower()

        if correo_normalizado in correos_archivo:
            errores.append(
                f"Fila {fila}: correo repetido dentro del archivo."
            )
        else:
            correos_archivo.add(correo_normalizado)

        if documento in documentos_archivo:
            errores.append(
                f"Fila {fila}: documento repetido dentro del archivo."
            )
        else:
            documentos_archivo.add(documento)

        # DUPLICADOS EN USUARIO
        if correo and Usuario.objects.filter(
            correo__iexact=correo
        ).exists():
            errores.append(
                f"Fila {fila}: el correo ya está registrado."
            )

        if documento and Usuario.objects.filter(
            numero_documento=documento
        ).exists():
            errores.append(
                f"Fila {fila}: el documento ya está registrado."
            )

        # DUPLICADOS EN TABLAS RELACIONADAS
        if (
            rol == "Empleado"
            and documento.isdigit()
            and registro["_tipo_doc"]
        ):
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM persona
                    WHERE documento = %s
                """, [int(documento)])

                if cursor.fetchone()[0] > 0:
                    errores.append(
                        f"Fila {fila}: el documento ya existe en persona."
                    )

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM empleado
                    WHERE id_empleado = %s
                """, [int(documento)])

                if cursor.fetchone()[0] > 0:
                    errores.append(
                        f"Fila {fila}: el documento ya existe en empleado."
                    )

    return errores


# ==========================================
# VISTA DE IMPORTACIÓN MASIVA
# ==========================================

@administrador_requerido
def importar_personas(request):
    error = None
    errores = []
    vista_previa = []
    cantidad = 0

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        if not archivo:
            error = "Selecciona un archivo."

        else:
            try:
                contenido, registros = leer_archivo_importacion(archivo)

                errores = validar_registros_importacion(registros)
                cantidad = len(registros)

                # GUARDAR ÚNICAMENTE LA HUELLA DEL ARCHIVO
                huella = hashlib.sha256(contenido).hexdigest()

                request.session["importacion_hash"] = huella
                request.session.modified = True

                # NO MOSTRAR CONTRASEÑAS
                for registro in registros[:10]:
                    vista_previa.append({
                        "fila": registro["_fila"],
                        "documento": registro["numero_documento"],
                        "correo": registro["correo"],
                        "rol": registro["rol"],
                        "estado": registro["estado"],
                    })

            except Exception as excepcion:
                print("ERROR EN VISTA PREVIA:", excepcion)
                error = str(excepcion)

    return render(
        request,
        "panel/importar_personas.html",
        {
            "error": error,
            "errores": errores,
            "vista_previa": vista_previa,
            "cantidad": cantidad,
            "puede_confirmar": (
                request.method == "POST"
                and not error
                and not errores
                and cantidad > 0
            ),
        }
    )


# ==========================================
# CONFIRMAR IMPORTACIÓN MASIVA
# ==========================================

@administrador_requerido
@require_POST
def confirmar_importacion_personas(request):
    archivo = request.FILES.get("archivo")
    error = None

    if not archivo:
        error = "Selecciona nuevamente el mismo archivo."

    else:
        try:
            contenido, registros = leer_archivo_importacion(archivo)

            huella = hashlib.sha256(contenido).hexdigest()
            huella_anterior = request.session.get("importacion_hash")

            if not huella_anterior or huella != huella_anterior:
                error = (
                    "El archivo no coincide con el que se validó. "
                    "Vuelve a realizar la vista previa."
                )

            else:
                errores = validar_registros_importacion(registros)

                if errores:
                    error = (
                        "Los datos cambiaron o dejaron de ser válidos. "
                        "Vuelve a cargar el archivo y revisa los errores."
                    )

                else:
                    with transaction.atomic():

                        for registro in registros:
                            tipo_doc = registro["_tipo_doc"]
                            documento = registro["numero_documento"]
                            correo = registro["correo"]
                            rol = registro["rol"]

                            hash_contrasena = bcrypt.hashpw(
                                registro["contrasena"].encode("utf-8"),
                                bcrypt.gensalt()
                            ).decode("utf-8")

                            # CREAR USUARIO
                            Usuario.objects.create(
                                pkfk_id_doc=tipo_doc,
                                username=registro["username"] or None,
                                telefono=registro["telefono"] or None,
                                correo=correo,
                                numero_documento=documento,
                                contrasena=hash_contrasena,
                                rol=rol,
                                estado=registro["estado"],
                                verificado="SI",
                                premium=False
                            )

                            # CREAR RELACIONES DEL EMPLEADO
                            if rol == "Empleado":
                                with connection.cursor() as cursor:
                                    nuevo_id = generar_id_recuperacion(cursor)
                                    codigo = secrets.randbelow(900000) + 100000

                                    cursor.execute("""
                                        INSERT INTO recuperar_cuenta (
                                            id_recuperar_cuenta,
                                            codigo_verif
                                        )
                                        VALUES (%s, %s)
                                    """, [nuevo_id, codigo])

                                    cursor.execute("""
                                        INSERT INTO persona (
                                            fkpk_id_doc,
                                            documento,
                                            primer_nombre,
                                            segundo_nombre,
                                            primer_apellido,
                                            segundo_apellido,
                                            fk_id_recuperar_cuenta
                                        )
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, [
                                        tipo_doc.id_doc,
                                        int(documento),
                                        registro["primer_nombre"],
                                        registro["segundo_nombre"] or None,
                                        registro["primer_apellido"],
                                        registro["segundo_apellido"] or None,
                                        nuevo_id
                                    ])

                                    cursor.execute("""
                                        INSERT INTO empleado (
                                            pkfk_id_doc,
                                            id_empleado,
                                            correo,
                                            contrasena
                                        )
                                        VALUES (%s, %s, %s, %s)
                                    """, [
                                        tipo_doc.id_doc,
                                        int(documento),
                                        correo,
                                        hash_contrasena
                                    ])

                    request.session.pop("importacion_hash", None)

                    return redirect("/panel/personas/?importados=1")

        except Exception as excepcion:
            print("ERROR EN IMPORTACIÓN MASIVA:", excepcion)

            error = (
                "No se pudo completar la importación. "
                "La operación fue cancelada y no se guardó el lote."
            )

    return render(
        request,
        "panel/importar_personas.html",
        {
            "error": error,
            "errores": [],
            "vista_previa": [],
            "cantidad": 0,
            "puede_confirmar": False,
        }
    )
    
    
# ==========================================
# ACTIVAR / DESACTIVAR PERSONAS
# ==========================================

@administrador_requerido
@require_POST
def cambiar_estado_persona(request, id_usuario):

    usuario = Usuario.objects.filter(
        id_usuario=id_usuario
    ).first()

    if usuario is None:
        return redirect("/panel/personas/?no_encontrado=1")

    rol = (usuario.rol or "").strip().lower()

    if rol not in ["administrador", "empleado"]:
        return redirect("/panel/personas/?accion_no_permitida=1")

    # Evitar desactivar la cuenta con la que se inició sesión.
    if str(request.session.get("admin_id")) == str(usuario.id_usuario):
        return redirect("/panel/personas/?no_puede_desactivarse=1")

    estado_actual = (usuario.estado or "").strip().lower()

    if estado_actual == "activo":
        nuevo_estado = "Inactivo"
    else:
        nuevo_estado = "Activo"

    try:
        usuario.estado = nuevo_estado
        usuario.save(update_fields=["estado"])

        if nuevo_estado == "Activo":
            return redirect("/panel/personas/?activado=1")

        return redirect("/panel/personas/?desactivado=1")

    except Exception as excepcion:
        print("ERROR AL CAMBIAR ESTADO:", excepcion)
        return redirect("/panel/personas/?estado_error=1")



# ==========================================
# ELIMINAR PERSONAS
# ==========================================

@administrador_requerido
@require_POST
def eliminar_persona(request, id_usuario):

    # VALIDAR LA PALABRA DE CONFIRMACIÓN
    confirmacion = request.POST.get(
        "confirmacion", ""
    ).strip().upper()

    if confirmacion != "ELIMINAR":
        return redirect(
            "/panel/personas/?confirmacion_invalida=1"
        )

    usuario = Usuario.objects.filter(
        id_usuario=id_usuario
    ).first()

    if usuario is None:
        return redirect("/panel/personas/?no_encontrado=1")

    rol = (usuario.rol or "").strip().lower()

    # SOLO SE PERMITE ELIMINAR ADMINISTRADORES Y EMPLEADOS.
    if rol not in ["administrador", "empleado"]:
        return redirect(
            "/panel/personas/?accion_no_permitida=1"
        )

    # EVITAR ELIMINAR LA CUENTA DE LA SESIÓN ACTUAL.
    if str(request.session.get("admin_id")) == str(usuario.id_usuario):
        return redirect(
            "/panel/personas/?no_puede_eliminarse=1"
        )

    tipo_documento_id = usuario.pkfk_id_doc_id
    numero_documento = usuario.numero_documento
    id_recuperacion = None

    try:
        with transaction.atomic():

            if rol == "empleado":

                with connection.cursor() as cursor:

                    # OBTENER EL ID DE RECUPERACIÓN.
                    cursor.execute("""
                        SELECT fk_id_recuperar_cuenta
                        FROM persona
                        WHERE fkpk_id_doc = %s
                          AND documento = %s
                    """, [
                        tipo_documento_id,
                        numero_documento
                    ])

                    fila = cursor.fetchone()

                    if fila:
                        id_recuperacion = fila[0]

                    # ELIMINAR REGISTRO DE EMPLEADO.
                    cursor.execute("""
                        DELETE FROM empleado
                        WHERE pkfk_id_doc = %s
                          AND id_empleado = %s
                    """, [
                        tipo_documento_id,
                        numero_documento
                    ])

                    # ELIMINAR DATOS PERSONALES.
                    cursor.execute("""
                        DELETE FROM persona
                        WHERE fkpk_id_doc = %s
                          AND documento = %s
                    """, [
                        tipo_documento_id,
                        numero_documento
                    ])

            # ELIMINAR USUARIO.
            with connection.cursor() as cursor:

                cursor.execute("""
                    DELETE FROM usuario
                    WHERE id_usuario = %s
                """, [usuario.id_usuario])

                if cursor.rowcount != 1:
                    raise ValueError(
                        "No fue posible eliminar el usuario."
                    )

                # ELIMINAR REGISTRO DE RECUPERACIÓN.
                if id_recuperacion is not None:

                    cursor.execute("""
                        DELETE FROM recuperar_cuenta
                        WHERE id_recuperar_cuenta = %s
                    """, [id_recuperacion])

        return redirect("/panel/personas/?eliminado=1")

    except Exception as excepcion:

        print("ERROR AL ELIMINAR PERSONA:", excepcion)

        # LA TRANSACCIÓN REVIERTE LOS CAMBIOS
        # SI ALGUNA RELACIÓN IMPIDE LA ELIMINACIÓN.
        return redirect(
            "/panel/personas/?eliminacion_error=1"
        )

# ==========================================
# DENUNCIAS: LISTADO Y FILTROS
# ==========================================

@administrador_requerido
def denuncias(request):

    filtros_validos = [
        "pendiente",
        "en_revision",
        "resuelta",
        "rechazada",
    ]

    filtro = request.GET.get("filtro", "pendiente").strip()

    if filtro not in filtros_validos:
        filtro = "pendiente"

    denuncias_lista = (
        UsuarioDenuncias.objects
        .select_related(
            "id_usuario_denunciante",
            "id_usuario_denunciado",
        )
        .filter(estado=filtro)
        .order_by("-fecha_creacion")
    )

    contexto = {
        "correo": request.session.get("admin_correo"),
        "filtro": filtro,
        "denuncias": denuncias_lista,

        "total_pendientes": UsuarioDenuncias.objects.filter(
            estado="pendiente"
        ).count(),

        "total_revision": UsuarioDenuncias.objects.filter(
            estado="en_revision"
        ).count(),

        "total_resueltas": UsuarioDenuncias.objects.filter(
            estado="resuelta"
        ).count(),

        "total_rechazadas": UsuarioDenuncias.objects.filter(
            estado="rechazada"
        ).count(),

        "mensaje": request.GET.get("msg"),
    }

    return render(
        request,
        "panel/denuncias.html",
        contexto
    )


# ==========================================
# DENUNCIAS: RESPONDER Y CAMBIAR ESTADO
# ==========================================

@administrador_requerido
@require_POST
def responder_denuncia(request):

    id_denuncia = request.POST.get("id_denuncia", "").strip()
    estado = request.POST.get("estado", "").strip()
    respuesta = request.POST.get("respuesta", "").strip()

    estados_permitidos = [
        "resuelta",
        "rechazada",
        "en_revision",
    ]

    if not id_denuncia.isdigit():
        return redirect("/panel/denuncias/?error=id")

    if estado not in estados_permitidos:
        return redirect("/panel/denuncias/?error=estado")

    if not respuesta:
        return redirect("/panel/denuncias/?error=respuesta")

    denuncia = UsuarioDenuncias.objects.filter(
        id_denuncia=int(id_denuncia)
    ).first()

    if denuncia is None:
        return redirect("/panel/denuncias/?error=no_encontrada")

    try:
        denuncia.estado = estado
        denuncia.respuesta = respuesta
        denuncia.fecha_respuesta = timezone.now()

        denuncia.save(
            update_fields=[
                "estado",
                "respuesta",
                "fecha_respuesta",
            ]
        )

        return redirect(
            "/panel/denuncias/?filtro=" + estado + "&msg=respondida"
        )

    except Exception as excepcion:
        print("ERROR AL RESPONDER DENUNCIA:", excepcion)

        return redirect(
            "/panel/denuncias/?error=guardar"
        )


# ==========================================
# PREGUNTAS DE USUARIOS: LISTADO Y FILTROS
# ==========================================

@administrador_requerido
def preguntas(request):

    filtros_validos = [
        "pendiente",
        "respondida",
        "cerrada",
    ]

    filtro = request.GET.get("filtro", "pendiente").strip()

    if filtro not in filtros_validos:
        filtro = "pendiente"

    preguntas_lista = (
        UsuarioPreguntas.objects
        .select_related("id_usuario")
        .filter(estado=filtro)
        .order_by("-fecha_creacion")
    )

    contexto = {
        "correo": request.session.get("admin_correo"),
        "filtro": filtro,
        "preguntas": preguntas_lista,

        "total_pendientes": UsuarioPreguntas.objects.filter(
            estado="pendiente"
        ).count(),

        "total_respondidas": UsuarioPreguntas.objects.filter(
            estado="respondida"
        ).count(),

        "total_cerradas": UsuarioPreguntas.objects.filter(
            estado="cerrada"
        ).count(),

        "mensaje": request.GET.get("msg"),
    }

    return render(
        request,
        "panel/preguntas.html",
        contexto
    )


# ==========================================
# PREGUNTAS DE USUARIOS: RESPONDER
# ==========================================

@administrador_requerido
@require_POST
def responder_pregunta(request):

    id_pregunta = request.POST.get("id_pregunta", "").strip()
    respuesta = request.POST.get("respuesta", "").strip()

    if not id_pregunta.isdigit():
        return redirect("/panel/preguntas/?error=id")

    if not respuesta:
        return redirect("/panel/preguntas/?error=respuesta")

    pregunta = UsuarioPreguntas.objects.filter(
        id_pregunta=int(id_pregunta)
    ).first()

    if pregunta is None:
        return redirect("/panel/preguntas/?error=no_encontrada")

    if pregunta.estado != "pendiente":
        return redirect("/panel/preguntas/?error=estado")

    try:
        pregunta.respuesta = respuesta
        pregunta.estado = "respondida"
        pregunta.fecha_respuesta = timezone.now()

        pregunta.save(
            update_fields=[
                "respuesta",
                "estado",
                "fecha_respuesta",
            ]
        )

        return redirect(
            "/panel/preguntas/?filtro=respondida&msg=respondida"
        )

    except Exception as excepcion:
        print("ERROR AL RESPONDER PREGUNTA:", excepcion)

        return redirect(
            "/panel/preguntas/?error=guardar"
        )


# ==========================================
# SOLICITUDES DE ENTREGA: LISTADO (SOLO LECTURA)
# ==========================================

@administrador_requerido
def solicitudes_entrega(request):

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                i.*,
                p.nombre_producto,
                COALESCE(NULLIF(us.username, ''), us.correo)
                    AS nombre_solicitante,
                COALESCE(NULLIF(up.username, ''), up.correo)
                    AS nombre_propietario,
                us.correo AS correo_solicitante,
                up.correo AS correo_propietario
            FROM intercambios i
            LEFT JOIN productos p
                ON p.id_producto = i.id_producto
            LEFT JOIN usuario us
                ON us.id_usuario = i.id_solicitante
            LEFT JOIN usuario up
                ON up.id_usuario = i.id_propietario
            ORDER BY i.creado_en DESC
        """)

        columnas = [
            columna[0]
            for columna in cursor.description
        ]

        solicitudes = [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]

    contexto = {
        "correo": request.session.get("admin_correo"),
        "solicitudes_entrega": solicitudes,
        "total_solicitudes": len(solicitudes),
    }

    return render(
        request,
        "panel/solicitudes.html",
        contexto
    )

# ==========================================
# REPORTES: FILTROS Y CONSULTAS
# ==========================================

def leer_filtros_reportes(request):
    tipos_validos = [
        "todos",
        "usuarios",
        "productos",
        "categorias",
        "solicitudes",
    ]

    tipo = request.GET.get("tipo", "todos").strip()

    if tipo not in tipos_validos:
        tipo = "todos"

    try:
        categoria = int(request.GET.get("categoria", "0"))
        if categoria < 0:
            categoria = 0
    except (ValueError, TypeError):
        categoria = 0

    rol = request.GET.get("rol", "").strip()[:50]

    fecha_inicio = request.GET.get("fecha_inicio", "").strip()
    fecha_fin = request.GET.get("fecha_fin", "").strip()

    errores = []

    # Validar fechas
    try:
        if fecha_inicio:
            date.fromisoformat(fecha_inicio)
    except ValueError:
        fecha_inicio = ""
        errores.append("La fecha inicial no es válida.")

    try:
        if fecha_fin:
            date.fromisoformat(fecha_fin)
    except ValueError:
        fecha_fin = ""
        errores.append("La fecha final no es válida.")

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        fecha_inicio = ""
        fecha_fin = ""
        errores.append(
            "La fecha inicial no puede ser posterior a la fecha final."
        )

    return {
        "tipo": tipo,
        "categoria": categoria,
        "rol": rol,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }, errores


def ejecutar_consulta_reporte(sql, parametros=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, parametros or [])

        columnas = [
            columna[0]
            for columna in cursor.description
        ]

        return [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]


def obtener_datos_reporte(filtros):
    datos = {}

    # ==========================================
    # INDICADORES GENERALES
    # ==========================================

    consultas_kpi = {
        "totalUsuarios": """
            SELECT COUNT(*) AS total
            FROM usuario
        """,

        "totalProductos": """
            SELECT COUNT(*) AS total
            FROM productos
        """,

        "totalCategorias": """
            SELECT COUNT(*) AS total
            FROM categorias
        """,

        "usuariosActivos": """
            SELECT COUNT(*) AS total
            FROM usuario
            WHERE LOWER(estado) = 'activo'
        """,

        "usuariosInactivos": """
            SELECT COUNT(*) AS total
            FROM usuario
            WHERE LOWER(estado) <> 'activo'
               OR estado IS NULL
        """,

        "usuariosVerificados": """
            SELECT COUNT(*) AS total
            FROM usuario
            WHERE verificado = 'SI'
               OR verificado = '1'
        """,

        "productosConImagen": """
            SELECT COUNT(*) AS total
            FROM productos
            WHERE imagen IS NOT NULL
              AND imagen <> ''
              AND imagen <> 'null'
        """,

        "productosSinImagen": """
            SELECT COUNT(*) AS total
            FROM productos
            WHERE imagen IS NULL
               OR imagen = ''
               OR imagen = 'null'
        """,

        "valorTotalProductos": """
            SELECT COALESCE(SUM(valor_estimado), 0) AS total
            FROM productos
            WHERE valor_estimado > 0
        """,
    }

    for nombre, sql in consultas_kpi.items():
        resultado = ejecutar_consulta_reporte(sql)
        datos[nombre] = resultado[0]["total"] or 0

    # ==========================================
    # USUARIOS POR ROL
    # ==========================================

    sql_roles = """
        SELECT
            CASE
                WHEN rol IS NULL OR rol = '' THEN 'Sin rol'
                ELSE rol
            END AS rol,
            COUNT(*) AS total
        FROM usuario
    """

    parametros = []

    if filtros["rol"]:
        sql_roles += " WHERE rol = %s"
        parametros.append(filtros["rol"])

    sql_roles += """
        GROUP BY
            CASE
                WHEN rol IS NULL OR rol = '' THEN 'Sin rol'
                ELSE rol
            END
        ORDER BY total DESC
    """

    datos["usuariosPorRol"] = ejecutar_consulta_reporte(
        sql_roles,
        parametros
    )

    # ==========================================
    # PRODUCTOS POR CATEGORÍA
    # ==========================================

    sql_categorias = """
        SELECT
            c.n_categoria,
            COUNT(p.id_producto) AS total,
            COALESCE(SUM(p.valor_estimado), 0) AS valor_total
        FROM categorias c
        LEFT JOIN productos p
            ON c.id_categoria = p.fk_id_categoria
    """

    parametros = []

    if filtros["categoria"] > 0:
        sql_categorias += " WHERE c.id_categoria = %s"
        parametros.append(filtros["categoria"])

    sql_categorias += """
        GROUP BY c.id_categoria, c.n_categoria
        ORDER BY total DESC
    """

    datos["productosPorCategoria"] = ejecutar_consulta_reporte(
        sql_categorias,
        parametros
    )

    # ==========================================
    # TOP 10 PRODUCTOS MÁS VALIOSOS
    # ==========================================

    sql_top = """
        SELECT
            p.nombre_producto,
            p.valor_estimado,
            c.n_categoria,
            u.username
        FROM productos p
        LEFT JOIN categorias c
            ON p.fk_id_categoria = c.id_categoria
        LEFT JOIN usuario u
            ON p.fk_id_usuario = u.id_usuario
        WHERE p.valor_estimado > 0
    """

    parametros = []

    if filtros["categoria"] > 0:
        sql_top += " AND p.fk_id_categoria = %s"
        parametros.append(filtros["categoria"])

    sql_top += """
        ORDER BY p.valor_estimado DESC
        LIMIT 10
    """

    datos["topProductos"] = ejecutar_consulta_reporte(
        sql_top,
        parametros
    )

    # ==========================================
    # ÚLTIMOS PRODUCTOS
    # ==========================================

    sql_ultimos_productos = """
        SELECT
            p.nombre_producto,
            p.valor_estimado,
            c.n_categoria,
            u.username,
            p.imagen
        FROM productos p
        LEFT JOIN categorias c
            ON p.fk_id_categoria = c.id_categoria
        LEFT JOIN usuario u
            ON p.fk_id_usuario = u.id_usuario
    """

    parametros = []

    if filtros["categoria"] > 0:
        sql_ultimos_productos += """
            WHERE p.fk_id_categoria = %s
        """
        parametros.append(filtros["categoria"])

    sql_ultimos_productos += """
        ORDER BY p.id_producto DESC
        LIMIT 5
    """

    datos["ultimosProductos"] = ejecutar_consulta_reporte(
        sql_ultimos_productos,
        parametros
    )

    # ==========================================
    # ÚLTIMOS USUARIOS
    # ==========================================

    sql_ultimos_usuarios = """
        SELECT
            id_usuario,
            username,
            correo,
            rol,
            estado,
            verificado
        FROM usuario
    """

    parametros = []

    if filtros["rol"]:
        sql_ultimos_usuarios += " WHERE rol = %s"
        parametros.append(filtros["rol"])

    sql_ultimos_usuarios += """
        ORDER BY id_usuario DESC
        LIMIT 10
    """

    datos["ultimosUsuarios"] = ejecutar_consulta_reporte(
        sql_ultimos_usuarios,
        parametros
    )

    # ==========================================
    # SOLICITUDES DE ENTREGA
    # ==========================================

    sql_solicitudes = """
        SELECT
            i.id_intercambio,
            i.estado,
            i.estado_entrega,
            i.direccion_recogida,
            i.direccion,
            i.creado_en,
            p.nombre_producto,
            COALESCE(
                NULLIF(us.username, ''),
                us.correo
            ) AS nombre_solicitante
        FROM intercambios i
        LEFT JOIN productos p
            ON p.id_producto = i.id_producto
        LEFT JOIN usuario us
            ON us.id_usuario = i.id_solicitante
        WHERE 1 = 1
    """

    parametros = []

    if filtros["fecha_inicio"]:
        sql_solicitudes += """
            AND i.creado_en >= %s
        """
        parametros.append(
            filtros["fecha_inicio"] + " 00:00:00"
        )

    if filtros["fecha_fin"]:
        sql_solicitudes += """
            AND i.creado_en <= %s
        """
        parametros.append(
            filtros["fecha_fin"] + " 23:59:59"
        )

    sql_solicitudes += """
        ORDER BY i.creado_en DESC
    """

    solicitudes = ejecutar_consulta_reporte(
        sql_solicitudes,
        parametros
    )

    datos["solicitudesEntrega"] = solicitudes
    datos["totalSolicitudesEntrega"] = len(solicitudes)

    # Agrupar solicitudes por estado
    solicitudes_por_estado = {}

    for solicitud in solicitudes:
        estado = solicitud["estado_entrega"] or "Pendiente"

        solicitudes_por_estado[estado] = (
            solicitudes_por_estado.get(estado, 0) + 1
        )

    datos["solicitudesPorEstado"] = solicitudes_por_estado

    return datos


# ==========================================
# PÁGINA PRINCIPAL DE REPORTES
# ==========================================

@administrador_requerido
def reportes(request):
    filtros, errores = leer_filtros_reportes(request)

    datos = obtener_datos_reporte(filtros)

    categorias = ejecutar_consulta_reporte("""
        SELECT id_categoria, n_categoria
        FROM categorias
        ORDER BY n_categoria
    """)

    roles = ejecutar_consulta_reporte("""
        SELECT DISTINCT rol
        FROM usuario
        WHERE rol IS NOT NULL
          AND rol <> ''
        ORDER BY rol
    """)

    contexto = {
        **datos,
        "filtros": filtros,
        "categoriasDisponibles": categorias,
        "rolesDisponibles": roles,
        "errores_filtros": errores,
        "correo": request.session.get("admin_correo"),
    }

    return render(
        request,
        "panel/reportes.html",
        contexto
    )


# ==========================================
# VERSIÓN IMPRIMIBLE DE REPORTES
# ==========================================

@administrador_requerido
def reportes_imprimir(request):
    filtros, errores = leer_filtros_reportes(request)

    datos = obtener_datos_reporte(filtros)

    contexto = {
        **datos,
        "filtros": filtros,
        "errores_filtros": errores,
        "correo": request.session.get("admin_correo"),
    }

    return render(
        request,
        "panel/reportes_imprimir.html",
        contexto
    )


# ==========================================
# USUARIOS PREMIUM (PAGOS) + FILTROS + PDF
# ==========================================

PLANES_PREMIUM = ["1 mes", "3 meses", "12 meses"]

ESTADO_SUSCRIPCION_SQL = """
    CASE
        WHEN up.id_premium IS NULL THEN 'sin_suscripcion'
        WHEN up.estado IN ('activo', 'cancelado')
             AND (up.fecha_fin IS NULL OR up.fecha_fin > CURRENT_TIMESTAMP)
            THEN up.estado
        ELSE 'vencido'
    END
"""


def _consulta_premium(request):
    plan = request.GET.get("plan", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    estado = request.GET.get("estado", "").strip()

    if plan not in PLANES_PREMIUM:
        plan = ""
    if not categoria.isdigit():
        categoria = ""
    if estado not in ("vigentes", "vencidos"):
        estado = ""

    sql = f"""
        SELECT pp.id_pago, pp.referencia, pp.plan, pp.monto, pp.creado_en,
               u.id_usuario, u.correo, u.telefono,
               COALESCE(NULLIF(TRIM(u.nombre), ''), NULLIF(TRIM(u.username), ''), u.correo) AS nombre,
               up.plan AS plan_actual, up.fecha_fin,
               {ESTADO_SUSCRIPCION_SQL} AS estado_suscripcion,
               (SELECT GROUP_CONCAT(DISTINCT c.n_categoria ORDER BY c.n_categoria SEPARATOR ', ')
                  FROM productos p
                  JOIN categorias c ON c.id_categoria = p.fk_id_categoria
                 WHERE p.fk_id_usuario = u.id_usuario
                   AND COALESCE(p.estado, 'Activo') = 'Activo') AS categorias_productos
          FROM pago_premium pp
          JOIN usuario u ON u.id_usuario = pp.id_usuario
          LEFT JOIN usuario_premium up ON up.id_usuario = u.id_usuario
         WHERE pp.estado = 'exitoso'
    """
    params = []

    if plan:
        sql += " AND pp.plan = %s"
        params.append(plan)

    if categoria:
        sql += """
            AND EXISTS (SELECT 1 FROM productos p
                         WHERE p.fk_id_usuario = u.id_usuario
                           AND p.fk_id_categoria = %s
                           AND COALESCE(p.estado, 'Activo') = 'Activo')
        """
        params.append(int(categoria))

    if estado == "vigentes":
        sql += f" AND {ESTADO_SUSCRIPCION_SQL} IN ('activo', 'cancelado')"
    elif estado == "vencidos":
        sql += f" AND {ESTADO_SUSCRIPCION_SQL} NOT IN ('activo', 'cancelado')"

    sql += " ORDER BY pp.creado_en DESC, pp.id_pago DESC"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columnas = [col[0] for col in cursor.description]
        pagos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        cursor.execute("SELECT id_categoria, n_categoria FROM categorias ORDER BY n_categoria")
        categorias = [
            {"id": fila[0], "nombre": fila[1]} for fila in cursor.fetchall()
        ]

    etiquetas_estado = {
        "activo": "Vigente",
        "cancelado": "Vigente (renovación cancelada)",
        "vencido": "Vencido",
        "sin_suscripcion": "Sin suscripción",
    }
    for pago in pagos:
        pago["estado_texto"] = etiquetas_estado.get(pago["estado_suscripcion"], "—")
        pago["vigente"] = pago["estado_suscripcion"] in ("activo", "cancelado")
        pago["monto_texto"] = f"{int(pago['monto'] or 0):,}".replace(",", ".")

    nombre_categoria = next(
        (c["nombre"] for c in categorias if str(c["id"]) == categoria), ""
    )

    descripcion = []
    if plan:
        descripcion.append(f"Plan: {plan}")
    if nombre_categoria:
        descripcion.append(f"Categoría: {nombre_categoria}")
    if estado:
        descripcion.append("Suscripción: " + ("vigentes" if estado == "vigentes" else "vencidas"))

    por_plan = {p: 0 for p in PLANES_PREMIUM}
    for pago in pagos:
        if pago["plan"] in por_plan:
            por_plan[pago["plan"]] += 1

    query = request.GET.copy()

    return {
        "pagos": pagos,
        "categorias": categorias,
        "planes": PLANES_PREMIUM,
        "filtro_plan": plan,
        "filtro_categoria": categoria,
        "filtro_estado": estado,
        "filtros_texto": " · ".join(descripcion) or "Todos los pagos premium",
        "total_pagos": len(pagos),
        "total_usuarios": len({p["id_usuario"] for p in pagos}),
        "total_recaudado": f"{int(sum(float(p['monto'] or 0) for p in pagos)):,}".replace(",", "."),
        "por_plan": por_plan,
        "querystring": query.urlencode(),
        "correo": request.session.get("admin_correo"),
    }


@administrador_requerido
def premium_usuarios(request):
    return render(request, "panel/premium.html", _consulta_premium(request))


@administrador_requerido
def premium_imprimir(request):
    return render(request, "panel/premium_imprimir.html", _consulta_premium(request))
