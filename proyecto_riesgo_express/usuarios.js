// ============================================================
// usuarios.js — Usuarios del dashboard (demo académica)
// ------------------------------------------------------------
// PROPÓSITO: directorio de usuarios permitidos por login.html.
// Las contraseñas se almacenan como hash SHA-256 en hexadecimal
// (nunca en texto plano) y se comparan contra el hash calculado
// en el navegador.
//
// Generar hash:  echo -n "tupassword" | sha256sum
//
// Advertencia: la contraseña en claro junto al hash es solo para
// conveniencia de la demo académica — NO replicar en producción.
//
// Documentado: 2026-09-18
// ============================================================
/**
 * Lista de usuarios registrados para el acceso al dashboard.
 *
 * @global
 * @type {Array<Object>}
 * @property {string} usuario - Nombre de usuario (login).
 * @property {string} nombre  - Nombre visible del usuario/área.
 * @property {string} rol     - Rol para permisos (Administrador, Cobranzas, Analista).
 * @property {string} hash    - SHA-256 hex de la contraseña.
 */
const USUARIOS = [
  {
    usuario: "admin",
    nombre: "Administrador",
    rol: "Administrador",
    hash: "08a97a6d14592c87f6f304d8943106f0a3e56804f54e5ef5aa38da55fff0ed0f" // riesgo2026
  },
  {
    usuario: "cobranzas",
    nombre: "Área de Cobranzas",
    rol: "Cobranzas",
    hash: "58e31696ae7c592bab1ee88e3af2ec0fbb8821aaafcf4e357d3b3dd653f21375" // cobranzas2026
  },
  {
    usuario: "analista",
    nombre: "Analista de Riesgo",
    rol: "Analista",
    hash: "600326bba6425e343574395782d5a0ff4e54328278e6acbe51fd91a7cc7a379b" // analista2026
  }
];
