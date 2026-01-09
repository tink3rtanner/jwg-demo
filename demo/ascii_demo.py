#!/usr/bin/env python3
"""
Euridice JWG-API Sandbox - ASCII Demo Suite
Claude-style interactive demo with visual bounces and test case execution

STATUS: Standalone - makes HTTP requests to configurable base URL.
        Designed to integrate into /services/demo-ui once the stack is built.
        
INTEGRATION: This follows the test cases from readme.md (T1-T5) and will
             integrate with the planned docker-compose architecture.
"""

import time
import json
import sys
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import subprocess
import requests
from datetime import datetime

# ANSI color codes for Claude-style formatting
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Claude-style colors
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    GRAY = '\033[90m'
    
    # Backgrounds
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestCase:
    id: str
    name: str
    description: str
    transaction: str
    endpoint: str
    method: str = "GET"
    expected_status: int = 200
    validator: Optional[Callable] = None
    status: TestStatus = TestStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None

class ASCIIAnimator:
    """Creates cute visual bounces and animations"""
    
    @staticmethod
    def bounce_dots(count: int = 3, delay: float = 0.2):
        """Animated bouncing dots"""
        for i in range(count):
            dots = '.' * (i + 1) + ' ' * (count - i - 1)
            print(f"\r{Colors.CYAN}{dots}{Colors.RESET}", end='', flush=True)
            time.sleep(delay)
        print(f"\r{' ' * count}\r", end='', flush=True)
    
    @staticmethod
    def spinner(steps: int = 4, delay: float = 0.1):
        """Spinning animation"""
        spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        for i in range(steps):
            print(f"\r{Colors.CYAN}{spinners[i % len(spinners)]}{Colors.RESET}", end='', flush=True)
            time.sleep(delay)
        print("\r ", end='', flush=True)
    
    @staticmethod
    def success_bounce():
        """Celebratory bounce animation"""
        frames = [
            "  ✓  ",
            " ✓✓ ",
            "✓✓✓",
            " ✓✓ ",
            "  ✓  "
        ]
        for frame in frames:
            print(f"\r{Colors.GREEN}{frame}{Colors.RESET}", end='', flush=True)
            time.sleep(0.1)
        print("\r     \r", end='', flush=True)
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 40):
        """Progress bar with bounce"""
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percent = int(100 * current / total)
        return f"{Colors.CYAN}[{bar}]{Colors.RESET} {percent}%"

