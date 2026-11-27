<?php

namespace App\Controllers;

class ReporteController extends BaseController
{
    public function index()
    {
        $session = \Config\Services::session();
        
        if (!$session->get('isLoggedIn') || strtolower($session->get('rol') ?? '') !== 'administrador') {
            return redirect()->to(base_url('?login_error=acceso'));
        }

        $db = \Config\Database::connect();

        $filtros = $this->leerFiltros();
        $data = $this->obtenerDatosReporte($db, $filtros);
        $data['filtros'] = $filtros;
        $data['categoriasDisponibles'] = $db->query("SELECT id_categoria, n_categoria FROM categorias ORDER BY n_categoria")->getResultArray();
        $data['rolesDisponibles'] = $db->query("SELECT DISTINCT rol FROM usuario WHERE rol IS NOT NULL AND rol <> '' ORDER BY rol")->getResultArray();

        return view('reportes', $data);
    }

    // ==================== VERSIÓN IMPRIMIBLE PARA PDF ====================
    public function imprimir()
    {
        $session = \Config\Services::session();
        
        if (!$session->get('isLoggedIn') || strtolower($session->get('rol') ?? '') !== 'administrador') {
            return redirect()->to(base_url('?login_error=acceso'));
        }

        $db = \Config\Database::connect();

        $filtros = $this->leerFiltros();
        $data = $this->obtenerDatosReporte($db, $filtros);
        $data['filtros'] = $filtros;

        return view('reportes_imprimir', $data);
    }

    /**
     * Lee y sanitiza los filtros que llegan por GET: categoría, rol de
     * usuario y rango de fechas (aplicado a las solicitudes de entrega,
     * que es la única tabla del sistema con fecha de creación real).
     */
    private function leerFiltros(): array
    {
        $request = \Config\Services::request();

        $tipo = trim((string) ($request->getGet('tipo') ?? 'todos'));
        $tiposValidos = ['todos', 'usuarios', 'productos', 'categorias', 'solicitudes'];
        if (!in_array($tipo, $tiposValidos, true)) {
            $tipo = 'todos';
        }

        return [
            'tipo'         => $tipo,
            'categoria'    => (int) ($request->getGet('categoria') ?? 0),
            'rol'          => trim((string) ($request->getGet('rol') ?? '')),
            'fecha_inicio' => trim((string) ($request->getGet('fecha_inicio') ?? '')),
            'fecha_fin'    => trim((string) ($request->getGet('fecha_fin') ?? '')),
        ];
    }

