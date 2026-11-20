package com.swapy.swapy_java.controller;

import com.swapy.swapy_java.config.SesionEmpleadoInterceptor;
import com.swapy.swapy_java.model.Empleado;
import com.swapy.swapy_java.model.EmpleadoPerfil;
import com.swapy.swapy_java.repository.EmpleadoRepository;
import com.swapy.swapy_java.repository.SolicitudEntregaDetalle;
import com.swapy.swapy_java.repository.TipoDocumentoRepository;
import com.swapy.swapy_java.service.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@Controller
public class EmpleadoPanelController {

    private final EmpleadoRepository empleadoRepository;
    private final TipoDocumentoRepository tipoDocumentoRepository;
    private final PanelEmpleadoService panelEmpleadoService;
    private final IntercambioService intercambioService;
    private final SolicitudEntregaService solicitudEntregaService;
    private final DenunciaService denunciaService;
    private final PerfilService perfilService;
    private final EmpleadoGestionService empleadoGestionService;

    public EmpleadoPanelController(EmpleadoRepository empleadoRepository,
                                    TipoDocumentoRepository tipoDocumentoRepository,
                                    PanelEmpleadoService panelEmpleadoService,
                                    IntercambioService intercambioService,
                                    SolicitudEntregaService solicitudEntregaService,
                                    DenunciaService denunciaService,
                                    PerfilService perfilService,
                                    EmpleadoGestionService empleadoGestionService) {
        this.empleadoRepository = empleadoRepository;
        this.tipoDocumentoRepository = tipoDocumentoRepository;
        this.panelEmpleadoService = panelEmpleadoService;
        this.intercambioService = intercambioService;
        this.solicitudEntregaService = solicitudEntregaService;
        this.denunciaService = denunciaService;
        this.perfilService = perfilService;
        this.empleadoGestionService = empleadoGestionService;
    }

    @GetMapping("/empleado/panel")
    public String panel(HttpServletRequest request, Model model,
                         @RequestParam(required = false) String repEstado,
                         @RequestParam(required = false) Boolean repSoloMias,
                         @RequestParam(required = false) String repFechaInicio,
                         @RequestParam(required = false) String repFechaFin) {
        Long idEmpleado = (Long) request.getSession().getAttribute(SesionEmpleadoInterceptor.SESSION_KEY);
        Empleado empleado = empleadoRepository.findByIdEmpleado(idEmpleado)
                .orElseThrow(() -> new IllegalStateException("Empleado de la sesión ya no existe"));
        EmpleadoPerfil perfil = perfilService.obtenerOCrear(idEmpleado);

        model.addAttribute("empleado", empleado);
        model.addAttribute("perfil", perfil);
        model.addAttribute("stats", panelEmpleadoService.obtenerStats(idEmpleado));
        model.addAttribute("intercambios", solicitudEntregaService.listarTodas());
        model.addAttribute("solicitudesPendientes", solicitudEntregaService.listarPendientesSinAsignar());
        model.addAttribute("misEntregas", solicitudEntregaService.listarMisEntregas(idEmpleado));
        model.addAttribute("todasLasEntregas", solicitudEntregaService.listarTodas());
        model.addAttribute("denuncias", denunciaService.listarTodas());
        model.addAttribute("empleados", empleadoGestionService.listarTodos());
        model.addAttribute("tiposDocumento", tipoDocumentoRepository.findAll());

        // ---- Reporte filtrable ----
        boolean soloMias = Boolean.TRUE.equals(repSoloMias);
        Long fkEmpleadoFiltro = soloMias ? idEmpleado : null;
        List<SolicitudEntregaDetalle> reporte = solicitudEntregaService.listarParaReporte(
                repEstado, fkEmpleadoFiltro, repFechaInicio, repFechaFin);
        model.addAttribute("reporte", reporte);
        model.addAttribute("repEstado", repEstado == null ? "" : repEstado);
        model.addAttribute("repSoloMias", soloMias);
        model.addAttribute("repFechaInicio", repFechaInicio == null ? "" : repFechaInicio);
        model.addAttribute("repFechaFin", repFechaFin == null ? "" : repFechaFin);

        return "panel";
    }

    @GetMapping("/empleado/reportes/imprimir")
    public String imprimirReporte(HttpServletRequest request, Model model,
                                   @RequestParam(required = false) String repEstado,
                                   @RequestParam(required = false) Boolean repSoloMias,
                                   @RequestParam(required = false) String repFechaInicio,
                                   @RequestParam(required = false) String repFechaFin) {
        Long idEmpleado = (Long) request.getSession().getAttribute(SesionEmpleadoInterceptor.SESSION_KEY);
        boolean soloMias = Boolean.TRUE.equals(repSoloMias);
        Long fkEmpleadoFiltro = soloMias ? idEmpleado : null;
        List<SolicitudEntregaDetalle> reporte = solicitudEntregaService.listarParaReporte(
                repEstado, fkEmpleadoFiltro, repFechaInicio, repFechaFin);
        model.addAttribute("reporte", reporte);
        model.addAttribute("repEstado", repEstado == null ? "" : repEstado);
        model.addAttribute("repSoloMias", soloMias);
        model.addAttribute("repFechaInicio", repFechaInicio == null ? "" : repFechaInicio);
        model.addAttribute("repFechaFin", repFechaFin == null ? "" : repFechaFin);
        return "reporte_empleado_imprimir";
    }
}
