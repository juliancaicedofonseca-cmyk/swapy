from django.urls import path
from . import views


urlpatterns = [

    # ==========================================
    # AUTENTICACIÓN
    # ==========================================

    path(
        "login/",
        views.login_admin,
        name="panel_login"
    ),

    path(
        "sso/",
        views.sso_desde_php,
        name="panel_sso"
    ),

    path(
        "logout/",
        views.logout_admin,
        name="panel_logout"
    ),

    # ==========================================
    # INICIO
    # ==========================================

    path(
        "dashboard/",
        views.dashboard,
        name="panel_dashboard"
    ),

    # ==========================================
    # PERSONAS REGISTRADAS
    # ==========================================

    path(
        "personas/",
        views.personas,
        name="panel_personas"
    ),

    path(
        "personas/crear/",
        views.crear_persona,
        name="panel_crear_persona"
    ),

    path(
        "personas/editar/<int:id_usuario>/",
        views.editar_persona,
        name="panel_editar_persona"
    ),

    path(
        "personas/estado/<int:id_usuario>/",
        views.cambiar_estado_persona,
        name="panel_cambiar_estado"
    ),

    path(
        "personas/eliminar/<int:id_usuario>/",
        views.eliminar_persona,
        name="panel_eliminar_persona"
    ),

    path(
        "personas/importar/",
        views.importar_personas,
        name="panel_importar_personas"
    ),

    path(
        "personas/importar/confirmar/",
        views.confirmar_importacion_personas,
        name="panel_confirmar_importacion"
    ),

    # ==========================================
    # DENUNCIAS
    # ==========================================

    path(
        "denuncias/",
        views.denuncias,
        name="panel_denuncias"
    ),

    path(
        "denuncias/responder/",
        views.responder_denuncia,
        name="panel_responder_denuncia"
    ),

    # ==========================================
    # PREGUNTAS DE USUARIOS
    # ==========================================

    path(
        "preguntas/",
        views.preguntas,
        name="panel_preguntas"
    ),

    path(
        "preguntas/responder/",
        views.responder_pregunta,
        name="panel_responder_pregunta"
    ),

    # ==========================================
    # SOLICITUDES DE ENTREGA
    # ==========================================

    path(
        "solicitudes/",
        views.solicitudes_entrega,
        name="panel_solicitudes"
    ),
    
    path(
    "reportes/",
    views.reportes,
    name="panel_reportes"
),

path(
    "reportes/imprimir/",
    views.reportes_imprimir,
    name="panel_reportes_imprimir"
),

    # ==========================================
    # USUARIOS PREMIUM
    # ==========================================

    path(
        "premium/",
        views.premium_usuarios,
        name="panel_premium"
    ),

    path(
        "premium/imprimir/",
        views.premium_imprimir,
        name="panel_premium_imprimir"
    ),

]