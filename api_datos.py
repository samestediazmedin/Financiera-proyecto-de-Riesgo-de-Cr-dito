"""API JSON en vivo desde data/processed — base de datos del proyecto.

Servidor stdlib (sin dependencias extra) que expone:

  GET /api/sistema  -> agregados BI de la Superfinanciera/ICETEX
                       (misma forma que datos_sistema.js, calculada EN VIVO)
  GET /api/health   -> "ok"

Recalcula automaticamente cuando los CSV cambian (cache por mtime).
Uso:  .venv/Scripts/python.exe api_datos.py   (puerto 8189)
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from src.utils.exportar_agregados_dashboard import SFC, ICETEX, generar_datos

_cache = {"datos": None, "firma": None}


def datos_frescos() -> dict:
    """Devuelve agregados; recalcula si alg\u00fan CSV cambi\u00f3 en disco."""
    firma = (SFC.stat().st_mtime, ICETEX.stat().st_mtime if ICETEX.exists() else 0)
    if _cache["datos"] is None or _cache["firma"] != firma:
        _cache["datos"] = generar_datos()
        _cache["firma"] = firma
    return _cache["datos"]


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_GET(self):
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
        pass


if __name__ == "__main__":
    puerto = 8189
    srv = ThreadingHTTPServer(("127.0.0.1", puerto), Handler)
    print(f"API de datos en http://127.0.0.1:{puerto}/api/sistema (Ctrl+C para parar)")
    srv.serve_forever()
