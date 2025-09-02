# D:\IA-CRM-AUTO\models\ads.py
from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Annotated

Gender = Literal["male", "female", "unknown"]
Objective = Literal["leadgen", "conversions", "traffic", "reach", "awareness"]
Platform = Literal["google", "meta"]

# Pydantic v2: restricciones con Annotated + Field
Age = Annotated[int, Field(ge=13, le=100)]
Budget = Annotated[float, Field(gt=0)]

class Persona(BaseModel):
    name: str = Field(..., description="Nombre o etiqueta de la persona/segmento")
    age_min: Age = 18
    age_max: Age = 65
    genders: List[Gender] = ["unknown"]
    pains: List[str] = []
    goals: List[str] = []
    interests: List[str] = []   # Meta Ads
    keywords: List[str] = []    # Google Ads

class AdCampaignRequest(BaseModel):
    product_name: str
    value_prop: Optional[str] = None
    website: Optional[HttpUrl] = None
    landing_path: Optional[str] = None

    location_countries: List[str] = ["AR"]
    location_cities: List[str] = []
    language: Literal["es", "en", "pt", "other"] = "es"

    budget_daily: Budget = 10.0
    objective: Objective = "conversions"
    platform: List[Platform] = ["google", "meta"]

    personas: List[Persona]
    promo: Optional[str] = None

    # UTM opcionales (si no se envían se generan)
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None

class Creative(BaseModel):
    headline: str
    description: Optional[str] = None
    primary_text: Optional[str] = None  # Meta
    cta: str = "Más información"
    image_prompt: Optional[str] = None
    final_url: HttpUrl
    display_url: Optional[str] = None

class GooglePlan(BaseModel):
    bidding: str
    networks: List[str]
    locations: Dict[str, List[str]]  # {countries:[], cities:[]}
    schedule: str
    keywords_exact: List[str]
    keywords_phrase: List[str]
    negative_keywords: List[str]
    headlines: List[str]
    descriptions: List[str]
    final_url_template: str  # con {keyword}

class MetaPlan(BaseModel):
    placements: List[str]
    optimization_goal: str
    locations: Dict[str, List[str]]
    adsets: List[Dict]
    creatives: List[Creative]

class AdPlan(BaseModel):
    product_name: str
    objective: Objective
    budget_daily: float
    google: Optional[GooglePlan]
    meta: Optional[MetaPlan]

class AdPreview(BaseModel):
    google_search_card: Optional[Dict]
    meta_feed_card: Optional[Dict]

class AdSegmentResponse(BaseModel):
    plan: AdPlan
    preview: AdPreview
    download_url: Optional[str] = None  # (opcional) export
