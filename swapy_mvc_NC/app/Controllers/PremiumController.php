<?php

namespace App\Controllers;

class PremiumController extends BaseController
{
    private const DURACIONES = [
        '1' => ['nombre' => '1 mes', 'meses' => 1, 'precio' => 50000],
        '3' => ['nombre' => '3 meses', 'meses' => 3, 'precio' => 130000],
        '12' => ['nombre' => '12 meses', 'meses' => 12, 'precio' => 550000],
    ];

    public function index()
    {
        $session = session();
        $idUsuario = (int) $session->get('id_usuario');

        if (!$session->get('isLoggedIn') || $idUsuario <= 0) {
            return redirect()->to(base_url('?login_error=sesion'));
        }

        if (strtolower((string) $session->get('rol')) !== 'cliente') {
            return redirect()->to(base_url('perfil'));
        }

        $db = db_connect();
        $usuario = $db->table('usuario')
            ->select('id_usuario, premium')
            ->where('id_usuario', $idUsuario)
            ->get()
            ->getRowArray();

        if (!$usuario) {
            $session->destroy();
            return redirect()->to(base_url('?login_error=sesion'));
        }

        // Por si el usuario no volvió por premium/retorno: consulta a Mercado Pago sus pagos pendientes
        $mensajeMp = $this->sincronizarPendientes($idUsuario);
        if ($mensajeMp !== null) {
            $session->setFlashdata('mensaje', $mensajeMp);
            return redirect()->to(base_url('premium'));
        }

        $suscripcion = $db->table('usuario_premium')
            ->where('id_usuario', $idUsuario)
            ->get()
            ->getRowArray();

        $ahora = new \DateTimeImmutable();
        $fechaFin = !empty($suscripcion['fecha_fin'])
            ? new \DateTimeImmutable($suscripcion['fecha_fin'])
            : null;
        $estado = $suscripcion['estado'] ?? null;
        $vigente = $suscripcion !== null
            && in_array($estado, ['activo', 'cancelado'], true)
            && ($fechaFin === null || $fechaFin > $ahora);

        // Mantiene el indicador legado de usuario alineado con la suscripción compartida.
        $premiumActual = $vigente ? 1 : 0;
        if ((int) $usuario['premium'] !== $premiumActual) {
            $db->table('usuario')
                ->where('id_usuario', $idUsuario)
                ->update(['premium' => $premiumActual]);
        }

        if ($suscripcion && in_array($estado, ['activo', 'cancelado'], true)
            && $fechaFin !== null && $fechaFin <= $ahora) {
            $db->table('usuario_premium')
                ->where('id_usuario', $idUsuario)
                ->whereIn('estado', ['activo', 'cancelado'])
                ->update(['estado' => 'vencido']);
            $suscripcion['estado'] = 'vencido';
        }

        $pagos = $db->table('pago_premium')
            ->where('id_usuario', $idUsuario)
            ->where('estado', 'exitoso')
            ->orderBy('creado_en', 'DESC')
            ->get()
            ->getResultArray();

        return view('premium', [
            'suscripcion' => $suscripcion,
            'pagos' => $pagos,
            'vigente' => $vigente,
            'duraciones' => self::DURACIONES,
            'mensaje' => $session->getFlashdata('mensaje'),
        ]);
    }

    public function comprar()
    {
        $session = session();
        $idUsuario = (int) $session->get('id_usuario');

        if (!$session->get('isLoggedIn') || $idUsuario <= 0) {
            return redirect()->to(base_url('?login_error=sesion'));
        }

        if (strtolower((string) $session->get('rol')) !== 'cliente') {
            return redirect()->to(base_url('perfil'));
        }

        $claveDuracion = (string) $this->request->getPost('meses');
        if (!isset(self::DURACIONES[$claveDuracion])) {
            $session->setFlashdata('mensaje', 'La duración seleccionada no es válida.');
            return redirect()->to(base_url('premium'));
        }

        if ($this->tokenMercadoPago() === '') {
            $session->setFlashdata('mensaje', 'Falta configurar el token de Mercado Pago (MERCADOPAGO_ACCESS_TOKEN en .env).');
            return redirect()->to(base_url('premium'));
        }

        $opcion = self::DURACIONES[$claveDuracion];
        $referencia = 'MP-' . strtoupper(bin2hex(random_bytes(6)));
        $db = db_connect();

        // 1. Se registra el pago como pendiente hasta que Mercado Pago lo apruebe
        $db->table('pago_premium')->insert([
            'id_usuario' => $idUsuario,
            'referencia' => $referencia,
            'plan' => $opcion['nombre'],
            'monto' => $opcion['precio'],
            'estado' => 'pendiente',
        ]);

        // 2. Se crea la preferencia de Checkout Pro
        $retorno = base_url('premium/retorno');
        $preferencia = [
            'items' => [[
                'id' => 'premium-' . $claveDuracion,
                'title' => 'Swapy Premium - ' . $opcion['nombre'],
                'quantity' => 1,
                'currency_id' => 'COP',
                'unit_price' => (float) $opcion['precio'],
            ]],
            'external_reference' => $referencia,
            'back_urls' => [
                'success' => $retorno,
                'pending' => $retorno,
                'failure' => $retorno,
            ],
            'auto_return' => 'approved',
        ];

        [$codigo, $respuesta] = $this->mercadoPago('POST', '/checkout/preferences', $preferencia);

        // Mercado Pago puede rechazar auto_return con URLs locales: se reintenta sin él
        if ($codigo >= 400) {
            unset($preferencia['auto_return']);
            [$codigo, $respuesta] = $this->mercadoPago('POST', '/checkout/preferences', $preferencia);
        }

        // Token TEST- => checkout sandbox; token APP_USR- (p. ej. de un usuario de prueba) => checkout normal
        $urlPago = str_starts_with($this->tokenMercadoPago(), 'TEST-')
            ? ($respuesta['sandbox_init_point'] ?? null)
            : ($respuesta['init_point'] ?? null);

        if ($codigo >= 400 || !$urlPago) {
            log_message('error', 'Mercado Pago preferencia: {r}', ['r' => json_encode($respuesta)]);
            $db->table('pago_premium')->where('referencia', $referencia)->update(['estado' => 'fallido']);
            $session->setFlashdata('mensaje', 'No se pudo conectar con Mercado Pago. Revisa el token e inténtalo de nuevo.');
            return redirect()->to(base_url('premium'));
        }

        return redirect()->to($urlPago);
    }

