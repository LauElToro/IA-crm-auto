import requests
import json

BASE_URL = "http://localhost:8000"

results = []

def log_result(name, response, expected_code):
    status = "success" if response.status_code == expected_code else "error"
    results.append({
        "test_name": name,
        "status": status,
        "expected_status_code": expected_code,
        "actual_status_code": response.status_code,
        "message": response.json() if response.status_code == 200 else None,
        "error_detail": None if response.status_code == expected_code else response.text
    })

# 1. Health check
try:
    r = requests.get(f"{BASE_URL}/health")
    log_result("Health Check", r, 200)
except Exception as e:
    results.append({
        "test_name": "Health Check",
        "status": "error",
        "expected_status_code": 200,
        "actual_status_code": 0,
        "message": None,
        "error_detail": str(e)
    })

# 2. Classify single lead
try:
    payload = {
        "nombre": "Laura",
        "apellido": "Gonzalez",
        "email": "laura@example.com",
        "telefono": "123456789",
        "empresa": "Viajes Geniales",
        "cargo": "CEO",
        "industria": "Turismo",
        "bio": "Apasionada del marketing y automatización"
    }
    r = requests.post(f"{BASE_URL}/leads/classify", json=payload)
    log_result("Classify Lead", r, 200)
except Exception as e:
    results.append({
        "test_name": "Classify Lead",
        "status": "error",
        "expected_status_code": 200,
        "actual_status_code": 0,
        "message": None,
        "error_detail": str(e)
    })

# 3. Bulk import
try:
    payload = [
        {
            "nombre": "Carlos",
            "apellido": "Martinez",
            "email": "carlos@example.com",
            "telefono": "987654321",
            "empresa": "TechVision",
            "cargo": "CTO",
            "industria": "SaaS",
            "bio": "Interesado en automatización y herramientas de IA"
        },
        {
            "nombre": "Ana",
            "apellido": "Silva",
            "email": "ana@example.com",
            "telefono": "1122334455",
            "empresa": "EduFuturo",
            "cargo": "Directora",
            "industria": "Educación",
            "bio": "Explorando soluciones digitales innovadoras"
        }
    ]
    r = requests.post(f"{BASE_URL}/leads/bulk-import", json=payload)
    log_result("Bulk Import", r, 200)
except Exception as e:
    results.append({
        "test_name": "Bulk Import",
        "status": "error",
        "expected_status_code": 200,
        "actual_status_code": 0,
        "message": None,
        "error_detail": str(e)
    })

# 4. Get all leads
try:
    r = requests.get(f"{BASE_URL}/leads")
    log_result("Get Leads", r, 200)
except Exception as e:
    results.append({
        "test_name": "Get Leads",
        "status": "error",
        "expected_status_code": 200,
        "actual_status_code": 0,
        "message": None,
        "error_detail": str(e)
    })

# Output final JSON
with open("e2e_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
