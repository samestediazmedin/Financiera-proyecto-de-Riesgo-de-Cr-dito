// ============================================================
// usuarios.js — Usuarios del dashboard (demo académica)
// Passwords almacenadas como SHA-256 hex (nunca en texto plano).
// Generar hash: echo -n "tupassword" | sha256sum
// ============================================================
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
