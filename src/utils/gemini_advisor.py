"""Asesor de riesgo financiero con IA (Google Gemini) — v1.

Convierte los agregados de la cartera SFC en contexto para el modelo y
responde preguntas de negocio en lenguaje natural.

Configuración de la API key (cualquiera de las dos):
  1) Variable de entorno:  GEMINI_API_KEY
  2) Archivo .env en la raíz del proyecto con:  GEMINI_API_KEY=tu_key

La key se obtiene gratis en https://aistudio.google.com
Sin key configurada el asesor responde con un aviso (la app sigue funcionando).
"""
from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _cargar_dotenv() -> None:
    """Carga GEMINI_API_KEY desde .env del proyecto si no viene en el entorno."""
    if os.getenv("GEMINI_API_KEY"):
        return
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8-sig").splitlines():
            linea = linea.strip()
            if linea.startswith("GEMINI_API_KEY") and "=" in linea:
                os.environ["GEMINI_API_KEY"] = linea.split("=", 1)[1].strip().strip('"').strip("'")


def consultar_asesor_gemini(pregunta: str, resumen: dict, top_entidades: str = "") -> str:
    """Consulta Gemini con el contexto de la cartera. Devuelve texto siempre."""
    _cargar_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "tu_api_key_aqui":
        return (
            "⚠️ **Asesor IA no activo**: falta configurar `GEMINI_API_KEY`.\n\n"
            "1. Crea una key gratis en [aistudio.google.com](https://aistudio.google.com)\n"
            "2. Crea un archivo `.env` en la raíz del proyecto con: `GEMINI_API_KEY=tu_key`\n"
            "   (o ejecuta `setx GEMINI_API_KEY \"tu_key\"` y reinicia Streamlit)\n\n"
            "El resto del dashboard funciona normalmente sin la key."
        )

    try:
        from google import genai
    except ImportError:
        return "⚠️ Falta la librería. Instala con:\n\n```\n.venv\\Scripts\\pip install google-genai\n```"

    contexto = f"""Contexto de la cartera analizada (Superfinanciera, datos reales):
- Exposición total filtrada: ${resumen.get('total_monto', 0):,.0f} COP
- % cartera vencida del conjunto: {resumen.get('pct_vencida', 0):.2f}%
- Registros en el filtro: {resumen.get('registros', 0):,}
- Registros clasificados Alto riesgo: {resumen.get('cant_alto_riesgo', 0):,}
- Score proxy promedio (0-1000): {resumen.get('score_prom', 0)}
{top_entidades}"""

    prompt = f"""Eres un analista senior de riesgo de crédito en Colombia, pragmático y claro.
{contexto}

Pregunta del usuario: {pregunta}

Responde en español, ejecutivo y conciso (máx. 6 viñetas o 3 párrafos).
Usa cifras del contexto cuando aporten. Si la pregunta requiere datos que no
están en el contexto, dilo explícitamente y sugiere qué filtro aplicar en el
dashboard para obtenerlos."""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text or "_(sin respuesta del modelo)_"
    except Exception as e:  # red, cuota, key inválida…
        return f"❌ Error al consultar Gemini: {e}"


def sugerencias_rapidas() -> list[str]:
    return [
        "¿Qué acciones tomarías con los registros de alto riesgo?",
        "Resume la salud de la cartera en 3 conclusiones ejecutivas",
        "¿Qué productos o entidades merecen monitoreo intensivo y por qué?",
    ]
