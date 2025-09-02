from __future__ import annotations
import os, time
from threading import Semaphore
from typing import Dict, Any

AI_ENABLED = os.getenv("CLASSIFY_AI_ENABLED", "1") == "1"
AI_MAX_CONCURRENCY = int(os.getenv("AI_MAX_CONCURRENCY", "1"))
AI_MIN_SECONDS_BETWEEN_CALLS = float(os.getenv("AI_MIN_SECONDS_BETWEEN_CALLS", "0.0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_sem = Semaphore(AI_MAX_CONCURRENCY)

def _fallback_explicacion(lead: Dict[str, Any], motivo: str) -> str:
    puntaje = lead.get("puntaje", "N/A")
    empresa = lead.get("empresa") or lead.get("nombre") or "el lead"
    cargo = lead.get("cargo") or "—"
    industria = lead.get("industria") or "—"
    return (
        f"Evaluación automática (sin IA) — Puntaje: **{puntaje}**.\n\n"
        f"- Empresa: {empresa}\n"
        f"- Cargo: {cargo}\n"
        f"- Industria: {industria}\n\n"
        f"Se generó una explicación heurística porque la IA no estuvo disponible ({motivo})."
    )

def _llm_explicacion(lead: Dict[str, Any]) -> str:
    import google.generativeai as genai
    from google.api_core.exceptions import GoogleAPIError, ResourceExhausted

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY no configurada")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        "Eres un analista de marketing. Explica en 1-2 párrafos (conciso, en español) "
        "por qué este lead es interesante para una agencia performance + IA. "
        "Incluye señales positivas y dudas. Datos del lead:\n"
        f"{lead}"
    )

    with _sem:
        if AI_MIN_SECONDS_BETWEEN_CALLS > 0:
            time.sleep(AI_MIN_SECONDS_BETWEEN_CALLS)
        resp = model.generate_content(prompt)
        return resp.text or "Sin texto devuelto por IA"

def clasificar_lead_por_ia(lead: Dict[str, Any]) -> str:
    """
    Versión segura: usa IA si está habilitada y disponible;
    si no, devuelve explicación heurística (no rompe el endpoint).
    """
    if not AI_ENABLED:
        return _fallback_explicacion(lead, "IA deshabilitada por configuración")

    try:
        return _llm_explicacion(lead)
    except Exception as e:
        motivo = type(e).__name__
        return _fallback_explicacion(lead, motivo)