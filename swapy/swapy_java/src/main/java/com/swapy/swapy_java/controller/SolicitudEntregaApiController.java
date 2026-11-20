package com.swapy.swapy_java.controller;

import com.swapy.swapy_java.config.SesionEmpleadoInterceptor;
import com.swapy.swapy_java.model.SolicitudEntrega;
import com.swapy.swapy_java.service.SolicitudEntregaService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/empleado/solicitudes-entrega")
public class SolicitudEntregaApiController {

    private final SolicitudEntregaService service;

    public SolicitudEntregaApiController(SolicitudEntregaService service) {
        this.service = service;
    }

    private Long idEmpleado(HttpServletRequest request) {
        return (Long) request.getSession().getAttribute(SesionEmpleadoInterceptor.SESSION_KEY);
    }

    @PostMapping("/{id}/aceptar")
    public ResponseEntity<?> aceptar(@PathVariable Integer id, HttpServletRequest request) {
        try {
            SolicitudEntrega s = service.aceptar(id, idEmpleado(request));
            return ResponseEntity.ok(Map.of("ok", true, "estado", s.getEstadoEntrega()));
        } catch (RuntimeException ex) {
            return ResponseEntity.badRequest().body(Map.of("ok", false, "error", ex.getMessage()));
        }
    }

    @PostMapping("/{id}/rechazar")
    public ResponseEntity<?> rechazar(@PathVariable Integer id) {
        try {
            SolicitudEntrega s = service.rechazar(id);
            return ResponseEntity.ok(Map.of("ok", true, "estado", s.getEstadoEntrega()));
        } catch (RuntimeException ex) {
            return ResponseEntity.badRequest().body(Map.of("ok", false, "error", ex.getMessage()));
        }
    }

    @PostMapping("/{id}/en-ruta")
    public ResponseEntity<?> enRuta(@PathVariable Integer id, HttpServletRequest request) {
        try {
            SolicitudEntrega s = service.marcarEnRuta(id, idEmpleado(request));
            return ResponseEntity.ok(Map.of("ok", true, "estado", s.getEstadoEntrega()));
        } catch (RuntimeException ex) {
            return ResponseEntity.badRequest().body(Map.of("ok", false, "error", ex.getMessage()));
        }
    }

    @PostMapping("/{id}/entregada")
    public ResponseEntity<?> entregada(@PathVariable Integer id, HttpServletRequest request) {
        try {
            SolicitudEntrega s = service.marcarEntregada(id, idEmpleado(request));
            return ResponseEntity.ok(Map.of("ok", true, "estado", s.getEstadoEntrega()));
        } catch (RuntimeException ex) {
            return ResponseEntity.badRequest().body(Map.of("ok", false, "error", ex.getMessage()));
        }
    }

    @PostMapping("/{id}/intento-fallido")
    public ResponseEntity<?> intentoFallido(@PathVariable Integer id, HttpServletRequest request) {
        try {
            SolicitudEntrega s = service.marcarIntentoFallido(id, idEmpleado(request));
            return ResponseEntity.ok(Map.of("ok", true, "estado", s.getEstadoEntrega(), "intentos", s.getIntentosFallidos()));
        } catch (RuntimeException ex) {
            return ResponseEntity.badRequest().body(Map.of("ok", false, "error", ex.getMessage()));
        }
    }
}
