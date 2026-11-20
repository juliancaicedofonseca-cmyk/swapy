USE swapy;

CREATE TABLE IF NOT EXISTS `conversaciones` (
  `id_conversacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `id_iniciador` int(11) NOT NULL,
  `id_destinatario` int(11) NOT NULL,
  `ultimo_mensaje` varchar(255) DEFAULT NULL,
  `actualizado_en` datetime NOT NULL,
  PRIMARY KEY (`id_conversacion`),
  UNIQUE KEY `uq_conversacion_producto_usuario` (`id_producto`, `id_iniciador`, `id_destinatario`),
  KEY `idx_conversaciones_iniciador` (`id_iniciador`),
  KEY `idx_conversaciones_destinatario` (`id_destinatario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `mensajes_chat` (
  `id_mensaje_chat` int(11) NOT NULL AUTO_INCREMENT,
  `id_conversacion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL DEFAULT 0,
  `tipo` varchar(20) NOT NULL DEFAULT 'usuario',
  `contenido` text NOT NULL,
  `creado_en` datetime NOT NULL,
  PRIMARY KEY (`id_mensaje_chat`),
  KEY `idx_mensajes_chat_conversacion` (`id_conversacion`),
  CONSTRAINT `fk_mensajes_chat_conversacion` FOREIGN KEY (`id_conversacion`) REFERENCES `conversaciones` (`id_conversacion`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;