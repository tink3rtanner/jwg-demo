#!/usr/bin/env python3
"""
Seed script to load demo data into HAPI FHIR server
"""
import httpx
import json
import time
from pathlib import Path

HAPI_BASE_URL = "http://hapi-fhir:8080/fhir"
EXAMPLES_DIR = Path("/app/examples")

def wait_for_hapi(max_retries=30):
    """Wait for HAPI FHIR server to be ready"""
    print("Waiting for HAPI FHIR server...")
    for i in range(max_retries):
        try:
            response = httpx.get(f"{HAPI_BASE_URL}/metadata", timeout=5)
            if response.status_code == 200:
                print("HAPI FHIR server is ready!")
                return True
        except Exception:
            pass
        time.sleep(2)
        print(f"  Retry {i+1}/{max_retries}...")
    return False

def load_resource(resource_data):
    """Load a single resource into HAPI"""
    resource_type = resource_data.get("resourceType")
    resource_id = resource_data.get("id")
    
    url = f"{HAPI_BASE_URL}/{resource_type}"
    if resource_id:
        url += f"/{resource_id}"
    
    try:
        response = httpx.put(
            url,
            json=resource_data,
            headers={"Content-Type": "application/fhir+json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            print(f"  ✓ Loaded {resource_type}/{resource_id or 'new'}")
            return True
        else:
            print(f"  ✗ Failed to load {resource_type}/{resource_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ Error loading {resource_type}/{resource_id}: {e}")
        return False

def load_bundle(bundle_data):
    """Load a bundle of resources"""
    entries = bundle_data.get("entry", [])
    success_count = 0
    for entry in entries:
        resource = entry.get("resource")
        if resource:
            if load_resource(resource):
                success_count += 1
    return success_count

def main():
    if not wait_for_hapi():
        print("ERROR: HAPI FHIR server did not become ready")
        return 1
    
    print("\nLoading seed data...")
    
    # Load all JSON files from examples directory
    json_files = list(EXAMPLES_DIR.glob("*.json"))
    
    if not json_files:
        print("No example files found in /app/examples")
        return 1
    
    total_loaded = 0
    for json_file in json_files:
        print(f"\nLoading {json_file.name}...")
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            if data.get("resourceType") == "Bundle":
                count = load_bundle(data)
                total_loaded += count
            else:
                if load_resource(data):
                    total_loaded += 1
        except Exception as e:
            print(f"  ✗ Error loading {json_file.name}: {e}")
    
    print(f"\n✓ Seed complete! Loaded {total_loaded} resources.")
    return 0

if __name__ == "__main__":
    exit(main())
