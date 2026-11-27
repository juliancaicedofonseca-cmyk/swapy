USE swapy;

CREATE TABLE IF NOT EXISTS `intercambios` (
  `id_intercambio` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `id_solicitante` int(11) NOT NULL,
  `id_propietario` int(11) NOT NULL,
  `confirmado_solicitante` tinyint(1) NOT NULL DEFAULT 0,
  `confirmado_propietario` tinyint(1) NOT NULL DEFAULT 0,
  `direccion` varchar(255) NOT NULL,
  `descripcion_lugar` text NOT NULL,
  `descripcion_producto` text NOT NULL,
  `estado` varchar(30) NOT NULL DEFAULT 'pendiente',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_intercambio`),
  KEY `idx_intercambio_producto` (`id_producto`),
  KEY `idx_intercambio_solicitante` (`id_solicitante`),
  KEY `idx_intercambio_propietario` (`id_propietario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;