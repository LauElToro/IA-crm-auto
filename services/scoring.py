def score_lead(data):
    score = 0

    if "CEO" in (data.get("cargo") or ""):
        score += 20

    if data.get("industria") in ["SaaS", "Turismo", "Educación"]:
        score += 15

    if data.get("tamaño_empresa") == "51-200":
        score += 10

    if "automatización" in (data.get("bio") or "").lower():
        score += 10

    return min(score, 100)
