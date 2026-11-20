package com.swapy.swapy_java.service;

import com.swapy.swapy_java.model.SolicitudEntrega;
import com.swapy.swapy_java.repository.SolicitudEntregaDetalle;
import com.swapy.swapy_java.repository.SolicitudEntregaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;

@Service
public class SolicitudEntregaService {

    private final SolicitudEntregaRepository repository;

    public SolicitudEntregaService(SolicitudEntregaRepository repository) {
        this.repository = repository;
    }

    public List<SolicitudEntregaDetalle> listarTodas() {
        return repository.listarConDetalle();
    }

    public List<SolicitudEntregaDetalle> listarPendientesSinAsignar() {
        return repository.listarPendientesConDetalle();
    }

    public List<SolicitudEntregaDetalle> listarMisEntregas(Long idEmpleado) {
        return repository.listarMisEntregasConDetalle(idEmpleado);
    }

    public long contarPendientes() {
        return repository.countByEstadoEntrega(SolicitudEntrega.EstadoEntrega.Pendiente);
    }

    public long contarPorEstado(SolicitudEntrega.EstadoEntrega... estados) {
        return repository.countByEstadoEntregaIn(java.util.Arrays.asList(estados));
    }

    public long contarCreadosEsteMes() {
        return repository.countCreadosDesde(java.time.LocalDate.now().withDayOfMonth(1));
    }

    /**
     * Reporte filtrable para el empleado: por estado de entrega, por
     * empleado asignado (para "solo mis entregas") y por rango de fechas.
     * Cualquier parámetro en null/"" significa "sin filtrar por ese campo".
     */
    public List<SolicitudEntregaDetalle> listarParaReporte(String estado, Long fkEmpleado,
                                                             String fechaInicio, String fechaFin) {
        String est = (estado == null || estado.isBlank()) ? null : estado;
        String fi = (fechaInicio == null || fechaInicio.isBlank()) ? null : fechaInicio + " 00:00:00";
        String ff = (fechaFin == null || fechaFin.isBlank()) ? null : fechaFin + " 23:59:59";
        return repository.listarParaReporte(est, fkEmpleado, fi, ff);
    }

    /** El empleado toma la solicitud pendiente: Pendiente -> Aceptada. */
    @Transactional
    public SolicitudEntrega aceptar(Integer id, Long idEmpleado) {
        SolicitudEntrega s = obtener(id);
        if (s.getEstadoEntrega() != SolicitudEntrega.EstadoEntrega.Pendiente) {
            throw new IllegalStateException("La solicitud ya fue tomada por otro empleado.");
        }
        s.setFkIdEmpleado(idEmpleado);
        s.setEstadoEntrega(SolicitudEntrega.EstadoEntrega.Aceptada);
        return repository.save(s);
    }

    public SolicitudEntrega rechazar(Integer id) {
        SolicitudEntrega s = obtener(id);
        s.setEstadoEntrega(SolicitudEntrega.EstadoEntrega.Cancelada);
        return repository.save(s);
    }

    /** Aceptada -> En_ruta (el empleado recogió el producto y va en camino). */
    @Transactional
    public SolicitudEntrega marcarEnRuta(Integer id, Long idEmpleado) {
        SolicitudEntrega s = deEmpleado(id, idEmpleado);
        s.setConfirmacionOrigen(true);
        s.setEstadoEntrega(SolicitudEntrega.EstadoEntrega.En_ruta);
        return repository.save(s);
    }

    /** En_ruta -> Entregada. */
    @Transactional
    public SolicitudEntrega marcarEntregada(Integer id, Long idEmpleado) {
        SolicitudEntrega s = deEmpleado(id, idEmpleado);
        s.setConfirmacionDestino(true);
        s.setEstadoEntrega(SolicitudEntrega.EstadoEntrega.Entregada);
        s.setFechaEntrega(LocalDateTime.now());
        return repository.save(s);
    }

    /** Cliente no estaba en el punto de entrega: se reagenda automáticamente (hasta 3 intentos). */
    @Transactional
    public SolicitudEntrega marcarIntentoFallido(Integer id, Long idEmpleado) {
        SolicitudEntrega s = deEmpleado(id, idEmpleado);
        int intentos = (s.getIntentosFallidos() == null ? 0 : s.getIntentosFallidos()) + 1;
        s.setIntentosFallidos(intentos);
        if (intentos >= 3) {
            s.setEstadoEntrega(SolicitudEntrega.EstadoEntrega.Fallida);
        }
        return repository.save(s);
    }

    public SolicitudEntrega obtener(Integer id) {
        return repository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Solicitud no encontrada: " + id));
    }

    private SolicitudEntrega deEmpleado(Integer id, Long idEmpleado) {
        SolicitudEntrega s = obtener(id);
        if (s.getFkIdEmpleado() == null || !s.getFkIdEmpleado().equals(idEmpleado)) {
            throw new IllegalStateException("Esta solicitud no está asignada a este empleado.");
        }
        return s;
    }
}
