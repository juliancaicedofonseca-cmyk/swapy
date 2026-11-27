<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Premium | Swapy</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { color-scheme: dark; --bg:#10100f; --card:#1b1a18; --line:#38352f; --text:#f5f1e9; --muted:#b3ada2; --gold:#f3bd58; }
        * { box-sizing:border-box; }
        body { margin:0; min-height:100vh; padding:32px 18px; background:radial-gradient(ellipse at top,#302719 0,var(--bg) 55%); color:var(--text); font:16px 'DM Sans',sans-serif; }
        main { width:min(860px,100%); margin:0 auto; }
        a { color:var(--gold); text-decoration:none; }
        .back { display:inline-block; margin-bottom:22px; }
        h1,h2 { font-family:Syne,sans-serif; }
        h1 { margin:0 0 8px; font-size:clamp(30px,5vw,44px); }
        h1 span { color:var(--gold); }
        .lead,.muted { color:var(--muted); }
        .card { margin-top:22px; padding:24px; border:1px solid var(--line); border-radius:18px; background:rgba(27,26,24,.94); box-shadow:0 18px 50px #0004; }
        .status { display:inline-block; padding:6px 11px; border-radius:999px; color:#17130c; background:var(--gold); font-size:13px; font-weight:700; text-transform:capitalize; }
        .details { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin:22px 0; }
        .detail { padding:16px; border:1px solid var(--line); border-radius:12px; }
        .detail small { display:block; margin-bottom:6px; color:var(--muted); }
        .detail strong { font-size:18px; }
        .notice { padding:13px 16px; border:1px solid #76603b; border-radius:12px; color:#f8d797; background:#3a2e1c; }
        .actions { display:flex; flex-wrap:wrap; gap:12px; align-items:center; }
        button { padding:11px 16px; border:0; border-radius:10px; color:#17130c; background:var(--gold); font-weight:700; cursor:pointer; }
        .payment { padding:14px 0; border-bottom:1px solid var(--line); }
        .payment:last-child { border-bottom:0; }
        .payment-top { display:flex; flex-wrap:wrap; justify-content:space-between; gap:8px; }
        .plans { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; }
        .plan { display:flex; flex-direction:column; padding:18px; border:1px solid var(--line); border-radius:14px; background:#22201d; }
        .plan h3 { margin:0 0 8px; font:700 20px Syne,sans-serif; }
        .price { margin:4px 0 12px; color:var(--gold); font:800 25px Syne,sans-serif; }
        .plan p { flex:1; color:var(--muted); }
        .plan form { margin-top:12px; }
        .simulated { color:#f8d797; font-size:13px; }
        @media(max-width:520px) { .card { padding:18px; } }
    </style>
</head>
<body>
<main>
    <a class="back" href="<?= base_url('perfil') ?>">← Volver a mi perfil</a>
    <h1>Mi <span>Premium</span></h1>
    <p class="lead">Consulta el estado de tu suscripción y los pagos registrados en tu cuenta.</p>

    <?php if (!empty($mensaje)): ?>
        <p class="notice" role="status"><?= esc($mensaje) ?></p>
    <?php endif; ?>

    <section class="card" aria-labelledby="resumen-titulo">
        <h2 id="resumen-titulo">Resumen</h2>
        <?php if ($vigente && $suscripcion): ?>
            <span class="status"><?= esc($suscripcion['estado']) ?></span>
            <div class="details">
                <div class="detail"><small>Plan</small><strong><?= esc($suscripcion['plan'] ?: 'Sin especificar') ?></strong></div>
                <div class="detail"><small>Fecha de inicio</small><strong><?= !empty($suscripcion['fecha_inicio']) ? esc(date('d/m/Y', strtotime($suscripcion['fecha_inicio']))) : '—' ?></strong></div>
                <div class="detail"><small>Vencimiento</small><strong><?= !empty($suscripcion['fecha_fin']) ? esc(date('d/m/Y', strtotime($suscripcion['fecha_fin']))) : 'Sin vencimiento' ?></strong></div>
            </div>
            <?php if (($suscripcion['estado'] ?? '') === 'cancelado'): ?>
                <p class="notice">La renovación está cancelada. Tu acceso sigue disponible hasta el vencimiento.</p>
            <?php else: ?>
                <p>Tu plan Premium está activo.</p>
                <form class="actions" action="<?= base_url('premium/cancelar') ?>" method="post" onsubmit="return confirm('¿Deseas cancelar la renovación de tu suscripción?');">
                    <?= csrf_field() ?>
                    <button type="submit">Cancelar suscripción</button>
                    <span class="muted">Conservarás el acceso hasta la fecha de vencimiento.</span>
                </form>
            <?php endif; ?>
        <?php else: ?>
            <p>Aún no tienes una suscripción Premium vigente.</p>
            <?php if ($suscripcion): ?>
                <p class="muted">Último estado registrado: <?= esc($suscripcion['estado']) ?>.</p>
            <?php endif; ?>
            <p class="muted">Si ya realizaste un pago, contacta al equipo de Swapy para revisar el registro.</p>
        <?php endif; ?>
    </section>

    <section class="card" aria-labelledby="suscripcion-titulo">
        <h2 id="suscripcion-titulo"><?= $vigente ? 'Renovar tu suscripción' : 'Activa tu suscripción Premium' ?></h2>
        <p class="muted">Elige la duración. Todas las opciones incluyen prioridad VIP para tus productos en el catálogo.</p>
        <div class="plans">
            <?php foreach ($duraciones as $meses => $opcion): ?>
                <article class="plan">
                    <h3><?= esc($opcion['nombre']) ?></h3>
                    <div class="price">$<?= esc(number_format($opcion['precio'], 0, ',', '.')) ?> <small>COP</small></div>
                    <p>Tu producto aparece antes que los productos de clientes sin VIP.</p>
                    <form action="<?= base_url('premium/comprar') ?>" method="post">
                        <?= csrf_field() ?>
                        <input type="hidden" name="meses" value="<?= esc((string) $meses) ?>">
                        <button type="submit">Suscribirme ahora</button>
                    </form>
                </article>
            <?php endforeach; ?>
        </div>
        <p class="simulated">Pago procesado por Mercado Pago (modo de prueba). Tu suscripción se activa cuando el pago es aprobado.</p>
    </section>

    <section class="card" aria-labelledby="pagos-titulo">
        <h2 id="pagos-titulo">Panel de pagos</h2>
        <p class="muted">Historial de compras y renovaciones de esta cuenta.</p>
        <?php if (!empty($pagos)): ?>
            <?php foreach ($pagos as $pago): ?>
                <article class="payment">
                    <div class="payment-top">
                        <strong><?= esc(ucfirst($pago['plan'])) ?> · $<?= esc(number_format((float) $pago['monto'], 0, ',', '.')) ?></strong>
                        <span class="muted"><?= esc(date('d/m/Y H:i', strtotime($pago['creado_en']))) ?></span>
                    </div>
                    <small class="muted">Referencia: <?= esc($pago['referencia']) ?></small>
                </article>
            <?php endforeach; ?>
        <?php else: ?>
            <p class="muted">Aún no hay pagos exitosos registrados.</p>
        <?php endif; ?>
    </section>
</main>
</body>
</html>
