def enriquecer_datos_lead(lead):
    # Simulación de enriquecimiento externo
    enrichment = {
        "tamaño_empresa": "51-200",  # Simulado, puede venir de APIs reales como Clearbit
        "industria": lead.get("industria") or "SaaS",
        "tecnologias": ["Google Ads", "Hubspot", "Zapier"]
    }
    lead.update(enrichment)
    return lead
