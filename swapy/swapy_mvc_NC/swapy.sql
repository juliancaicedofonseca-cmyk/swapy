-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 16-06-2026 a las 02:26:43
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

drop database if exists swapy;
create database swapy;
use swapy;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `swapy`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administrador`
--

CREATE TABLE `administrador` (
  `pkfk_id_doc` int(11) NOT NULL,
  `id_admin` bigint(20) NOT NULL,
  `correo` varchar(30) NOT NULL,
  `contraseña` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `n_categoria` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `n_categoria`) VALUES
(1, 'Tecnología'),
(2, 'Hogar'),
(3, 'Juegos'),
(4, 'Moda'),
(5, 'Deportes'),
(6, 'Mascotas'),
(7, 'Automóvil'),
(8, 'Otros');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chats`
--

CREATE TABLE `chats` (
  `id_chat` int(11) NOT NULL,
  `fk_id_doc` int(11) NOT NULL,
  `fk_id_usuario` bigint(20) NOT NULL,
  `estado_chat` tinytext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `denuncias`
--

CREATE TABLE `denuncias` (
  `id_denuncia` int(11) NOT NULL,
  `correo_denunciante` varchar(255) NOT NULL,
  `correo_denunciado` varchar(255) NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `descripcion` text NOT NULL,
  `estado` varchar(50) DEFAULT 'Pendiente',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `faqs`
--

CREATE TABLE `faqs` (
  `id_faq` int(11) NOT NULL,
  `pregunta` text NOT NULL,
  `respuesta` text NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `orden` int(11) DEFAULT 1,
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagenes`
--

CREATE TABLE `imagenes` (
  `id_img` int(11) NOT NULL,
  `img_producto` blob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `impulsar`
--

CREATE TABLE `impulsar` (
  `cod_impulso` int(11) NOT NULL,
  `pago` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `intercambio`
--

CREATE TABLE `intercambio` (
  `id_intercambio` int(11) NOT NULL,
  `fk_id_chat` int(11) NOT NULL,
  `n_producto_publicado` varchar(35) DEFAULT NULL,
  `n_producto_ofertado` varchar(35) DEFAULT NULL,
  `fecha_cierre` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes`
--

CREATE TABLE `mensajes` (
  `id_mensaje` int(11) NOT NULL,
  `fk_id_doc` int(11) NOT NULL,
  `fk_id_usuario` bigint(20) NOT NULL,
  `fk_id_chat` int(11) NOT NULL,
  `contenido_mensaje` varchar(45) DEFAULT NULL,
  `fecha_hora_envio` datetime DEFAULT NULL,
  `estado_mensaje` tinytext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `fkpk_id_doc` int(11) NOT NULL,
  `documento` bigint(20) NOT NULL,
  `primer_nombre` varchar(15) NOT NULL,
  `segundo_nombre` varchar(15) DEFAULT NULL,
  `primer_apellido` varchar(12) NOT NULL,
  `segundo_apellido` varchar(12) DEFAULT NULL,
  `fk_id_recuperar_cuenta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `problemas_frecuentes`
--

CREATE TABLE `problemas_frecuentes` (
  `id_problema` int(11) NOT NULL,
  `titulo_problema` varchar(45) DEFAULT NULL,
  `solucion` varchar(45) DEFAULT NULL,
  `fk_id_doc` int(11) NOT NULL,
  `fk_id_admin` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(20) NOT NULL,
  `valor_estimado` int(11) DEFAULT NULL,
  `desc_producto` varchar(45) DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `fk_id_categoria` int(11) NOT NULL,
  `fk_cod_impulso` int(11) DEFAULT NULL,
  `fk_id_doc` int(11) NOT NULL,
  `fk_id_usuario` bigint(20) NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'Activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre_producto`, `valor_estimado`, `desc_producto`, `imagen`, `fk_id_categoria`, `fk_cod_impulso`, `fk_id_doc`, `fk_id_usuario`) VALUES
(4, 'estructura', 199000, 'pah', 'productos/1781564279_85d736798bfb9d929133.png', 5, NULL, 1, 9),
(5, 'mapa mental', 1000, 'informacion', 'productos/1781564566_505c7dcdec272b22a22e.png', 8, NULL, 1, 9);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_has_imagenes`
--

CREATE TABLE `productos_has_imagenes` (
  `pkfk_id_producto` int(11) NOT NULL,
  `pkfk_id_img` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `publicaciones`
--

CREATE TABLE `publicaciones` (
  `id` int(10) UNSIGNED NOT NULL,
  `usuario_id` int(10) UNSIGNED NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `valor_minimo` decimal(12,2) DEFAULT 0.00,
  `descripcion_deseado` text DEFAULT NULL,
  `categoria_deseada` varchar(100) DEFAULT NULL,
  `imagen` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recuperar_cuenta`
--

CREATE TABLE `recuperar_cuenta` (
  `id_recuperar_cuenta` int(11) NOT NULL,
  `codigo_verif` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_perfil`
--

CREATE TABLE `reporte_perfil` (
  `id_reporte` int(11) NOT NULL,
  `motivo` varchar(45) DEFAULT NULL,
  `fk_id_doc` int(11) NOT NULL,
  `fk_id_admin` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `t_doc`
--

CREATE TABLE `t_doc` (
  `id_doc` int(11) NOT NULL,
  `tipo_doc` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `t_doc`
--

INSERT INTO `t_doc` (`id_doc`, `tipo_doc`) VALUES
(1, 'CC'),
(2, 'TI'),
(3, 'CE');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `pkfk_id_doc` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(30) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `rol` varchar(50) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Activo',
  `codigo_verificacion` varchar(10) DEFAULT NULL,
  `otp_expira` datetime DEFAULT NULL,
  `verificado` varchar(5) DEFAULT NULL,
  `premium` tinyint(1) DEFAULT 0,
  `descripcion` text DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `categorias` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`pkfk_id_doc`, `id_usuario`, `username`, `telefono`, `correo`, `contraseña`, `rol`, `estado`, `codigo_verificacion`, `otp_expira`, `verificado`, `premium`, `descripcion`, `foto`, `categorias`) VALUES
(1, 1, NULL, NULL, 'admin@gmail.com', '$2y$10$vMInTOJFZmlwHcooOQL5fej4VxRzp1FFW4iyygjOyklum1XSoVbJa', 'Administrador', 'Activo', '971021', NULL, 'NO', 0, NULL, NULL, NULL),
(1, 8, NULL, NULL, 'empleado@gmail.com', '1234', 'Empleado', 'Activo', '674716', NULL, 'NO', 0, NULL, NULL, NULL),
(1, 9, NULL, NULL, 'cliente@gmail.com', '12345', 'Cliente', 'Activo', '975109', NULL, 'NO', 0, NULL, NULL, NULL),
(1, 10, 'juan pablo', '3214335346', 'leo@gmail.com', '$2y$10$NHT2czNEMp.WJW9N1QmXY.7.5uWsfjUx8LhkjpQtiypmJkT1Fs9DO', 'Cliente', 'Activo', NULL, NULL, 'SI', 0, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_denuncias`
--

CREATE TABLE `usuario_denuncias` (
  `id_denuncia` int(11) NOT NULL,
  `id_usuario_denunciante` int(11) NOT NULL,
  `id_usuario_denunciado` int(11) DEFAULT NULL,
  `tipo_denuncia` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  `respuesta` longtext DEFAULT NULL,
  `estado` enum('pendiente','en_revision','resuelta','rechazada') DEFAULT 'pendiente',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_respuesta` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_preguntas`
--

CREATE TABLE `usuario_preguntas` (
  `id_pregunta` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `pregunta` longtext NOT NULL,
  `respuesta` longtext DEFAULT NULL,
  `estado` enum('pendiente','respondida','cerrada') DEFAULT 'pendiente',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_respuesta` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_premium`
--

CREATE TABLE `usuario_premium` (
  `id_premium` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_inicio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_fin` timestamp NULL DEFAULT NULL,
  `plan` varchar(50) DEFAULT 'basico',
  `estado` enum('activo','cancelado','vencido') DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `intercambios`
--

CREATE TABLE `intercambios` (
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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversaciones`
--

CREATE TABLE `conversaciones` (
  `id_conversacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `id_iniciador` int(11) NOT NULL,
  `id_destinatario` int(11) NOT NULL,
  `ultimo_mensaje` varchar(255) DEFAULT NULL,
  `actualizado_en` datetime NOT NULL,
  PRIMARY KEY (`id_conversacion`),
  UNIQUE KEY `uq_conversacion_producto_usuario` (`id_producto`,`id_iniciador`,`id_destinatario`),
  KEY `idx_conversaciones_iniciador` (`id_iniciador`),
  KEY `idx_conversaciones_destinatario` (`id_destinatario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes_chat`
--

CREATE TABLE `mensajes_chat` (
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

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administrador`
--
ALTER TABLE `administrador`
  ADD PRIMARY KEY (`pkfk_id_doc`,`id_admin`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id_chat`);

--
-- Indices de la tabla `denuncias`
--
ALTER TABLE `denuncias`
  ADD PRIMARY KEY (`id_denuncia`);

--
-- Indices de la tabla `faqs`
--
ALTER TABLE `faqs`
  ADD PRIMARY KEY (`id_faq`);

--
-- Indices de la tabla `imagenes`
--
ALTER TABLE `imagenes`
  ADD PRIMARY KEY (`id_img`);

--
-- Indices de la tabla `impulsar`
--
ALTER TABLE `impulsar`
  ADD PRIMARY KEY (`cod_impulso`);

--
-- Indices de la tabla `intercambio`
--
ALTER TABLE `intercambio`
  ADD PRIMARY KEY (`id_intercambio`),
  ADD KEY `fk_intercambio_chats` (`fk_id_chat`);

--
-- Indices de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD PRIMARY KEY (`id_mensaje`),
  ADD KEY `fk_mensajes_chats` (`fk_id_chat`);

--
-- Indices de la tabla `persona`
--
ALTER TABLE `persona`
  ADD PRIMARY KEY (`fkpk_id_doc`,`documento`),
  ADD KEY `fk_persona_recuperar` (`fk_id_recuperar_cuenta`);

--
-- Indices de la tabla `problemas_frecuentes`
--
ALTER TABLE `problemas_frecuentes`
  ADD PRIMARY KEY (`id_problema`),
  ADD KEY `fk_problemas_admin` (`fk_id_doc`,`fk_id_admin`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `fk_productos_categoria` (`fk_id_categoria`),
  ADD KEY `fk_productos_impulso` (`fk_cod_impulso`);

--
-- Indices de la tabla `productos_has_imagenes`
--
ALTER TABLE `productos_has_imagenes`
  ADD PRIMARY KEY (`pkfk_id_producto`,`pkfk_id_img`),
  ADD KEY `fk_phi_img` (`pkfk_id_img`);

--
-- Indices de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_usuario` (`usuario_id`);

--
-- Indices de la tabla `recuperar_cuenta`
--
ALTER TABLE `recuperar_cuenta`
  ADD PRIMARY KEY (`id_recuperar_cuenta`);

--
-- Indices de la tabla `reporte_perfil`
--
ALTER TABLE `reporte_perfil`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `fk_reporte_admin` (`fk_id_doc`,`fk_id_admin`);

--
-- Indices de la tabla `t_doc`
--
ALTER TABLE `t_doc`
  ADD PRIMARY KEY (`id_doc`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`);

--
-- Indices de la tabla `usuario_denuncias`
--
ALTER TABLE `usuario_denuncias`
  ADD PRIMARY KEY (`id_denuncia`),
  ADD KEY `idx_usuario_denuncias_denunciante` (`id_usuario_denunciante`),
  ADD KEY `idx_usuario_denuncias_denunciado` (`id_usuario_denunciado`),
  ADD KEY `idx_usuario_denuncias_estado` (`estado`);

--
-- Indices de la tabla `usuario_preguntas`
--
ALTER TABLE `usuario_preguntas`
  ADD PRIMARY KEY (`id_pregunta`),
  ADD KEY `idx_usuario_preguntas_usuario` (`id_usuario`),
  ADD KEY `idx_usuario_preguntas_estado` (`estado`);

--
-- Indices de la tabla `usuario_premium`
--
ALTER TABLE `usuario_premium`
  ADD PRIMARY KEY (`id_premium`),
  ADD UNIQUE KEY `id_usuario` (`id_usuario`),
  ADD KEY `idx_usuario_premium_usuario` (`id_usuario`),
  ADD KEY `idx_usuario_premium_estado` (`estado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `denuncias`
--
ALTER TABLE `denuncias`
  MODIFY `id_denuncia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `faqs`
--
ALTER TABLE `faqs`
  MODIFY `id_faq` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `usuario_denuncias`
--
ALTER TABLE `usuario_denuncias`
  MODIFY `id_denuncia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario_preguntas`
--
ALTER TABLE `usuario_preguntas`
  MODIFY `id_pregunta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario_premium`
--
ALTER TABLE `usuario_premium`
  MODIFY `id_premium` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `administrador`
--
ALTER TABLE `administrador`
  ADD CONSTRAINT `fk_admin_persona` FOREIGN KEY (`pkfk_id_doc`,`id_admin`) REFERENCES `persona` (`fkpk_id_doc`, `documento`);

--
-- Filtros para la tabla `intercambio`
--
ALTER TABLE `intercambio`
  ADD CONSTRAINT `fk_intercambio_chats` FOREIGN KEY (`fk_id_chat`) REFERENCES `chats` (`id_chat`);

--
-- Filtros para la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD CONSTRAINT `fk_mensajes_chats` FOREIGN KEY (`fk_id_chat`) REFERENCES `chats` (`id_chat`);

--
-- Filtros para la tabla `persona`
--
ALTER TABLE `persona`
  ADD CONSTRAINT `fk_persona_recuperar` FOREIGN KEY (`fk_id_recuperar_cuenta`) REFERENCES `recuperar_cuenta` (`id_recuperar_cuenta`),
  ADD CONSTRAINT `fk_persona_tipoDoc` FOREIGN KEY (`fkpk_id_doc`) REFERENCES `t_doc` (`id_doc`);

--
-- Filtros para la tabla `problemas_frecuentes`
--
ALTER TABLE `problemas_frecuentes`
  ADD CONSTRAINT `fk_problemas_admin` FOREIGN KEY (`fk_id_doc`,`fk_id_admin`) REFERENCES `administrador` (`pkfk_id_doc`, `id_admin`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `fk_productos_categoria` FOREIGN KEY (`fk_id_categoria`) REFERENCES `categorias` (`id_categoria`);

--
-- Filtros para la tabla `productos_has_imagenes`
--
ALTER TABLE `productos_has_imagenes`
  ADD CONSTRAINT `fk_phi_img` FOREIGN KEY (`pkfk_id_img`) REFERENCES `imagenes` (`id_img`),
  ADD CONSTRAINT `fk_phi_productos` FOREIGN KEY (`pkfk_id_producto`) REFERENCES `productos` (`id_producto`);

--
-- Filtros para la tabla `reporte_perfil`
--
ALTER TABLE `reporte_perfil`
  ADD CONSTRAINT `fk_reporte_admin` FOREIGN KEY (`fk_id_doc`,`fk_id_admin`) REFERENCES `administrador` (`pkfk_id_doc`, `id_admin`);

--
-- Filtros para la tabla `usuario_denuncias`
--
ALTER TABLE `usuario_denuncias`
  ADD CONSTRAINT `usuario_denuncias_ibfk_1` FOREIGN KEY (`id_usuario_denunciante`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_denuncias_ibfk_2` FOREIGN KEY (`id_usuario_denunciado`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `usuario_preguntas`
--
ALTER TABLE `usuario_preguntas`
  ADD CONSTRAINT `usuario_preguntas_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `usuario_premium`
--
ALTER TABLE `usuario_premium`
  ADD CONSTRAINT `usuario_premium_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
