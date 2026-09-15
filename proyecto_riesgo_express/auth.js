// ============================================================
// auth.js — Guardián de sesión + utilidades de logout
// Incluir PRIMERO en toda página protegida (index*.html).
// La sesión vive en sessionStorage (se cierra con la pestaña).
// ============================================================
(function () {
  const KEY = 'sesionRiesgo';
  function leerSesion() {
    try { return JSON.parse(sessionStorage.getItem(KEY) || 'null'); }
    catch { return null; }
  }
  // ---- Guard: si no hay sesión válida → login ----
  const sesion = leerSesion();
  if (!sesion || !sesion.usuario) {
    location.replace('login.html');
  }
  // ---- Poblar chip de usuario + botón salir (si existen) ----
  document.addEventListener('DOMContentLoaded', function () {
    const chip = document.getElementById('user-chip');
    if (chip && sesion) {
      chip.innerHTML =
        '<span class="hidden sm:inline text-xs text-slate-400">' + sesion.nombre + '</span>' +
        '<span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">' + sesion.rol + '</span>';
      chip.classList.remove('hidden');
    }
  });
  // ---- Logout global ----
  window.logout = function () {
    sessionStorage.removeItem(KEY);
    location.replace('login.html');
  };
})();
