from fastapi import FastAPI, HTTPException, Query
from typing import List
from models.lead import LeadData
from services.enrich import enriquecer_datos_lead
from services.scoring import score_lead
from services.classify_ia import clasificar_lead_por_ia
from database.mysql import get_all_leads, insert_lead
from models.ads import AdCampaignRequest, AdSegmentResponse
from services.ads import build_ad_plan, build_previews

from concurrent.futures import ThreadPoolExecutor, as_completed

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/leads")
def get_leads():
    return get_all_leads()

@app.post("/leads/classify")
def classify_lead(lead: LeadData):
    try:
        enriched = enriquecer_datos_lead(lead.dict())
        enriched["puntaje"] = score_lead(enriched)
        enriched["explicacion"] = clasificar_lead_por_ia(enriched)
        insert_lead(enriched)
        return enriched
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/leads/bulk-import")
def bulk_import(leads: List[LeadData], use_ai: bool = Query(False, description="Usar IA para explicación")):
    results = {"processed": 0, "success": 0, "failed": 0, "errors": []}
    def process_one(idx: int, lead: LeadData):
        l = enriquecer_datos_lead(lead.dict())
        l["puntaje"] = score_lead(l)
        l["explicacion"] = clasificar_lead_por_ia(l) if use_ai else f"Procesado en lote sin IA. Puntaje: {l['puntaje']}."
        try:
            insert_lead(l)
        except Exception as e:
            return (idx, False, f"DB insert error: {e}")
        return (idx, True, l)
    max_workers = min(4, max(1, len(leads)))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for fut in as_completed([ex.submit(process_one, i, lead) for i, lead in enumerate(leads)]):
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
