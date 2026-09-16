// ============================================================
// auth.js — Guardián de sesión + utilidades de logout
// Incluir PRIMERO en toda página protegida (index*.html).
// Sesión: sessionStorage con fallback a token en URL (#s=base64)
// para navegadores que bloquean el almacenamiento.
// ============================================================
(function () {
  const KEY = 'sesionRiesgo';

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

  // 4) Chip de usuario + rol (si existe el elemento)
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
  window.logout = function () {
    try { sessionStorage.removeItem(KEY); } catch (e) {}
    location.replace('login.html');
  };
})();
