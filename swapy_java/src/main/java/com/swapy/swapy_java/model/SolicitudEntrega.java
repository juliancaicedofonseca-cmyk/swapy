package com.swapy.swapy_java.model;

import jakarta.persistence.*;

import java.time.LocalDateTime;
import java.time.LocalTime;

/**
 * Mapea la tabla `intercambios`, que es la misma tabla donde el flujo del
 * cliente (PHP, ConversacionController::solicitudEntrega) inserta cada vez
 * que solicita el envío de un trueque. Antes el panel de empleado leía de
 * las tablas legadas `intercambio` / `entrega`, que nunca se llenaban desde
 * el lado del cliente — por eso las solicitudes reales nunca aparecían aquí.
 *
 * Solo se mapean las columnas que el empleado necesita gestionar; el resto
 * de columnas de la fila (id_producto, id_solicitante, etc.) se leen aparte
 * mediante SolicitudEntregaRepository#listarConDetalle (con JOIN a
 * productos/usuario para traer nombre real del producto y del solicitante).
 */
@Entity
@Table(name = "intercambios")
public class SolicitudEntrega {

    public enum EstadoEntrega { Pendiente, Aceptada, En_ruta, Entregada, Fallida, Cancelada }

    @Id
    @Column(name = "id_intercambio")
    private Integer idIntercambio;

    @Column(name = "id_producto", insertable = false, updatable = false)
    private Integer idProducto;

    @Column(name = "id_solicitante", insertable = false, updatable = false)
    private Integer idSolicitante;

    @Column(name = "id_propietario", insertable = false, updatable = false)
    private Integer idPropietario;

    @Column(name = "direccion_recogida", length = 255)
    private String direccionRecogida;

    /** Columna `direccion` de la tabla = dirección de entrega. */
    @Column(name = "direccion", length = 255)
    private String direccionEntrega;

    @Column(name = "descripcion_lugar")
    private String descripcionLugar;

    @Column(name = "descripcion_producto")
    private String descripcionProducto;

    @Column(name = "fk_id_empleado")
    private Long fkIdEmpleado;

    @Enumerated(EnumType.STRING)
    @Column(name = "estado_entrega", length = 20)
    private EstadoEntrega estadoEntrega = EstadoEntrega.Pendiente;

    @Column(name = "hora_limite")
    private LocalTime horaLimite;

    @Column(name = "confirmacion_origen")
    private Boolean confirmacionOrigen = false;

    @Column(name = "confirmacion_destino")
    private Boolean confirmacionDestino = false;

    @Column(name = "intentos_fallidos")
    private Integer intentosFallidos = 0;

    @Column(name = "fecha_entrega")
    private LocalDateTime fechaEntrega;

    public Integer getIdIntercambio() { return idIntercambio; }
    public Integer getIdProducto() { return idProducto; }
    public Integer getIdSolicitante() { return idSolicitante; }
    public Integer getIdPropietario() { return idPropietario; }
    public String getDireccionRecogida() { return direccionRecogida; }
    public void setDireccionRecogida(String direccionRecogida) { this.direccionRecogida = direccionRecogida; }
    public String getDireccionEntrega() { return direccionEntrega; }
    public void setDireccionEntrega(String direccionEntrega) { this.direccionEntrega = direccionEntrega; }
    public String getDescripcionLugar() { return descripcionLugar; }
    public String getDescripcionProducto() { return descripcionProducto; }
    public Long getFkIdEmpleado() { return fkIdEmpleado; }
    public void setFkIdEmpleado(Long fkIdEmpleado) { this.fkIdEmpleado = fkIdEmpleado; }
    public EstadoEntrega getEstadoEntrega() { return estadoEntrega; }
    public void setEstadoEntrega(EstadoEntrega estadoEntrega) { this.estadoEntrega = estadoEntrega; }
    public LocalTime getHoraLimite() { return horaLimite; }
    public void setHoraLimite(LocalTime horaLimite) { this.horaLimite = horaLimite; }
    public Boolean getConfirmacionOrigen() { return confirmacionOrigen; }
    public void setConfirmacionOrigen(Boolean confirmacionOrigen) { this.confirmacionOrigen = confirmacionOrigen; }
    public Boolean getConfirmacionDestino() { return confirmacionDestino; }
    public void setConfirmacionDestino(Boolean confirmacionDestino) { this.confirmacionDestino = confirmacionDestino; }
    public Integer getIntentosFallidos() { return intentosFallidos; }
    public void setIntentosFallidos(Integer intentosFallidos) { this.intentosFallidos = intentosFallidos; }
    public LocalDateTime getFechaEntrega() { return fechaEntrega; }
    public void setFechaEntrega(LocalDateTime fechaEntrega) { this.fechaEntrega = fechaEntrega; }
}