    /**
     * Mercado Pago redirige aquí al terminar el checkout.
     * El estado real se consulta a la API (no se confía en los parámetros de la URL).
     */
    public function retorno()
    {
        $session = session();
        $referencia = (string) $this->request->getGet('external_reference');
        $paymentId = (string) ($this->request->getGet('payment_id') ?: $this->request->getGet('collection_id'));

        $mensaje = 'El pago no se completó. Puedes intentarlo de nuevo.';

        if ($referencia !== '' && ctype_digit($paymentId)) {
            [$codigo, $pago] = $this->mercadoPago('GET', '/v1/payments/' . $paymentId);

            if ($codigo === 200 && ($pago['external_reference'] ?? '') === $referencia) {
                $mensaje = $this->procesarEstadoPago($referencia, (string) ($pago['status'] ?? ''));
            }
        }

        $session->setFlashdata('mensaje', $mensaje);
        return redirect()->to(base_url('premium'));
    }

    /**
     * Aplica el resultado de Mercado Pago a un pago pendiente.
     */
    private function procesarEstadoPago(string $referencia, string $estadoMp): string
    {
        $db = db_connect();
        $registro = $db->table('pago_premium')->where('referencia', $referencia)->get()->getRowArray();

        if (!$registro) {
            return 'No se encontró el pago.';
        }

        if ($registro['estado'] === 'exitoso') {
            return 'Tu pago ya fue aprobado y tu suscripción Premium está activa.';
        }

        if (in_array($estadoMp, ['pending', 'in_process', 'authorized'], true)) {
            return 'Tu pago está en proceso. Se activará cuando Mercado Pago lo apruebe.';
        }

        if ($estadoMp !== 'approved') {
            $db->table('pago_premium')->where('referencia', $referencia)
                ->where('estado', 'pendiente')->update(['estado' => 'fallido']);
            return 'Mercado Pago rechazó el pago. Puedes intentarlo con otro medio.';
        }

        $opcion = null;
        foreach (self::DURACIONES as $duracion) {
            if ($duracion['nombre'] === $registro['plan']) {
                $opcion = $duracion;
            }
        }

        if ($opcion === null) {
            return 'El plan del pago no es válido.';
        }

        $idUsuario = (int) $registro['id_usuario'];
        $ahora = new \DateTimeImmutable();
        $db->transBegin();

        try {
            // Marca el pago como exitoso una sola vez (evita activar dos veces)
            $db->table('pago_premium')->where('referencia', $referencia)
                ->where('estado', 'pendiente')->update(['estado' => 'exitoso']);

            if ($db->affectedRows() === 0) {
                $db->transRollback();
                return 'Tu pago ya fue procesado.';
            }

            $suscripcion = $db->table('usuario_premium')
                ->where('id_usuario', $idUsuario)
                ->get()
                ->getRowArray();

            // Cada pago inicia el día en que se paga y vence exactamente los meses pagados después
            $fechaInicio = $ahora;
            $fechaFin = $this->sumarMesesCalendario($ahora, $opcion['meses']);

            $datosSuscripcion = [
                'fecha_inicio' => $fechaInicio->format('Y-m-d H:i:s'),
                'fecha_fin' => $fechaFin->format('Y-m-d H:i:s'),
                'plan' => $opcion['nombre'],
                'estado' => 'activo',
            ];

            if ($suscripcion) {
                $db->table('usuario_premium')
                    ->where('id_usuario', $idUsuario)
                    ->update($datosSuscripcion);
            } else {
                $db->table('usuario_premium')->insert([
                    'id_usuario' => $idUsuario,
                    ...$datosSuscripcion,
                ]);
            }

            $db->table('usuario')
                ->where('id_usuario', $idUsuario)
                ->update(['premium' => 1]);

            if ($db->transStatus() === false) {
                throw new \RuntimeException('No se pudo guardar el pago.');
            }
            $db->transCommit();

            return '¡Pago aprobado por Mercado Pago! Ya eres Premium ⭐. Tu suscripción de '
                . $opcion['nombre'] . ' está activa hasta el ' . $fechaFin->format('d/m/Y') . '.';
        } catch (\Throwable $e) {
            $db->transRollback();
            log_message('error', 'Error activando Premium: {message}', ['message' => $e->getMessage()]);
            return 'El pago fue aprobado pero no se pudo activar la suscripción. Contacta a soporte.';
        }
    }