    /**
     * Arma todos los datos del reporte aplicando los filtros recibidos.
     * Se usa tanto para la vista en pantalla como para la versión imprimible,
     * así el PDF (imprimir/guardar como PDF) respeta los mismos filtros.
     */
    private function obtenerDatosReporte($db, array $filtros): array
    {
        $data = [];

        // ==================== KPIs GENERALES (no se filtran: son el total de la plataforma) ====================
        $data['totalUsuarios'] = $db->query("SELECT COUNT(*) as total FROM usuario")->getRow()->total ?? 0;
        $data['totalProductos'] = $db->query("SELECT COUNT(*) as total FROM productos")->getRow()->total ?? 0;
        $data['totalCategorias'] = $db->query("SELECT COUNT(*) as total FROM categorias")->getRow()->total ?? 0;
        $data['usuariosActivos'] = $db->query("SELECT COUNT(*) as total FROM usuario WHERE estado = 'activo'")->getRow()->total ?? 0;
        $data['usuariosInactivos'] = $db->query("SELECT COUNT(*) as total FROM usuario WHERE estado != 'activo' OR estado IS NULL")->getRow()->total ?? 0;
        $data['usuariosVerificados'] = $db->query("SELECT COUNT(*) as total FROM usuario WHERE verificado = 'SI' OR verificado = '1'")->getRow()->total ?? 0;
        $data['productosConImagen'] = $db->query("SELECT COUNT(*) as total FROM productos WHERE imagen IS NOT NULL AND imagen != '' AND imagen != 'null'")->getRow()->total ?? 0;
        $data['productosSinImagen'] = $db->query("SELECT COUNT(*) as total FROM productos WHERE imagen IS NULL OR imagen = '' OR imagen = 'null'")->getRow()->total ?? 0;
        $valorTotal = $db->query("SELECT SUM(valor_estimado) as total FROM productos WHERE valor_estimado > 0")->getRow()->total ?? 0;
        $data['valorTotalProductos'] = $valorTotal;

        // ---- filtro por rol: usuarios por rol ----
        $builderUsuarios = $db->table('usuario')
            ->select("CASE WHEN rol IS NULL OR rol = '' THEN 'Sin rol' ELSE rol END as rol, COUNT(*) as total")
            ->groupBy('rol')
            ->orderBy('total', 'DESC');
        if ($filtros['rol'] !== '') {
            $builderUsuarios->where('rol', $filtros['rol']);
        }
        $data['usuariosPorRol'] = $builderUsuarios->get()->getResultArray();

        // ---- filtro por categoría: productos por categoría ----
        $builderCategorias = $db->table('categorias c')
            ->select('c.n_categoria, COUNT(p.id_producto) as total, COALESCE(SUM(p.valor_estimado), 0) as valor_total')
            ->join('productos p', 'c.id_categoria = p.fk_id_categoria', 'left')
            ->groupBy('c.id_categoria, c.n_categoria')
            ->orderBy('total', 'DESC');
        if ($filtros['categoria'] > 0) {
            $builderCategorias->where('c.id_categoria', $filtros['categoria']);
        }
        $data['productosPorCategoria'] = $builderCategorias->get()->getResultArray();

        // ---- top productos (respeta filtro de categoría) ----
        $builderTop = $db->table('productos p')
            ->select('p.nombre_producto, p.valor_estimado, c.n_categoria, u.username')
            ->join('categorias c', 'p.fk_id_categoria = c.id_categoria', 'left')
            ->join('usuario u', 'p.fk_id_usuario = u.id_usuario', 'left')
            ->where('p.valor_estimado >', 0)
            ->orderBy('p.valor_estimado', 'DESC')
            ->limit(10);
        if ($filtros['categoria'] > 0) {
            $builderTop->where('p.fk_id_categoria', $filtros['categoria']);
        }
        $data['topProductos'] = $builderTop->get()->getResultArray();

        // ---- últimos productos (respeta filtro de categoría) ----
        $builderUltimosProductos = $db->table('productos p')
            ->select('p.nombre_producto, p.valor_estimado, c.n_categoria, u.username, p.imagen')
            ->join('categorias c', 'p.fk_id_categoria = c.id_categoria', 'left')
            ->join('usuario u', 'p.fk_id_usuario = u.id_usuario', 'left')
            ->orderBy('p.id_producto', 'DESC')
            ->limit(5);
        if ($filtros['categoria'] > 0) {
            $builderUltimosProductos->where('p.fk_id_categoria', $filtros['categoria']);
        }
        $data['ultimosProductos'] = $builderUltimosProductos->get()->getResultArray();

        // ---- últimos usuarios (respeta filtro de rol) ----
        $builderUltimosUsuarios = $db->table('usuario')
            ->select('id_usuario, username, correo, rol, estado, verificado')
            ->orderBy('id_usuario', 'DESC')
            ->limit(10);
        if ($filtros['rol'] !== '') {
            $builderUltimosUsuarios->where('rol', $filtros['rol']);
        }
        $data['ultimosUsuarios'] = $builderUltimosUsuarios->get()->getResultArray();

        // ---- solicitudes de entrega (respeta rango de fechas) ----
        $builderSolicitudes = $db->table('intercambios i')
            ->select("i.id_intercambio, i.estado, i.estado_entrega, i.direccion_recogida, i.direccion, i.creado_en,
                      p.nombre_producto,
                      COALESCE(NULLIF(us.username, ''), us.correo) as nombre_solicitante")
            ->join('productos p', 'p.id_producto = i.id_producto', 'left')
            ->join('usuario us', 'us.id_usuario = i.id_solicitante', 'left')
            ->orderBy('i.creado_en', 'DESC');
        if ($filtros['fecha_inicio'] !== '') {
            $builderSolicitudes->where('i.creado_en >=', $filtros['fecha_inicio'] . ' 00:00:00');
        }
        if ($filtros['fecha_fin'] !== '') {
            $builderSolicitudes->where('i.creado_en <=', $filtros['fecha_fin'] . ' 23:59:59');
        }
        $solicitudes = $builderSolicitudes->get()->getResultArray();
        $data['solicitudesEntrega'] = $solicitudes;
        $data['totalSolicitudesEntrega'] = count($solicitudes);
        $porEstadoEntrega = [];
        foreach ($solicitudes as $s) {
            $estado = $s['estado_entrega'] ?: 'Pendiente';
            $porEstadoEntrega[$estado] = ($porEstadoEntrega[$estado] ?? 0) + 1;
        }
        $data['solicitudesPorEstado'] = $porEstadoEntrega;

        return $data;
    }
}