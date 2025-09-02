# e2e_backend_test.py
import os
import time
import json
import traceback
import sys
from typing import Any, Dict, List, Tuple

try:
    import requests
except ImportError:
    raise SystemExit("Falta 'requests'. Instalalo con: pip install requests")

# ---------------- Config ----------------
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
OUT_FILE = os.getenv("OUT_FILE", "e2e_backend_results.json")
REQ_TIMEOUT = float(os.getenv("REQ_TIMEOUT", "60"))             # s
REQ_TIMEOUT_BULK = float(os.getenv("REQ_TIMEOUT_BULK", str(REQ_TIMEOUT * 2)))
WAIT_STARTUP = float(os.getenv("WAIT_STARTUP", "5"))            # s para esperar /health
SKIP_BULK = os.getenv("SKIP_BULK", "0") == "1"
SKIP_ADS = os.getenv("SKIP_ADS", "0") == "1"

session = requests.Session()
results: List[Dict[str, Any]] = []

# ---------- Datos de prueba ----------
LEADS = [
    {
        "nombre": "Carlos", "apellido": "Martinez", "email": "carlos@techvision.com",
        "telefono": "123456789", "empresa": "TechVision", "cargo": "CTO",
        "industria": "SaaS", "bio": "Explora automatización y herramientas AI"
    },
    {
        "nombre": "Ana", "apellido": "Silva", "email": "ana@eduimpact.org",
        "telefono": "111222333", "empresa": "EduImpact", "cargo": "Directora",
        "industria": "Educación", "bio": "Optimiza funnels educativos online"
    },
    {
        "nombre": "Luis", "apellido": "Rodriguez", "email": "luis@legalflow.com",
        "telefono": "444555666", "empresa": "LegalFlow", "cargo": "CEO",
        "industria": "LegalTech", "bio": "Busca escalar marketing digital"
    },
    {
        "nombre": "María", "apellido": "Gómez", "email": "maria@mineriaeco.com",
        "telefono": "333444555", "empresa": "MineríaEco", "cargo": "CMO",
        "industria": "Minería", "bio": "Cree en performance con automatización"
    },
    {
        "nombre": "Jorge", "apellido": "Fernandez", "email": "jorge@viajesejecutivos.com",
        "telefono": "999888777", "empresa": "Viajes Ejecutivos", "cargo": "CEO",
        "industria": "Turismo", "bio": "Explorando IA para captar clientes premium"
    },
    {
        "nombre": "Lucía", "apellido": "Pérez", "email": "lucia@farma360.com",
        "telefono": "222333444", "empresa": "Farma360", "cargo": "Marketing Manager",
        "industria": "Salud", "bio": "Busca optimizar campañas por canales"
    },
    {
        "nombre": "Hernán", "apellido": "Alonso", "email": "hernan@agrodata.io",
        "telefono": "555666777", "empresa": "AgroData", "cargo": "VP Marketing",
        "industria": "Agro", "bio": "Datos predictivos y performance rural"
    },
    {
        "nombre": "Julieta", "apellido": "Sosa", "email": "julieta@logix.com",
        "telefono": "666777888", "empresa": "LogiX", "cargo": "Especialista en Mkt",
        "industria": "Logística", "bio": "Automatización y tracking inteligente"
    },
    {
        "nombre": "Federico", "apellido": "Ibarra", "email": "fede@fintechpower.com",
        "telefono": "888999000", "empresa": "FintechPower", "cargo": "Coordinador de Marketing",
        "industria": "Fintech", "bio": "Aplica IA en adquisición multicanal"
    },
    {
        "nombre": "Valentina", "apellido": "López", "email": "vale@consultinghub.com",
        "telefono": "777888999", "empresa": "ConsultingHub", "cargo": "Marketing Director",
        "industria": "Consultoría", "bio": "Transformación digital con ROI"
    }
]

ADS_PAYLOAD = {
    "product_name": "iPhone 14 128GB",
    "value_prop": "Garantía oficial y envío en 24hs",
    "website": "https://libertyclub.io/",
    "landing_path": "/iphone-14",
    "location_countries": ["AR"],
    "location_cities": ["Buenos Aires", "Córdoba"],
    "language": "es",
    "budget_daily": 50,
    "objective": "conversions",
    "platform": ["google", "meta"],
    "personas": [
        {
            "name": "Tech Lovers 25-44",
            "age_min": 25,
            "age_max": 44,
            "genders": ["unknown"],
            "pains": ["celular lento"],
            "goals": ["mejor cámara", "batería"],
            "interests": ["Apple", "iOS", "Fotografía"],
            "keywords": ["iphone 14", "iphone 14 precio", "comprar iphone"]
        }
    ],
    "promo": "12x sin interés y envío gratis"
}

