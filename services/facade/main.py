"""
JWG API Facade - Capability statement generator and admin interface
"""
import yaml
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import zipfile
import io
from typing import Optional, Dict, Any

app = FastAPI(title="JWG API Facade")

# CORS for demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
CONFIG_PATH = Path("/app/config/config.yaml")
config = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

HAPI_BASE_URL = "http://hapi-fhir:8080/fhir"
if not HAPI_BASE_URL.endswith("/"):
    HAPI_BASE_URL += "/"


def generate_capability_statement() -> Dict[str, Any]:
    """Generate a capability statement based on config"""
    interfaces = config.get("interfaces", {})
    priority_areas = config.get("supported_priority_areas", [])
    identifier_systems = config.get("supported_identifier_systems", {}).get("Patient", [])
    fhir_version = config.get("fhir_version", "4.0.1")
    
    # Base capability statement structure
    cap_statement = {
        "resourceType": "CapabilityStatement",
        "id": "jwg-provider",
        "url": "https://fhir.local/metadata",
        "version": "1.0.0",
        "name": "JWG API Provider",
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
            "url": "https://fhir.local",
            "description": "JWG API Demo Provider"
        },
        "rest": [
            {
                "mode": "server",
                "documentation": "JWG API Provider supporting document and resource access",
                "security": {
                    "cors": True
                },
                "resource": []
            }
        ]
    }
    
    # Add supported identifier systems extension
    if identifier_systems:
        cap_statement["rest"][0]["resource"].append({
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
                    "documentation": "Search by identifier"
                }
            ],
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/capabilitystatement-supported-system",
                    "valueString": system
                }
                for system in identifier_systems
            ]
        })
    
    # Add DocumentReference if document interface enabled
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
                    "documentation": "Search by patient"
                },
                {
                    "name": "type",
                    "type": "token",
                    "documentation": "Search by document type"
                },
                {
                    "name": "status",
                    "type": "token",
                    "documentation": "Search by status"
                }
            ]
        })
    
    # Add resource types if resource interface enabled
    if interfaces.get("resource", False):
        resource_types = ["Condition", "Observation", "AllergyIntolerance", "MedicationStatement", "Encounter"]
        for res_type in resource_types:
            cap_statement["rest"][0]["resource"].append({
                "type": res_type,
                "profile": f"http://hl7.org/fhir/StructureDefinition/{res_type}",
                "interaction": [
                    {"code": "read"},
                    {"code": "search-type"}
                ],
                "searchParam": [
                    {
                        "name": "patient",
                        "type": "reference",
                        "documentation": f"Search {res_type} by patient"
                    }
                ]
            })
    
    # Add priority areas extension
    if priority_areas:
        cap_statement["extension"] = [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/capabilitystatement-priority-area",
                "valueCode": area
            }
            for area in priority_areas
        ]
    
    return cap_statement


@app.get("/")
async def root():
    return {"message": "JWG API Facade", "version": "0.1.0"}


@app.get("/metadata")
async def get_metadata():
    """T1: Inspect - Return capability statement"""
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
    """Proxy POST requests to HAPI FHIR server"""
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


@app.get("/admin/import")
async def admin_import_page():
    """Admin import UI page"""
    return {
        "title": "Import Content",
        "description": "Upload FHIR bundles or ZIP files to import into the provider",
        "endpoint": "/admin/import",
        "method": "POST",
        "accepts": ["application/json", "application/zip", "application/fhir+json"]
    }


@app.post("/admin/import")
async def admin_import(file: UploadFile = File(...)):
    """T4: Admin Import - Upload content"""
    try:
        content = await file.read()
        
        # Try to parse as JSON bundle
        if file.content_type in ["application/json", "application/fhir+json"] or file.filename.endswith(".json"):
            bundle = json.loads(content.decode("utf-8"))
            if bundle.get("resourceType") == "Bundle":
                # Post bundle to HAPI
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{HAPI_BASE_URL}",
                        json=bundle,
                        headers={"Content-Type": "application/fhir+json"}
                    )
                    if response.status_code in [200, 201]:
                        return {
                            "status": "success",
                            "message": f"Imported {len(bundle.get('entry', []))} resources",
                            "response": response.json()
                        }
                    else:
                        raise HTTPException(status_code=response.status_code, detail=response.text)
        
        # Handle ZIP files
        elif file.content_type == "application/zip" or file.filename.endswith(".zip"):
            zip_data = io.BytesIO(content)
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                imported_count = 0
                for filename in zip_ref.namelist():
                    if filename.endswith(".json"):
                        file_content = zip_ref.read(filename)
                        bundle = json.loads(file_content.decode("utf-8"))
                        if bundle.get("resourceType") == "Bundle":
                            async with httpx.AsyncClient() as client:
                                response = await client.post(
                                    f"{HAPI_BASE_URL}",
                                    json=bundle,
                                    headers={"Content-Type": "application/fhir+json"}
                                )
                                if response.status_code in [200, 201]:
                                    imported_count += len(bundle.get("entry", []))
                
                return {
                    "status": "success",
                    "message": f"Imported {imported_count} resources from ZIP"
                }
        
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/export")
async def admin_export_page():
    """Admin export UI page"""
    return {
        "title": "Export Content",
        "description": "Export FHIR data for a patient",
        "endpoint": "/admin/export",
        "method": "POST",
        "parameters": {
            "patient_id": "Patient resource ID",
            "mode": "documents|resources|both"
        }
    }


@app.post("/admin/export")
async def admin_export(patient_id: str = Form(...), mode: str = Form("both")):
    """T5: Admin Export - Export content"""
    try:
        async with httpx.AsyncClient() as client:
            # Fetch patient
            patient_response = await client.get(f"{HAPI_BASE_URL}Patient/{patient_id}")
            if patient_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Patient not found")
            
            patient = patient_response.json()
            
            # Create export bundle
            export_bundle = {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": [{
                    "resource": patient
                }]
            }
            
            # Add documents if requested
            if mode in ["documents", "both"]:
                doc_response = await client.get(f"{HAPI_BASE_URL}DocumentReference?patient=Patient/{patient_id}")
                if doc_response.status_code == 200:
                    doc_bundle = doc_response.json()
                    if doc_bundle.get("entry"):
                        export_bundle["entry"].extend(doc_bundle["entry"])
            
            # Add resources if requested
            if mode in ["resources", "both"]:
                resource_types = ["Condition", "Observation", "AllergyIntolerance", "MedicationStatement", "Encounter"]
                for res_type in resource_types:
                    res_response = await client.get(f"{HAPI_BASE_URL}{res_type}?patient=Patient/{patient_id}")
                    if res_response.status_code == 200:
                        res_bundle = res_response.json()
                        if res_bundle.get("entry"):
                            export_bundle["entry"].extend(res_bundle["entry"])
            
            # Create ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr("export.json", json.dumps(export_bundle, indent=2))
            
            zip_buffer.seek(0)
            
            return FileResponse(
                path=None,
                filename=f"export_patient_{patient_id}.zip",
                media_type="application/zip",
                background=None
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
