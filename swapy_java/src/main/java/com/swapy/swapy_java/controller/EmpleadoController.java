package com.swapy.swapy_java.controller;

import com.swapy.swapy_java.config.SesionEmpleadoInterceptor;
import com.swapy.swapy_java.model.Empleado;
import com.swapy.swapy_java.repository.EmpleadoRepository;
import com.swapy.swapy_java.repository.PersonaRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.Optional;

@Controller
@RequestMapping("/empleado")
public class EmpleadoController {

    @Autowired
    private EmpleadoRepository empleadoRepository;

    @Autowired
    private PersonaRepository personaRepository;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    // 1. Muestra la vista del login (spempleados.html)
    @GetMapping("")
    public String index() {
        return "spempleados";
    }

    // 2. Procesa el Login (Complejidad reducida)
    @PostMapping("/login")
    public String login(@RequestParam("correo") String correo,
                        @RequestParam("password") String password,
                        HttpSession session,
                        RedirectAttributes redirectAttributes) {

        Optional<Empleado> empOpt = empleadoRepository.findByCorreo(correo);

        if (empOpt.isEmpty()) {
            redirectAttributes.addFlashAttribute("error", "El correo no existe en la tabla empleado.");
            return "redirect:/empleado";
        }

        Empleado emp = empOpt.get();

        // Validación delegada para bajar la complejidad ciclomática
        if (!validarPassword(password, emp.getContrasena())) {
            redirectAttributes.addFlashAttribute("error", "La contraseña es incorrecta.");
            return "redirect:/empleado";
        }

        String nombreCompleto = "Empleado";
        if (emp.getPersona() != null) {
            nombreCompleto = emp.getPersona().getNombreCompleto();
        }

        // Configuración de la sesión
        session.setAttribute("isLoggedIn", true);
        session.setAttribute(SesionEmpleadoInterceptor.SESSION_KEY, emp.getIdEmpleado());
        session.setAttribute("empleadoId", emp.getIdEmpleado());
        session.setAttribute("id_empleado", emp.getIdEmpleado());
        session.setAttribute("id_doc", emp.getId() != null ? emp.getId().getPkfkIdDoc() : null);
        session.setAttribute("correo", emp.getCorreo());
        session.setAttribute("nombre", nombreCompleto);
        session.setAttribute("rol", "Empleado");

        return "redirect:/empleado/panel";
    }

    // Método auxiliar privado para manejar la validación de hashes y contraseñas planas
    private boolean validarPassword(String password, String hashBD) {
        if (hashBD == null) {
            return false;
        }

        String hashNormalizado = hashBD;
        if (hashNormalizado.startsWith("$2y$")) {
            hashNormalizado = "$2a$" + hashNormalizado.substring(4);
        }

        if (hashNormalizado.startsWith("$2a$") || hashNormalizado.startsWith("$2b$")) {
            try {
                if (passwordEncoder.matches(password, hashNormalizado)) {
                    return true;
                }
            } catch (Exception ignored) {}
        }

        return password.equals(hashBD);
    }

    // 3. Logout
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/empleado";
    }
}