    /**
     * Revisa en Mercado Pago los pagos pendientes del usuario y aplica los que ya tengan resultado.
     * Devuelve un mensaje si alguno cambió de estado.
     */
    private function sincronizarPendientes(int $idUsuario): ?string
    {
        if ($this->tokenMercadoPago() === '') {
            return null;
        }

        $pendientes = db_connect()->table('pago_premium')
            ->select('referencia')
            ->where('id_usuario', $idUsuario)
            ->where('estado', 'pendiente')
            ->like('referencia', 'MP-', 'after')
            ->orderBy('id_pago', 'DESC')
            ->limit(10)
            ->get()
            ->getResultArray();

        $mensaje = null;

        foreach ($pendientes as $pendiente) {
            $referencia = $pendiente['referencia'];
            [$codigo, $busqueda] = $this->mercadoPago(
                'GET',
                '/v1/payments/search?external_reference=' . urlencode($referencia)
            );

            if ($codigo !== 200 || empty($busqueda['results'])) {
                continue;
            }

            // Si hay varios intentos para la misma referencia, gana el aprobado
            $estados = array_column($busqueda['results'], 'status');
            $estado = in_array('approved', $estados, true) ? 'approved' : (string) end($estados);

            if (in_array($estado, ['pending', 'in_process', 'authorized'], true)) {
                continue;
            }

            $resultado = $this->procesarEstadoPago($referencia, $estado);
            if ($estado === 'approved') {
                $mensaje = $resultado;
            }
        }

        return $mensaje;
    }

    private function tokenMercadoPago(): string
    {
        return trim((string) env('MERCADOPAGO_ACCESS_TOKEN', ''));
    }

    /**
     * Llamada al API REST de Mercado Pago.
     * @return array{0:int,1:array}
     */
    private function mercadoPago(string $metodo, string $ruta, ?array $cuerpo = null): array
    {
        $curl = curl_init('https://api.mercadopago.com' . $ruta);
        $cabeceras = [
            'Authorization: Bearer ' . $this->tokenMercadoPago(),
            'Content-Type: application/json',
        ];

        if ($cuerpo !== null) {
            $cabeceras[] = 'X-Idempotency-Key: ' . bin2hex(random_bytes(16));
            curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($cuerpo));
        }

        curl_setopt_array($curl, [
            CURLOPT_CUSTOMREQUEST => $metodo,
            CURLOPT_HTTPHEADER => $cabeceras,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 20,
        ]);

        $respuesta = curl_exec($curl);
        $codigo = (int) curl_getinfo($curl, CURLINFO_HTTP_CODE);

        if ($respuesta === false) {
            log_message('error', 'Mercado Pago cURL: {e}', ['e' => curl_error($curl)]);
            $codigo = 0;
        }

        curl_close($curl);

        return [$codigo ?: 500, json_decode((string) $respuesta, true) ?: []];
    }

    public function cancelar()
    {
        $session = session();
        $idUsuario = (int) $session->get('id_usuario');

        if (!$session->get('isLoggedIn') || $idUsuario <= 0) {
            return redirect()->to(base_url('?login_error=sesion'));
        }

        if (strtolower((string) $session->get('rol')) !== 'cliente') {
            return redirect()->to(base_url('perfil'));
        }

        $db = db_connect();
        $db->table('usuario_premium')
            ->where('id_usuario', $idUsuario)
            ->where('estado', 'activo')
            ->update(['estado' => 'cancelado']);

        $session->setFlashdata(
            'mensaje',
            $db->affectedRows() > 0
                ? 'La renovación quedó cancelada. Tu acceso continúa hasta la fecha de vencimiento.'
                : 'No hay una suscripción activa para cancelar.'
        );

        return redirect()->to(base_url('premium'));
    }

    private function sumarMesesCalendario(\DateTimeImmutable $fecha, int $meses): \DateTimeImmutable
    {
        $primerDiaMesObjetivo = $fecha->modify('first day of this month')->modify('+' . $meses . ' months');
        $dia = min((int) $fecha->format('d'), (int) $primerDiaMesObjetivo->format('t'));

        return $primerDiaMesObjetivo
            ->setDate((int) $primerDiaMesObjetivo->format('Y'), (int) $primerDiaMesObjetivo->format('m'), $dia)
            ->setTime((int) $fecha->format('H'), (int) $fecha->format('i'), (int) $fecha->format('s'));
    }
}