class DemoRunner:
    """Main demo runner with Claude-style UI"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_cases = self._load_test_cases()
        self.animator = ASCIIAnimator()
    
    def _load_test_cases(self) -> List[TestCase]:
        """Load test cases based on the spec"""
        return [
            TestCase(
                id="t1-inspect",
                name="T1: Inspect Provider Capabilities",
                description="GET /metadata returns CapabilityStatement with document/resource access",
                transaction="T1",
                endpoint="/metadata",
                method="GET",
                expected_status=200,
                validator=self._validate_capability_statement
            ),
            TestCase(
                id="t2-find-patient-get",
                name="T2: Find Patient (GET)",
                description="GET /Patient?identifier=... returns patient bundle",
                transaction="T2",
                endpoint="/Patient?identifier=urn:oid:2.16.840.1.113883.2.9.4.3.2|123456789",
                method="GET",
                expected_status=200,
                validator=self._validate_patient_bundle
            ),
            TestCase(
                id="t2-find-patient-post",
                name="T2: Find Patient (POST)",
                description="POST /Patient/_search with identifier search",
                transaction="T2",
                endpoint="/Patient/_search",
                method="POST",
                expected_status=200,
                validator=self._validate_patient_bundle
            ),
            TestCase(
                id="t3-doc-list",
                name="T3: List DocumentReferences",
                description="GET /DocumentReference?patient=... returns EPS documents",
                transaction="T3",
                endpoint="/DocumentReference?patient=Patient/1&status=current",
                method="GET",
                expected_status=200,
                validator=self._validate_document_reference_bundle
            ),
            TestCase(
                id="t3-doc-retrieve",
                name="T3: Retrieve Document Binary",
                description="GET /Binary/{id} retrieves document payload",
                transaction="T3",
                endpoint="/Binary/1",
                method="GET",
                expected_status=200,
                validator=self._validate_binary
            ),
            TestCase(
                id="t4-resource-query",
                name="T4: Query Resources (QEDM-style)",
                description="GET /Condition?patient=... returns resource bundle",
                transaction="T4",
                endpoint="/Condition?patient=Patient/1",
                method="GET",
                expected_status=200,
                validator=self._validate_resource_bundle
            ),
            TestCase(
                id="t5-export",
                name="T5: Admin Export",
                description="POST /admin/export exports patient data",
                transaction="T5",
                endpoint="/admin/export",
                method="POST",
                expected_status=200,
                validator=self._validate_export
            ),
        ]
    
    def _validate_capability_statement(self, response: requests.Response) -> tuple[bool, str]:
        """Validate CapabilityStatement response"""
        try:
            data = response.json()
            if data.get("resourceType") != "CapabilityStatement":
                return False, "Response is not a CapabilityStatement"
            if "fhirVersion" not in data:
                return False, "Missing fhirVersion"
            return True, "✓ CapabilityStatement valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_patient_bundle(self, response: requests.Response) -> tuple[bool, str]:
        """Validate Patient search bundle"""
        try:
            data = response.json()
            if data.get("resourceType") != "Bundle":
                return False, "Response is not a Bundle"
            if "entry" not in data:
                return False, "Bundle missing entries"
            return True, f"✓ Found {len(data.get('entry', []))} patient(s)"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_document_reference_bundle(self, response: requests.Response) -> tuple[bool, str]:
        """Validate DocumentReference bundle"""
        try:
            data = response.json()
            if data.get("resourceType") != "Bundle":
                return False, "Response is not a Bundle"
            return True, f"✓ Found {len(data.get('entry', []))} document(s)"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_binary(self, response: requests.Response) -> tuple[bool, str]:
        """Validate Binary resource"""
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type or 'application/fhir+json' in content_type:
                data = response.json()
                if data.get("resourceType") == "Binary":
                    return True, "✓ Binary resource retrieved"
            return True, f"✓ Binary retrieved ({len(response.content)} bytes)"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_resource_bundle(self, response: requests.Response) -> tuple[bool, str]:
        """Validate resource query bundle"""
        try:
            data = response.json()
            if data.get("resourceType") != "Bundle":
                return False, "Response is not a Bundle"
            return True, f"✓ Found {len(data.get('entry', []))} resource(s)"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_export(self, response: requests.Response) -> tuple[bool, str]:
        """Validate export response"""
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'application/zip' in content_type:
                return True, f"✓ Export ZIP retrieved ({len(response.content)} bytes)"
            elif 'application/json' in content_type:
                data = response.json()
                return True, "✓ Export response received"
            return True, "✓ Export completed"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _print_header(self):
        """Print Claude-style header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}  EURIDICE JWG-API SANDBOX - ASCII DEMO SUITE{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")
        print(f"{Colors.DIM}Base URL: {self.base_url}{Colors.RESET}\n")
    
    def _print_test_card(self, test: TestCase, index: int, total: int):
        """Print a Claude-style test card"""
        status_icon = {
            TestStatus.PENDING: f"{Colors.GRAY}○{Colors.RESET}",
            TestStatus.RUNNING: f"{Colors.CYAN}⟳{Colors.RESET}",
            TestStatus.PASSED: f"{Colors.GREEN}✓{Colors.RESET}",
            TestStatus.FAILED: f"{Colors.RED}✗{Colors.RESET}",
            TestStatus.SKIPPED: f"{Colors.YELLOW}⊘{Colors.RESET}",
        }
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─ Test {index}/{total}: {test.name}{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.RESET}  {status_icon[test.status]} {Colors.DIM}{test.description}{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.GRAY}Transaction: {test.transaction}  Method: {test.method}{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.GRAY}Endpoint: {test.endpoint}{Colors.RESET}")
        
        if test.status == TestStatus.RUNNING:
            self.animator.spinner(2, 0.15)
        
        if test.result:
            print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.GREEN}Status: {test.result.get('status_code', 'N/A')}{Colors.RESET}")
            if test.error:
                print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.RED}Error: {test.error}{Colors.RESET}")
            elif test.result.get('validation_message'):
                print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.GREEN}{test.result['validation_message']}{Colors.RESET}")
        
        print(f"{Colors.CYAN}└{Colors.RESET}")
    
    def _print_code_block(self, title: str, content: str, language: str = ""):
        """Print Claude-style code block"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}┌─ {title}{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET}")
        lines = content.split('\n')
        for line in lines[:20]:  # Limit to 20 lines
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.DIM}{line}{Colors.RESET}")
        if len(lines) > 20:
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.DIM}... ({len(lines) - 20} more lines){Colors.RESET}")
        print(f"{Colors.BLUE}└{Colors.RESET}\n")
    
    def _print_summary(self, passed: int, failed: int, total: int):
        """Print final summary with bounce"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}  SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        print(f"  {Colors.GREEN}✓ Passed: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}✗ Failed: {failed}{Colors.RESET}")
        print(f"  {Colors.GRAY}⊘ Total:  {total}{Colors.RESET}\n")
        
        if failed == 0:
            self.animator.success_bounce()
            print(f"{Colors.BOLD}{Colors.GREEN}🎉 All tests passed!{Colors.RESET}\n")
        else:
            print(f"{Colors.BOLD}{Colors.YELLOW}⚠️  Some tests failed. Check the output above.{Colors.RESET}\n")
    
    def run_test(self, test: TestCase) -> bool:
        """Run a single test case"""
        test.status = TestStatus.RUNNING
        
        try:
            url = f"{self.base_url}{test.endpoint}"
            headers = {"Accept": "application/fhir+json"}
            
            if test.method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif test.method == "POST":
                response = requests.post(url, headers=headers, json={}, timeout=5)
            else:
                raise ValueError(f"Unsupported method: {test.method}")
            
            test.result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.content)
            }
            
            # Validate status code
            if response.status_code != test.expected_status:
                test.status = TestStatus.FAILED
                test.error = f"Expected {test.expected_status}, got {response.status_code}"
                return False
            
            # Run custom validator if provided
            if test.validator:
                is_valid, message = test.validator(response)
                test.result["validation_message"] = message
                if not is_valid:
                    test.status = TestStatus.FAILED
                    test.error = message
                    return False
            
            test.status = TestStatus.PASSED
            return True
            
        except requests.exceptions.ConnectionError:
            test.status = TestStatus.FAILED
            test.error = "Connection refused - is the server running?"
            return False
        except requests.exceptions.Timeout:
            test.status = TestStatus.FAILED
            test.error = "Request timeout"
            return False
        except Exception as e:
            test.status = TestStatus.FAILED
            test.error = f"Unexpected error: {str(e)}"
            return False
    
    def run_all(self, interactive: bool = False):
        """Run all test cases"""
        self._print_header()
        
        passed = 0
        failed = 0
        total = len(self.test_cases)
        
        for i, test in enumerate(self.test_cases, 1):
            self._print_test_card(test, i, total)
            
            if interactive:
                input(f"{Colors.CYAN}Press Enter to run this test...{Colors.RESET}")
            
            result = self.run_test(test)
            
            if result:
                passed += 1
                self.animator.success_bounce()
            else:
                failed += 1
            
            self._print_test_card(test, i, total)
            
            if test.result and test.status == TestStatus.FAILED:
                # Show error details
                if test.error:
                    print(f"\n{Colors.RED}Error details:{Colors.RESET}")
                    print(f"  {test.error}\n")
            
            time.sleep(0.3)  # Small delay for visual effect
        
        self._print_summary(passed, failed, total)
        return failed == 0
    
    def run_single(self, test_id: str):
        """Run a single test by ID"""
        test = next((t for t in self.test_cases if t.id == test_id), None)
        if not test:
            print(f"{Colors.RED}Test '{test_id}' not found{Colors.RESET}")
            return False
        
        self._print_header()
        self._print_test_card(test, 1, 1)
        result = self.run_test(test)
        self._print_test_card(test, 1, 1)
        self._print_summary(1 if result else 0, 0 if result else 1, 1)
        return result

    def demo_mode(self):
        """Run in demo mode (shows UI without making requests)"""
        self._print_header()
        
        print(f"{Colors.BOLD}{Colors.CYAN}Running in DEMO MODE (no server connection){Colors.RESET}\n")
        
        for i, test in enumerate(self.test_cases, 1):
            self._print_test_card(test, i, len(self.test_cases))
            time.sleep(0.5)
            
            # Simulate test execution
            test.status = TestStatus.RUNNING
            self._print_test_card(test, i, len(self.test_cases))
            time.sleep(0.8)
            
            # Simulate success/failure
            import random
            if random.random() > 0.2:  # 80% pass rate
                test.status = TestStatus.PASSED
                test.result = {
                    "status_code": 200,
                    "validation_message": "✓ Test passed (simulated)"
                }
                self.animator.success_bounce()
            else:
                test.status = TestStatus.FAILED
                test.error = "Simulated failure (demo mode)"
            
            self._print_test_card(test, i, len(self.test_cases))
            time.sleep(0.3)
        
        passed = sum(1 for t in self.test_cases if t.status == TestStatus.PASSED)
        failed = sum(1 for t in self.test_cases if t.status == TestStatus.FAILED)
        self._print_summary(passed, failed, len(self.test_cases))

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Euridice JWG-API ASCII Demo Suite")
    parser.add_argument("--base-url", default="http://localhost:8080",
                       help="Base URL of the FHIR server")
    parser.add_argument("--test", help="Run a specific test by ID")
    parser.add_argument("--interactive", action="store_true",
                       help="Run tests interactively (pause between tests)")
    parser.add_argument("--demo", action="store_true",
                       help="Run in demo mode (shows UI without server)")
    
    args = parser.parse_args()
    
    runner = DemoRunner(base_url=args.base_url)
    
    if args.demo:
        runner.demo_mode()
        sys.exit(0)
    elif args.test:
        success = runner.run_single(args.test)
        sys.exit(0 if success else 1)
    else:
        success = runner.run_all(interactive=args.interactive)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
