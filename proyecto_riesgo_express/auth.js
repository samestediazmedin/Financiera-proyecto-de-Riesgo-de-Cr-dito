// ============================================================
// auth.js — Guardián de sesión + utilidades de logout
// ------------------------------------------------------------
// PROPÓSITO: proteger las páginas del dashboard (index.html,
// index.mejorado.html) redirigiendo a login.html si no hay una
// sesión válida. Incluir PRIMERO en toda página protegida.
//
// Estrategia de sesión (en orden de preferencia):
//   1) sessionStorage bajo la clave 'sesionRiesgo' (JSON).
//   2) Fallback: token en URL (#s=base64) para navegadores que
//      bloquean el almacenamiento; se migra a storage si es posible.
//
// Expone globalmente:
//   window.__sesion — objeto de sesión {usuario, nombre, rol, ts}
//   window.logout() — cierra sesión y redirige al login
//
// Documentado: 2026-09-18
// ============================================================
(function () {
  /** Clave de sessionStorage donde persiste la sesión del usuario. */
  const KEY = 'sesionRiesgo';

  /**
   * Parsea JSON de forma segura.
   * @param {string} raw - Texto JSON candidato.
   * @returns {Object|null} Objeto parseado o null si el JSON es inválido.
   */
  function parsear(raw) { try { return JSON.parse(raw); } catch (e) { return null; } }

  // 1) Intentar sessionStorage
  var sesion = null;
  try { sesion = parsear(sessionStorage.getItem(KEY)); }
  catch (e) { console.warn('[auth] sessionStorage bloqueado:', e && e.message); }

  // 2) Fallback: token en URL (#s=...) — lo migra a storage si puede
  if (!sesion || !sesion.usuario) {
    var m = (location.hash || '').match(/^#s=(.+)$/);
    if (m) {
      try {
        var dec = decodeURIComponent(escape(atob(decodeURIComponent(m[1]))));
        sesion = parsear(dec);
        if (sesion && sesion.usuario) {
          try { sessionStorage.setItem(KEY, JSON.stringify(sesion)); } catch (e2) {}
          history.replaceState(null, '', location.pathname + location.search);
        } else { sesion = null; }
      } catch (e) { sesion = null; console.warn('[auth] token URL inválido'); }
    }
  }

  // 3) Sin sesión válida → login
  if (!sesion || !sesion.usuario) { location.replace('login.html'); return; }

  window.__sesion = sesion;

  // 4) Chip de usuario + rol (si existe el elemento #user-chip en la página)
  document.addEventListener('DOMContentLoaded', function () {
    var chip = document.getElementById('user-chip');
    if (chip) {
      chip.innerHTML =
        '<span class="hidden sm:inline text-xs text-slate-400">' + sesion.nombre + '</span>' +
        '<span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">' + sesion.rol + '</span>';
      chip.classList.remove('hidden');
    }
  });

  // 5) Logout global
  /**
   * Cierra la sesión: borra sessionStorage y redirige al login.
   * @global
   */
  window.logout = function () {
    try { sessionStorage.removeItem(KEY); } catch (e) {}
    location.replace('login.html');
  };
})();
