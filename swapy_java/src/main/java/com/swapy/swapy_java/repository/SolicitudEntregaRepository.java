package com.swapy.swapy_java.repository;

import com.swapy.swapy_java.model.SolicitudEntrega;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface SolicitudEntregaRepository extends JpaRepository<SolicitudEntrega, Integer> {

    long countByEstadoEntrega(SolicitudEntrega.EstadoEntrega estadoEntrega);

    long countByEstadoEntregaIn(java.util.List<SolicitudEntrega.EstadoEntrega> estados);

    @Query(value = "SELECT COUNT(*) FROM intercambios WHERE creado_en >= :desde", nativeQuery = true)
    long countCreadosDesde(@Param("desde") java.time.LocalDate desde);

    String DETALLE_SELECT =
            "SELECT i.id_intercambio AS idIntercambio, " +
            "i.id_producto AS idProducto, " +
            "i.id_solicitante AS idSolicitante, " +
            "i.id_propietario AS idPropietario, " +
            "i.direccion_recogida AS direccionRecogida, " +
            "i.direccion AS direccionEntrega, " +
            "i.descripcion_lugar AS descripcionLugar, " +
            "i.descripcion_producto AS descripcionProducto, " +
            "i.estado AS estado, " +
            "i.fk_id_empleado AS fkIdEmpleado, " +
            "i.estado_entrega AS estadoEntrega, " +
            "i.hora_limite AS horaLimite, " +
            "i.intentos_fallidos AS intentosFallidos, " +
            "i.creado_en AS creadoEn, " +
            "p.nombre_producto AS nombreProducto, " +
            "COALESCE(NULLIF(us.username,''), us.correo) AS nombreSolicitante, " +
            "COALESCE(NULLIF(up.username,''), up.correo) AS nombrePropietario " +
            "FROM intercambios i " +
            "LEFT JOIN productos p ON p.id_producto = i.id_producto " +
            "LEFT JOIN usuario us ON us.id_usuario = i.id_solicitante " +
            "LEFT JOIN usuario up ON up.id_usuario = i.id_propietario ";

    @Query(value = DETALLE_SELECT + "ORDER BY i.id_intercambio DESC", nativeQuery = true)
    List<SolicitudEntregaDetalle> listarConDetalle();

    @Query(value = DETALLE_SELECT + "WHERE i.estado_entrega = 'Pendiente' ORDER BY i.id_intercambio DESC", nativeQuery = true)
    List<SolicitudEntregaDetalle> listarPendientesConDetalle();

    @Query(value = DETALLE_SELECT + "WHERE i.fk_id_empleado = :idEmpleado ORDER BY i.id_intercambio DESC", nativeQuery = true)
    List<SolicitudEntregaDetalle> listarMisEntregasConDetalle(@Param("idEmpleado") Long idEmpleado);

    @Query(value = DETALLE_SELECT +
            "WHERE (:estado IS NULL OR i.estado_entrega = :estado) " +
            "AND (:fkEmpleado IS NULL OR i.fk_id_empleado = :fkEmpleado) " +
            "AND (:fechaInicio IS NULL OR i.creado_en >= :fechaInicio) " +
            "AND (:fechaFin IS NULL OR i.creado_en <= :fechaFin) " +
            "ORDER BY i.id_intercambio DESC", nativeQuery = true)
    List<SolicitudEntregaDetalle> listarParaReporte(@Param("estado") String estado,
                                                      @Param("fkEmpleado") Long fkEmpleado,
                                                      @Param("fechaInicio") String fechaInicio,
                                                      @Param("fechaFin") String fechaFin);
}