# ---------- Helpers ----------
def call(method: str, path: str, json_body: Dict[str, Any] | List[Dict[str, Any]] | None = None,
         timeout: float | None = None) -> Tuple[int, Any, float, str]:
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        resp = session.request(method=method, url=url, json=json_body, timeout=timeout or REQ_TIMEOUT)
        elapsed = (time.time() - t0) * 1000.0
        content_type = (resp.headers.get("content-type") or "").lower()
        data = resp.json() if "application/json" in content_type else resp.text
        return resp.status_code, data, elapsed, ""
    except Exception as e:
        elapsed = (time.time() - t0) * 1000.0
        return 0, None, elapsed, f"{type(e).__name__}: {e}"

def record(test_name: str, expected: int, status: int, elapsed_ms: float,
           payload: Any = None, response: Any = None, error: str = ""):
    results.append({
        "test_name": test_name,
        "status": "success" if status == expected else "error",
        "expected_status_code": expected,
        "actual_status_code": status,
        "elapsed_ms": round(elapsed_ms, 1),
        "request": payload,
        "response": response if status == expected else None,
        "error_detail": None if status == expected else (response if response else error)
    })

def ensure_keys(obj: Any, keys: List[str]) -> bool:
    if not isinstance(obj, dict):
        return False
    return all(k in obj for k in keys)

def wait_for_health(max_seconds: float = WAIT_STARTUP) -> bool:
    """Espera a que /health devuelva 200 hasta max_seconds."""
    deadline = time.time() + max_seconds
    while time.time() < deadline:
        status, data, _, _ = call("GET", "/health")
        if status == 200 and ensure_keys(data, ["status"]):
            return True
        time.sleep(0.5)
    return False

# ---------- Tests ----------
def test_health():
    status, data, t, err = call("GET", "/health")
    ok = (status == 200) and ensure_keys(data, ["status"])
    record("GET /health", 200, status, t, None, data if ok else data, err)

def test_leads_endpoint_list():
    status, data, t, err = call("GET", "/leads")
    ok = (status == 200)
    record("GET /leads", 200, status, t, None, data if ok else data, err)

def test_lead_classify_each():
    for i, lead in enumerate(LEADS):
        status, data, t, err = call("POST", "/leads/classify", lead)
        ok = (status == 200) and isinstance(data, dict) and ensure_keys(data, ["puntaje", "explicacion"])
        record(f"POST /leads/classify — Lead {i+1} - {lead.get('empresa')}",
               200, status, t, lead, data if ok else data, err)

def test_leads_bulk_import():
    status, data, t, err = call("POST", "/leads/bulk-import", LEADS, timeout=REQ_TIMEOUT_BULK)
    ok = (status == 200) and isinstance(data, dict) and data.get("processed") == len(LEADS)
    record("POST /leads/bulk-import", 200, status, t, {"items": len(LEADS)},
           data if ok else data, err)

def test_ads_segment():
    status, data, t, err = call("POST", "/ads/segment", ADS_PAYLOAD)
    ok_basic = (status == 200) and isinstance(data, dict) and ensure_keys(data, ["plan", "preview"])
    ok_plan = ok_basic and ensure_keys(data["plan"], ["product_name", "objective", "budget_daily"])
    ok = ok_basic and ok_plan
    record("POST /ads/segment", 200, status, t, ADS_PAYLOAD, data if ok else data, err)

# ---------- Runner ----------
if __name__ == "__main__":
    print(f"Running E2E tests against: {BASE_URL}")
    print(f"- REQ_TIMEOUT={REQ_TIMEOUT}s  REQ_TIMEOUT_BULK={REQ_TIMEOUT_BULK}s  WAIT_STARTUP={WAIT_STARTUP}s")
    if SKIP_BULK: print("- SKIP_BULK=1 (saltará /leads/bulk-import)")
    if SKIP_ADS: print("- SKIP_ADS=1 (saltará /ads/segment)")
    print()

    # Espera opcional a que el server esté OK
    if not wait_for_health(WAIT_STARTUP):
        print(f"⚠️  /health no respondió 200 dentro de {WAIT_STARTUP}s; continúo igual...\n")

    try:
        test_health()
        test_leads_endpoint_list()
        test_lead_classify_each()

        if not SKIP_BULK:
            test_leads_bulk_import()
        else:
            record("POST /leads/bulk-import (skipped)", 200, 200, 0.0, {"items": len(LEADS)}, {"skipped": True}, "")

        if not SKIP_ADS:
            test_ads_segment()
        else:
            record("POST /ads/segment (skipped)", 200, 200, 0.0, ADS_PAYLOAD, {"skipped": True}, "")

    except Exception:
        results.append({
            "test_name": "UNCAUGHT_EXCEPTION",
            "status": "error",
            "expected_status_code": 200,
            "actual_status_code": 0,
            "elapsed_ms": 0,
            "request": None,
            "response": None,
            "error_detail": traceback.format_exc()
        })

    # Resumen
    success = sum(1 for r in results if r["status"] == "success")
    error = len(results) - success
    summary = {"total": len(results), "success": success, "error": error}
    print("SUMMARY:", json.dumps(summary, indent=2), "\n")

    # Guardar resultado
    payload = {"base_url": BASE_URL, "summary": summary, "results": results}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Mostrar detalle por consola
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nReporte guardado en: {OUT_FILE}")

    # Exit code útil para CI
    sys.exit(0 if error == 0 else 1)
