from fastapi import FastAPI, HTTPException, Query
from models.lead import LeadData
from services.enrich import enriquecer_datos_lead
from services.scoring import score_lead
from services.classify_ia import clasificar_lead_por_ia
from utils import *
from database.mysql import *
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from func.functions import *
from models.ads import *
from services.ads import *
from concurrent.futures import ThreadPoolExecutor, as_completed
# Cargar variables de entorno
load_dotenv()

# Instancia FastAPI
app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://ia-crm-auto.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # permite cualquier subdominio de vercel.app
    allow_methods=["*"],       # o ["POST", "OPTIONS"] si querés acotar
    allow_headers=["*"],
    allow_credentials=False,   # si vas a usar cookies: ponelo True y NO uses "*" en origins
))

# Endpoint de salud
@app.get("/health")
def health():
    return {"status": "ok"}

# Obtener todos los leads desde la base de datos
@app.get("/leads")
def get_leads():
    return get_all_leads()

# Clasificar un lead individual
@app.post("/leads/classify")
def classify_lead(lead: LeadData):
    try:
        enriched = enriquecer_datos_lead(lead.dict())
        enriched["puntaje"] = score_lead(enriched)
        enriched["explicacion"] = clasificar_lead_por_ia(enriched)  # <- segura
        insert_lead(enriched)
        return enriched
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/leads/bulk-import")
def bulk_import(leads: List[LeadData], use_ai: bool = Query(False, description="Usar IA para explicación")):
    """
    Procesa en paralelo, pero por defecto sin IA para evitar cuotas/429.
    Habilitá IA en bulk con ?use_ai=1 si lo necesitás.
    """
    results = {"processed": 0, "success": 0, "failed": 0, "errors": []}

    def process_one(idx: int, lead: LeadData):
        l = enriquecer_datos_lead(lead.dict())
        l["puntaje"] = score_lead(l)
        if use_ai:
            l["explicacion"] = clasificar_lead_por_ia(l)   # segura (c/ fallback)
        else:
            # Mini-explicación local sin IA
            l["explicacion"] = (
                f"Procesado en lote sin IA. Puntaje calculado: {l['puntaje']}."
                " Activá ?use_ai=1 para explicación generada por IA (con rate-limit)."
            )
        try:
            insert_lead(l)
        except Exception as e:
            return (idx, False, f"DB insert error: {e}")
        return (idx, True, l)

    max_workers = min(4, max(1, len(leads)))  # I/O bound razonable
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for i, lead in enumerate(leads):
            futures.append(ex.submit(process_one, i, lead))
        for fut in as_completed(futures):
            idx, ok, payload = fut.result()
            results["processed"] += 1
            if ok: results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"index": idx, "error": str(payload)})

    return results

@app.post("/ads/segment", response_model=AdSegmentResponse)
def ads_segment(req: AdCampaignRequest):
    try:
        plan = build_ad_plan(req)
        preview = build_previews(plan)
        return {"plan": plan, "preview": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))