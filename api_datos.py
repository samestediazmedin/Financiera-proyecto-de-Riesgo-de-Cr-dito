"""API JSON en vivo desde ``data/processed`` — base de datos del proyecto.

Propósito
---------
Micro-servidor HTTP construido solo con la librería estándar de Python
(sin dependencias extra) que expone los agregados BI calculados en vivo
por :func:`src.utils.exportar_agregados_dashboard.generar_datos`.

Endpoints
---------
``GET /api/sistema``
    Agregados BI de la Superfinanciera/ICETEX (misma forma que el objeto
    ``DATOS_SISTEMA`` de ``datos_sistema.js``, pero calculada EN VIVO).
``GET /api/health``
    Chequeo de vida; responde el texto plano ``"ok"``.
Cualquier otra ruta responde ``404``.

El resultado se cachea en memoria y se recalcula automáticamente cuando
algún CSV subyacente cambia en disco (comparación por ``mtime``).

Uso:
    .venv/Scripts/python.exe api_datos.py   (escucha en 127.0.0.1:8189)

Documentado: 2026-09-18.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from src.utils.exportar_agregados_dashboard import SFC, ICETEX, IEFIC, generar_datos

# Caché en memoria del último cálculo: {"datos": dict, "firma": tuple de mtimes}
_cache = {"datos": None, "firma": None}


def datos_frescos() -> dict:
    """Devuelve los agregados BI, recalculando si algún CSV cambió en disco.

    La "firma" de frescura es la tupla de ``st_mtime`` de los tres archivos
    fuente (SFC, ICETEX e IEFIC); si difiere de la última calculada se
    regenera el agregado con :func:`generar_datos`.

    Returns:
        dict: Estructura ``serieVencida``/``topProductos``/``calificacion``/
        ``icetexTop``/``iefic``/``meta`` lista para serializar como JSON.
    """
    firma = (SFC.stat().st_mtime, ICETEX.stat().st_mtime if ICETEX.exists() else 0, IEFIC.stat().st_mtime if IEFIC.exists() else 0)
    if _cache["datos"] is None or _cache["firma"] != firma:
        _cache["datos"] = generar_datos()
        _cache["firma"] = firma
    return _cache["datos"]


class Handler(BaseHTTPRequestHandler):
    """Handler HTTP con las rutas de la API.

    Procesa únicamente solicitudes ``GET``; ver :meth:`do_GET`. Todas las
    respuestas incluyen cabeceras CORS abiertas (``*``) y ``no-store`` para
    facilitar el consumo desde el frontend express durante el desarrollo.
    """

    def _cors(self):
        """Envía las cabeceras CORS y anti-caché comunes a toda respuesta."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_GET(self):
        """Enruta las solicitudes GET: ``/api/sistema`` y ``/api/health``.

        Args:
            No recibe argumentos; usa ``self.path`` (ruta solicitada).

        Comportamiento:
            - ``/api/sistema``: responde 200 con el JSON de
              :func:`datos_frescos` en UTF-8.
            - ``/api/health``: responde 200 con el texto ``ok``.
            - Otras rutas: 404 sin cuerpo.
        """
        if self.path == "/api/sistema":
            body = json.dumps(datos_frescos(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/health":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def log_message(self, *args):  # silencioso
        """Silencia el log por defecto de BaseHTTPRequestHandler (no log de accesos)."""
        pass


if __name__ == "__main__":
    # Arranque del servidor: solo escucha en localhost (127.0.0.1) por diseño.
    puerto = 8189
    srv = ThreadingHTTPServer(("127.0.0.1", puerto), Handler)
    print(f"API de datos en http://127.0.0.1:{puerto}/api/sistema (Ctrl+C para parar)")
    srv.serve_forever()
