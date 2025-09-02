import requests
import json

BASE_URL = "http://localhost:8000"
results = []

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

def test_lead(lead, i):
    try:
        res = requests.post(f"{BASE_URL}/leads/classify", json=lead)
        status = "success" if res.status_code == 200 else "error"
        results.append({
            "test_name": f"Lead {i+1} - {lead['empresa']}",
            "status": status,
            "expected_status_code": 200,
            "actual_status_code": res.status_code,
            "message": res.json() if status == "success" else None,
            "error_detail": None if status == "success" else res.text
        })
    except Exception as e:
        results.append({
            "test_name": f"Lead {i+1} - {lead['empresa']}",
            "status": "error",
            "expected_status_code": 200,
            "actual_status_code": 0,
            "message": None,
            "error_detail": str(e)
        })

for idx, lead in enumerate(LEADS):
    test_lead(lead, idx)

# Guardar resultado
with open("e2e_big_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
