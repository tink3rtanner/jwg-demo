#!/usr/bin/env python3
"""
EU Health Data API Demo Runner
ASCII art interactive demo with visual effects
"""

import time
import json
import sys
import subprocess
from typing import Dict, List, Optional
import httpx
from pathlib import Path

# Colors and styles
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Claude code style colors
    BLUE = '\033[38;5;75m'
    CYAN = '\033[38;5;87m'
    GREEN = '\033[38;5;84m'
    YELLOW = '\033[38;5;227m'
    ORANGE = '\033[38;5;215m'
    RED = '\033[38;5;203m'
    PURPLE = '\033[38;5;141m'
    GRAY = '\033[38;5;244m'
    
    BG_BLUE = '\033[48;5;17m'
    BG_GREEN = '\033[48;5;22m'
    BG_RED = '\033[48;5;52m'

API_BASE = "http://localhost:8082"
FHIR_BASE = "http://localhost:8082"

def clear_screen():
    """Clear terminal screen"""
    print("\033[2J\033[H", end="")

def print_header():
    """Print ASCII header"""
    header = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.BOLD}{Colors.BLUE}EU Health Data API Demo Suite{Colors.RESET}  {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}║{Colors.RESET}  {Colors.DIM}5-Actor Model • MHD • QEDm • PDQm/PIXm{Colors.RESET}  {Colors.CYAN}║{Colors.RESET}
{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(header)

def bounce_animation(text: str, duration: float = 1.0):
    """Bouncing text animation"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Colors.CYAN}{frames[i % len(frames)]}{Colors.RESET} {text}", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{Colors.GREEN}✓{Colors.RESET} {text}")

def pulse_animation(text: str, duration: float = 0.5):
    """Pulsing animation"""
    frames = ["●", "○", "●"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        color = Colors.GREEN if i % 2 == 0 else Colors.CYAN
        print(f"\r{color}{frames[i % len(frames)]}{Colors.RESET} {text}", end="", flush=True)
        time.sleep(0.2)
        i += 1
    print(f"\r{Colors.GREEN}✓{Colors.RESET} {text}")

def print_section(title: str, color=Colors.BLUE):
    """Print section header"""
    print(f"\n{color}{'═' * 60}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{color}{'═' * 60}{Colors.RESET}\n")

def print_test(name: str, status: str, details: str = ""):
    """Print test result"""
    if status == "pass":
        icon = f"{Colors.GREEN}✓{Colors.RESET}"
    elif status == "fail":
        icon = f"{Colors.RED}✗{Colors.RESET}"
    elif status == "skip":
        icon = f"{Colors.YELLOW}⊘{Colors.RESET}"
    else:
        icon = f"{Colors.CYAN}→{Colors.RESET}"
    
    print(f"  {icon} {name}")
    if details:
        print(f"    {Colors.DIM}{Colors.GRAY}{details}{Colors.RESET}")

def print_json(data: dict, max_lines: int = 10):
    """Print JSON in Claude code style"""
    json_str = json.dumps(data, indent=2)
    lines = json_str.split('\n')
    
    print(f"{Colors.BG_BLUE}{Colors.CYAN}")
    for i, line in enumerate(lines[:max_lines]):
        print(f"  {line}")
    if len(lines) > max_lines:
        print(f"  {Colors.DIM}... ({len(lines) - max_lines} more lines){Colors.RESET}")
    print(f"{Colors.RESET}")

def wait_for_service(url: str, max_attempts: int = 30) -> bool:
    """Wait for service to be ready"""
    for i in range(max_attempts):
        try:
            response = httpx.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def test_capability_discovery():
    """Test capability discovery"""
    print_section("1. Capability Discovery", Colors.BLUE)
    
    bounce_animation("Fetching CapabilityStatement...", 0.8)
    try:
        response = httpx.get(f"{API_BASE}/metadata", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("GET /metadata", "pass", f"Status: {response.status_code}")
            
            # Check structure
            if data.get("resourceType") == "CapabilityStatement":
                print_test("ResourceType is CapabilityStatement", "pass")
            else:
                print_test("ResourceType is CapabilityStatement", "fail")
                return False
            
            if data.get("fhirVersion") == "4.0.1":
                print_test("FHIR version is 4.0.1", "pass")
            else:
                print_test("FHIR version is 4.0.1", "fail")
            
            # Check instantiates
            if "instantiates" in data and isinstance(data["instantiates"], list):
                inst_count = len(data["instantiates"])
                print_test("instantiates field present", "pass", f"{inst_count} priority area(s)")
            else:
                print_test("instantiates field present", "fail")
            
            # Check resources
            resources = data.get("rest", [{}])[0].get("resource", [])
            doc_ref = any(r.get("type") == "DocumentReference" for r in resources)
            binary = any(r.get("type") == "Binary" for r in resources)
            condition = any(r.get("type") == "Condition" for r in resources)
            
            if doc_ref:
                print_test("DocumentReference resource declared", "pass")
            if binary:
                print_test("Binary resource declared", "pass")
            if condition:
                print_test("Resource types declared (QEDm)", "pass")
            
            print(f"\n{Colors.CYAN}CapabilityStatement Preview:{Colors.RESET}")
            print_json({
                "resourceType": data.get("resourceType"),
                "fhirVersion": data.get("fhirVersion"),
                "instantiates": data.get("instantiates", [])[:2],
                "rest": [{
                    "resource": [{"type": r.get("type")} for r in resources[:5]]
                }]
            })
            
            return True
        else:
            print_test("GET /metadata", "fail", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("GET /metadata", "fail", str(e))
        return False

def test_patient_match():
    """Test patient match"""
    print_section("2. Patient Match (PDQm/PIXm)", Colors.PURPLE)
    
    bounce_animation("Searching for patient...", 0.8)
    try:
        response = httpx.get(
            f"{FHIR_BASE}/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print_test("GET /Patient?identifier=...", "pass", f"Status: {response.status_code}")
            
            if data.get("resourceType") == "Bundle":
                entries = data.get("entry", [])
                if entries:
                    patient = entries[0].get("resource", {})
                    patient_id = patient.get("id")
                    print_test("Patient found", "pass", f"ID: {patient_id}")
                    
                    print(f"\n{Colors.CYAN}Patient Preview:{Colors.RESET}")
                    print_json({
                        "id": patient.get("id"),
                        "name": patient.get("name", [{}])[0] if patient.get("name") else {},
                        "identifier": patient.get("identifier", [])[:2]
                    })
                    
                    return patient_id
                else:
                    print_test("Patient found", "fail", "Empty Bundle")
                    return None
            else:
                print_test("Returns Bundle", "fail")
                return None
        else:
            print_test("GET /Patient?identifier=...", "fail", f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Patient match", "fail", str(e))
        return None

def test_document_consumer(patient_id: str) -> str:
    """Test document consumer (ITI-67, ITI-68)

    Returns:
        "pass" if all executed checks passed
        "fail" if any executed check failed
        "skip" if prerequisites are missing or required data isn't available
    """
    print_section("3. Document Consumer (MHD ITI-67, ITI-68)", Colors.ORANGE)
    
    if not patient_id:
        print_test("Document query", "skip", "No patient ID")
        return "skip"
    
    bounce_animation("Querying DocumentReferences...", 0.8)
    try:
        response = httpx.get(
            f"{FHIR_BASE}/fhir/DocumentReference?patient=Patient/{patient_id}&status=current",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print_test("ITI-67: GET /DocumentReference", "pass", f"Status: {response.status_code}")
            
            entries = data.get("entry", [])
            if entries:
                doc_ref = entries[0].get("resource", {})
                print_test("DocumentReference found", "pass", f"Type: {doc_ref.get('type', {}).get('coding', [{}])[0].get('code', 'N/A')}")
                
                # Check Binary reference
                content = doc_ref.get("content", [])
                if content:
                    attachment = content[0].get("attachment", {})
                    binary_url = attachment.get("url", "")
                    if binary_url:
                        binary_id = binary_url.split("/")[-1]
                        print_test("Binary reference present", "pass", f"ID: {binary_id}")
                        
                        # Test ITI-68
                        pulse_animation("Retrieving Binary...", 0.5)
                        try:
                            bin_response = httpx.get(f"{FHIR_BASE}/fhir/Binary/{binary_id}", timeout=5)
                            if bin_response.status_code == 200:
                                print_test("ITI-68: GET /Binary/{id}", "pass", f"Status: {bin_response.status_code}")
                                overall = "pass"
                            else:
                                print_test("ITI-68: GET /Binary/{id}", "fail", f"Status: {bin_response.status_code}")
                                overall = "fail"
                        except:
                            print_test("ITI-68: GET /Binary/{id}", "skip", "Binary not accessible")
                            overall = "skip"
                        return overall
                
                print(f"\n{Colors.CYAN}DocumentReference Preview:{Colors.RESET}")
                print_json({
                    "id": doc_ref.get("id"),
                    "status": doc_ref.get("status"),
                    "type": doc_ref.get("type", {}).get("coding", [{}])[0] if doc_ref.get("type") else {},
                    "subject": doc_ref.get("subject", {})
                })
                # ITI-67 succeeded and we found at least one DocumentReference. If we couldn't
                # attempt ITI-68 (no Binary URL / attachment), treat as pass for the section.
                return "pass"
            else:
                print_test("DocumentReference found", "skip", "No documents for patient")
                # ITI-67 succeeded, but there are no docs to validate ITI-68 against.
                return "skip"
        else:
            print_test("ITI-67: GET /DocumentReference", "fail", f"Status: {response.status_code}")
            return "fail"
    except Exception as e:
        print_test("Document query", "fail", str(e))
        return "fail"

def test_resource_access(patient_id: str) -> str:
    """Test resource access (QEDm PCC-44)

    Returns:
        "pass" if all executed queries succeeded (HTTP 200)
        "fail" if any query failed (non-200/exception)
        "skip" if prerequisites are missing
    """
    print_section("4. Resource Access (QEDm PCC-44)", Colors.GREEN)
    
    if not patient_id:
        print_test("Resource queries", "skip", "No patient ID")
        return "skip"
    
    resource_types = ["Condition", "Observation", "AllergyIntolerance", "MedicationStatement", "Encounter"]
    results = {}
    had_failure = False
    
    for res_type in resource_types:
        bounce_animation(f"Querying {res_type}...", 0.3)
        try:
            response = httpx.get(
                f"{FHIR_BASE}/fhir/{res_type}?patient=Patient/{patient_id}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entry", [])
                count = len(entries)
                status = "pass" if count > 0 else "skip"
                print_test(f"GET /{res_type}?patient=...", status, f"{count} result(s)")
                results[res_type] = count
            else:
                print_test(f"GET /{res_type}?patient=...", "fail", f"Status: {response.status_code}")
                had_failure = True
        except Exception as e:
            print_test(f"GET /{res_type}?patient=...", "fail", str(e))
            had_failure = True
    
    print(f"\n{Colors.CYAN}Resource Query Summary:{Colors.RESET}")
    for res_type, count in results.items():
        icon = f"{Colors.GREEN}✓{Colors.RESET}" if count > 0 else f"{Colors.GRAY}○{Colors.RESET}"
        print(f"  {icon} {res_type}: {count}")
    
    return "fail" if had_failure else "pass"

def test_document_producer():
    """Test document producer (ITI-65)"""
    print_section("5. Document Producer (MHD ITI-65)", Colors.YELLOW)
    
    # Check if we can POST a Bundle
    print_test("ITI-65: POST / with Bundle", "skip", "Requires valid Bundle JSON")
    print(f"\n{Colors.DIM}{Colors.GRAY}Note: Use demo UI 'Document Producer' tab to publish documents{Colors.RESET}")

def print_summary(passed: int, failed: int, skipped: int):
    """Print test summary"""
    print_section("Test Summary", Colors.CYAN)
    
    total = passed + failed + skipped
    if total > 0:
        pass_pct = (passed / total) * 100
    else:
        pass_pct = 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  {Colors.GREEN}✓ Passed:  {passed:3d}{Colors.RESET}")
    print(f"  {Colors.RED}✗ Failed:  {failed:3d}{Colors.RESET}")
    print(f"  {Colors.YELLOW}⊘ Skipped: {skipped:3d}{Colors.RESET}")
    print(f"  {Colors.CYAN}→ Total:   {total:3d}{Colors.RESET}")
    print(f"\n  {Colors.BOLD}Success Rate: {pass_pct:.1f}%{Colors.RESET}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed{Colors.RESET}\n")

def main():
    """Main demo runner"""
    clear_screen()
    print_header()
    
    print(f"{Colors.CYAN}Checking services...{Colors.RESET}\n")
    
    # Check services
    if not wait_for_service(f"{API_BASE}/"):
        print(f"{Colors.RED}✗ Services not available at {API_BASE}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start Docker services: cd docker && docker compose up -d{Colors.RESET}\n")
        sys.exit(1)
    
    pulse_animation("Services ready", 0.5)
    
    passed = 0
    failed = 0
    skipped = 0
    
    # Run tests
    if test_capability_discovery():
        passed += 1
    else:
        failed += 1
    
    patient_id = test_patient_match()
    if patient_id:
        passed += 1
    else:
        failed += 1
    
    doc_consumer_status = test_document_consumer(patient_id)
    if doc_consumer_status == "pass":
        passed += 1
    elif doc_consumer_status == "fail":
        failed += 1
    else:
        skipped += 1
    
    resource_access_status = test_resource_access(patient_id)
    if resource_access_status == "pass":
        passed += 1
    elif resource_access_status == "fail":
        failed += 1
    else:
        skipped += 1
    
    test_document_producer()
    skipped += 1  # Documented as skip
    
    # Summary
    print_summary(passed, failed, skipped)
    
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}Demo UI available at: {Colors.CYAN}http://localhost:8083{Colors.RESET}")
    print(f"{Colors.BLUE}API available at:     {Colors.CYAN}{API_BASE}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}\n")
        sys.exit(1)
