from typing import List, Dict
from .ads_rules import GOOGLE_NEGATIVES_BASE, META_DEFAULT_PLACEMENTS
from models.ads import AdCampaignRequest, AdPlan, GooglePlan, MetaPlan, Creative
from utils.utm import build_final_url, slugify

# Helpers

def _default_cta(objective: str) -> str:
    return {
        "leadgen": "Solicitar info",
        "conversions": "Comprar ahora",
        "traffic": "Más información",
        "reach": "Conocer más",
        "awareness": "Conocer más",
    }.get(objective, "Más información")


def _google_bidding(objective: str) -> str:
    return {
        "conversions": "MaximizeConversions",
        "leadgen": "MaximizeConversions (Lead Form / Conversiones)",
        "traffic": "MaximizeClicks",
        "reach": "TargetImpressionShare",
        "awareness": "TargetImpressionShare",
    }.get(objective, "MaximizeConversions")


def _meta_optimization_goal(objective: str) -> str:
    return {
        "conversions": "Conversions",
        "leadgen": "Leads",
        "traffic": "LinkClicks",
        "reach": "Reach",
        "awareness": "ThruPlay",
    }.get(objective, "Conversions")


def _expand_keywords(product: str, base: List[str]) -> List[str]:
    seeds = {product.lower()}
    for b in base:
        for t in b.lower().split():
            seeds.add(t)
    seeds = list({s.strip() for s in seeds if s.strip()})
    # Variantes simples; en prod podrías integrar word2vec/embeddings
    variants = []
    for s in seeds:
        variants += [
            s,
            f"{s} precio",
            f"{s} comprar",
            f"{s} opiniones",
            f"{s} cuotas",
            f"{s} envío",
        ]
    return list(dict.fromkeys(variants))  # unique y orden estable


def _build_google(req: AdCampaignRequest, utm_campaign: str) -> GooglePlan:
    persona_keywords = [kw for p in req.personas for kw in (p.keywords or [])]
    keywords = _expand_keywords(req.product_name, persona_keywords)

    headlines = list(filter(None, [
        f"{req.product_name} oficial",
        req.value_prop,
        req.promo,
        "Envíos a todo el país",
        "12x sin interés",
    ]))[:5]

    descriptions = list(filter(None, [
        req.value_prop,
        req.promo,
        "Soporte local y garantía",
        "Comprá online de forma segura",
    ]))[:4]

    final_url_template = build_final_url(
        base=(req.website or "https://example.com"),
        path=(req.landing_path or "/"),
        utm={
            "utm_source": req.utm_source or "google",
            "utm_medium": req.utm_medium or "cpc",
            "utm_campaign": utm_campaign,
            "utm_term": "{keyword}",  # macro para Search
        },
    )

    return GooglePlan(
        bidding=_google_bidding(req.objective),
        networks=["Search"],
        locations={"countries": req.location_countries, "cities": req.location_cities},
        schedule="Lun-Dom 08:00–22:00 (zona anunciante)",
        keywords_exact=[f"[{k}]" for k in keywords[:40]],
        keywords_phrase=[f'"{k}"' for k in keywords[40:100]],
        negative_keywords=GOOGLE_NEGATIVES_BASE,
        headlines=headlines,
        descriptions=descriptions,
        final_url_template=final_url_template,
    )


def _build_meta(req: AdCampaignRequest, utm_campaign: str) -> MetaPlan:
    adsets = []
    creatives = []

    for p in req.personas:
        utm = {
            "utm_source": req.utm_source or "meta",
            "utm_medium": req.utm_medium or "paid_social",
            "utm_campaign": utm_campaign,
            "utm_content": slugify(p.name),
        }
        final_url = build_final_url(req.website or "https://example.com", req.landing_path, utm)

        # Creative base (texto + prompt de imagen)
        primary_text = (
            f"{req.value_prop or req.product_name}. "
            + (f"{req.promo}. " if req.promo else "")
            + "Comprá online en minutos."
        )
        headline = req.product_name
        description = req.promo or "Envíos a todo el país"
        image_prompt = f"Foto producto {req.product_name} sobre fondo limpio, estilo e-commerce, luz suave"

        creatives.append(
            Creative(
                headline=headline,
                description=description,
                primary_text=primary_text,
                cta=_default_cta(req.objective),
                image_prompt=image_prompt,
                final_url=final_url,
                display_url=None,
            )
        )

        adsets.append(
            {
                "name": p.name,
                "age_min": p.age_min,
                "age_max": p.age_max,
                "genders": p.genders,
                "interests": p.interests[:25],  # Meta recomienda <=25
                "budget_daily_split": round(req.budget_daily / max(1, len(req.personas)), 2),
            }
        )

    return MetaPlan(
        placements=META_DEFAULT_PLACEMENTS,
        optimization_goal=_meta_optimization_goal(req.objective),
        locations={"countries": req.location_countries, "cities": req.location_cities},
        adsets=adsets,
        creatives=creatives,
    )


def build_ad_plan(req: AdCampaignRequest) -> AdPlan:
    utm_campaign = req.utm_campaign or slugify(req.product_name)

    google = _build_google(req, utm_campaign) if "google" in req.platform else None
    meta = _build_meta(req, utm_campaign) if "meta" in req.platform else None

    return AdPlan(
        product_name=req.product_name,
        objective=req.objective,
        budget_daily=req.budget_daily,
        google=google,
        meta=meta,
    )


def build_previews(plan: AdPlan) -> dict:
    preview = {"google_search_card": None, "meta_feed_card": None}

    if plan.google:
        # Tomamos los primeros assets para la tarjeta
        h = " | ".join((plan.google.headlines + [""] * 3)[:3])
        d = (plan.google.descriptions + [""])[0]
        preview["google_search_card"] = {
            "title": h,
            "description": d,
            "url": plan.google.final_url_template.replace("{keyword}", "iphone 14"),
            "path": "tienda/ofertas",
        }

    if plan.meta and plan.meta.creatives:
        c = plan.meta.creatives[0]
        preview["meta_feed_card"] = {
            "primary_text": c.primary_text,
            "headline": c.headline,
            "description": c.description,
            "cta": c.cta,
            "url": c.final_url,
            "image_prompt": c.image_prompt,
        }

    return preview