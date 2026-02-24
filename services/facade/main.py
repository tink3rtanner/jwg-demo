"""
JWG API Facade - Capability statement generator aligned with EU Health Data API IG
Implements Document Access Provider and Resource Access Provider actors
"""
import os
import yaml
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Dict, Any

app = FastAPI(title="JWG API Facade")

# CORS for demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config - support environment variable override for non-Docker environments
CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", "/app/config/config.yaml"))
config = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

HAPI_BASE_URL = os.environ.get("HAPI_BASE_URL", "http://hapi-fhir:8080/fhir")
if not HAPI_BASE_URL.endswith("/"):
    HAPI_BASE_URL += "/"


def generate_capability_statement() -> Dict[str, Any]:
    """Generate a capability statement aligned with EU Health Data API IG
    
    Uses instantiates to reference priority area capability statements.
    Supports both Document Access Provider and Resource Access Provider actors.
    """
    interfaces = config.get("interfaces", {})
    priority_areas = config.get("supported_priority_areas", [])
    identifier_systems = config.get("supported_identifier_systems", {}).get("Patient", [])
    fhir_version = config.get("fhir_version", "4.0.1")
    base_url = config.get("base_url", "https://fhir.local")
    
    # Base capability statement structure
    cap_statement = {
        "resourceType": "CapabilityStatement",
        "id": "jwg-provider",
        "url": f"{base_url}/metadata",
        "version": "1.0.0",
        "name": "EU Health Data API Provider",
        "status": "active",
        "experimental": True,
        "publisher": "JWG Demo",
        "fhirVersion": fhir_version,
        "kind": "capability",
        "software": {
            "name": "JWG API Sandbox",
            "version": "0.1.0"
        },
        "implementation": {
            "url": base_url,
            "description": "EU Health Data API Demo Provider"
        },
        "rest": [
            {
                "mode": "server",
                "documentation": "EU Health Data API Provider supporting document and resource access",
                "security": {
                    "cors": True,
                    "description": "SMART Backend Services (system-to-system authorization)"
                },
                "resource": []
            }
        ]
    }
    
    # Add instantiates for priority areas (per IG specification)
    instantiates = []
    if interfaces.get("document", False):
        for area in priority_areas:
            instantiates.append(f"{base_url}/CapabilityStatement/document-access-{area.lower()}")
    if interfaces.get("resource", False):
        for area in priority_areas:
            instantiates.append(f"{base_url}/CapabilityStatement/resource-access-{area.lower()}")
    
    if instantiates:
        cap_statement["instantiates"] = instantiates
    
    # Add Patient resource with PDQm/PIXm support
    patient_resource = {
        "type": "Patient",
        "profile": "http://hl7.org/fhir/StructureDefinition/Patient",
        "interaction": [
            {"code": "read"},
            {"code": "search-type"}
        ],
        "searchParam": [
            {
                "name": "identifier",
                "type": "token",
                "documentation": "PDQm/PIXm: Search by identifier (required)"
            },
            {
                "name": "family",
                "type": "string",
                "documentation": "PDQm: Search by family name (optional)"
            },
            {
                "name": "given",
                "type": "string",
                "documentation": "PDQm: Search by given name (optional)"
            },
            {
                "name": "birthdate",
                "type": "date",
                "documentation": "PDQm: Search by birth date (optional)"
            }
        ]
    }
    
    # Add supported identifier systems extension (per IG)
    if identifier_systems:
        patient_resource["extension"] = [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/capabilitystatement-supported-system",
                "valueString": system
            }
            for system in identifier_systems
        ]
    
    cap_statement["rest"][0]["resource"].append(patient_resource)
    
    # Add DocumentReference if Document Access Provider enabled (MHD ITI-67, ITI-68)
    if interfaces.get("document", False):
        cap_statement["rest"][0]["resource"].append({
            "type": "DocumentReference",
            "profile": "http://hl7.org/fhir/StructureDefinition/DocumentReference",
            "interaction": [
                {"code": "read"},
                {"code": "search-type"}
            ],
            "searchParam": [
                {
                    "name": "patient",
                    "type": "reference",
                    "documentation": "MHD ITI-67: Search by patient"
                },
                {
                    "name": "type",
                    "type": "token",
                    "documentation": "MHD ITI-67: Search by document type (LOINC)"
                },
                {
                    "name": "category",
                    "type": "token",
                    "documentation": "MHD ITI-67: Search by category (XDS ClassCode)"
                },
                {
                    "name": "status",
                    "type": "token",
                    "documentation": "MHD ITI-67: Search by status"
                }
            ]
        })
        
        # Add Binary for document retrieval (MHD ITI-68)
        cap_statement["rest"][0]["resource"].append({
            "type": "Binary",
            "interaction": [
                {"code": "read"}
            ]
        })
    
    # Add resource types if Resource Access Provider enabled (QEDm PCC-44)
    if interfaces.get("resource", False):
        resource_types = [
            {"type": "Condition", "params": ["patient", "clinical-status"]},
            {"type": "Observation", "params": ["patient", "category", "date"]},
            {"type": "AllergyIntolerance", "params": ["patient"]},
            {"type": "MedicationStatement", "params": ["patient", "status"]},
            {"type": "MedicationRequest", "params": ["patient", "status"]},
            {"type": "DiagnosticReport", "params": ["patient", "category"]},
            {"type": "Immunization", "params": ["patient", "date"]},
            {"type": "Encounter", "params": ["patient", "date"]}
        ]
        
        for res_def in resource_types:
            res_type = res_def["type"]
            params = res_def["params"]
            cap_statement["rest"][0]["resource"].append({
                "type": res_type,
                "profile": f"http://hl7.org/fhir/StructureDefinition/{res_type}",
                "interaction": [
                    {"code": "read"},
                    {"code": "search-type"}
                ],
                "searchParam": [
                    {
                        "name": param,
                        "type": "reference" if param == "patient" else ("token" if param in ["clinical-status", "status", "category"] else "date"),
                        "documentation": f"QEDm PCC-44: Search {res_type} by {param}"
                    }
                    for param in params
                ]
            })
    
    return cap_statement


@app.get("/")
async def root():
    return {"message": "JWG API Facade", "version": "0.1.0"}


@app.get("/metadata")
async def get_metadata():
    """Capability Discovery - Return capability statement per EU Health Data API IG
    
    Returns a CapabilityStatement that declares:
    - Supported priority areas via instantiates
    - Document Access Provider capabilities (MHD ITI-67, ITI-68)
    - Resource Access Provider capabilities (QEDm PCC-44)
    - Patient identity matching capabilities (PDQm/PIXm)
    """
    return generate_capability_statement()


@app.get("/fhir/{path:path}")
async def proxy_fhir(path: str):
    """Proxy requests to HAPI FHIR server"""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{HAPI_BASE_URL}{path}"
            response = await client.get(url)
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




@app.post("/fhir/{path:path}")
async def proxy_fhir_post(path: str, body: dict = None):
    """Proxy POST requests to HAPI FHIR server
    
    Supports:
    - Patient/$match (PDQm ITI-119) for fuzzy patient matching
    - Document publication (MHD ITI-65) via Bundle POST
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"{HAPI_BASE_URL}{path}"
            response = await client.post(url, json=body or {})
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
