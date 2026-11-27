package com.swapy.swapy_java.repository;

import java.sql.Time;
import java.time.LocalDateTime;

/**
 * Projection de solo lectura sobre `intercambios` + JOIN a `productos` y
 * `usuario`, para mostrar en el panel el nombre real del producto y del
 * solicitante (antes se mostraba el correo, o quedaba en blanco).
 */
public interface SolicitudEntregaDetalle {
    Integer getIdIntercambio();
    Integer getIdProducto();
    Integer getIdSolicitante();
    Integer getIdPropietario();
    String getDireccionRecogida();
    String getDireccionEntrega();
    String getDescripcionLugar();
    String getDescripcionProducto();
    String getEstado();
    Long getFkIdEmpleado();
    String getEstadoEntrega();
    Time getHoraLimite();
    Integer getIntentosFallidos();
    LocalDateTime getCreadoEn();
    String getNombreProducto();
    String getNombreSolicitante();
    String getNombrePropietario();
}
