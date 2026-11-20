package com.swapy.swapy_java.service;

import com.swapy.swapy_java.model.SolicitudEntrega;
import com.swapy.swapy_java.model.UsuarioDenuncia;
import org.springframework.stereotype.Service;

@Service
public class PanelEmpleadoService {

    private final IntercambioService intercambioService;
    private final SolicitudEntregaService solicitudEntregaService;
    private final DenunciaService denunciaService;

    public PanelEmpleadoService(IntercambioService intercambioService,
                                 SolicitudEntregaService solicitudEntregaService,
                                 DenunciaService denunciaService) {
        this.intercambioService = intercambioService;
        this.solicitudEntregaService = solicitudEntregaService;
        this.denunciaService = denunciaService;
    }

    public DashboardStats obtenerStats(Long idEmpleado) {
        DashboardStats stats = new DashboardStats();
        stats.intercambiosCreadosEsteMes = solicitudEntregaService.contarCreadosEsteMes();
        stats.intercambiosEntregados = solicitudEntregaService.contarPorEstado(SolicitudEntrega.EstadoEntrega.Entregada);
        stats.intercambiosEnProceso = solicitudEntregaService.contarPorEstado(
                SolicitudEntrega.EstadoEntrega.Aceptada, SolicitudEntrega.EstadoEntrega.En_ruta);
        stats.denunciasActivas = denunciaService.contarPorEstado(UsuarioDenuncia.Estado.pendiente)
                + denunciaService.contarPorEstado(UsuarioDenuncia.Estado.en_revision);
        stats.denunciasResueltas = denunciaService.contarPorEstado(UsuarioDenuncia.Estado.resuelta);
        stats.entregasPendientesHoy = solicitudEntregaService.listarMisEntregas(idEmpleado).stream()
                .filter(e -> "Aceptada".equals(e.getEstadoEntrega()) || "En_ruta".equals(e.getEstadoEntrega()))
                .count();
        return stats;
    }

    public static class DashboardStats {
        public long intercambiosCreadosEsteMes;
        public long intercambiosEntregados;
        public long intercambiosEnProceso;
        public long denunciasActivas;
        public long denunciasResueltas;
        public long entregasPendientesHoy;
    }
}
