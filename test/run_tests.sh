#!/bin/bash

# EU Health Data API Demo - Test Runner
# Executes comprehensive test plan

set -e

API_BASE="http://localhost:8082"
FHIR_BASE="http://localhost:8082"
DEMO_UI="http://localhost:8083"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test helper functions
test_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    PASSED=$((PASSED + 1))
}

test_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    FAILED=$((FAILED + 1))
}

test_info() {
    echo -e "${YELLOW}→ INFO:${NC} $1"
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    test_info "Waiting for service at $url..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            test_pass "Service ready at $url"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    test_fail "Service not ready at $url after $max_attempts attempts"
    return 1
}

# Test JSON response structure
test_json_structure() {
    local json=$1
    local field=$2
    local expected=$3
    
    if echo "$json" | jq -e ".$field == $expected" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo "=========================================="
echo "EU Health Data API Demo - Test Suite"
echo "=========================================="
echo ""

# 1. Infrastructure Tests
echo "1. INFRASTRUCTURE TESTS"
echo "----------------------"

wait_for_service "$API_BASE/"
wait_for_service "$API_BASE/metadata"
wait_for_service "$DEMO_UI"

echo ""

# 2. Capability Discovery Tests
echo "2. CAPABILITY DISCOVERY TESTS"
echo "----------------------------"

METADATA=$(curl -s "$API_BASE/metadata")

if echo "$METADATA" | jq -e '.resourceType == "CapabilityStatement"' > /dev/null 2>&1; then
    test_pass "GET /metadata returns CapabilityStatement"
else
    test_fail "GET /metadata does not return CapabilityStatement"
fi

if echo "$METADATA" | jq -e '.fhirVersion == "4.0.1"' > /dev/null 2>&1; then
    test_pass "FHIR version is 4.0.1"
else
    test_fail "FHIR version is not 4.0.1"
fi

if echo "$METADATA" | jq -e '.instantiates != null' > /dev/null 2>&1; then
    test_pass "CapabilityStatement has instantiates field"
else
    test_fail "CapabilityStatement missing instantiates field"
fi

if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "DocumentReference")' > /dev/null 2>&1; then
    test_pass "Document Access Provider capabilities declared (DocumentReference)"
else
    test_fail "Document Access Provider capabilities not found"
fi

if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "Binary")' > /dev/null 2>&1; then
    test_pass "Binary resource declared for document retrieval"
else
    test_fail "Binary resource not found"
fi

if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "Condition")' > /dev/null 2>&1; then
    test_pass "Resource Access Provider capabilities declared (Condition)"
else
    test_fail "Resource Access Provider capabilities not found"
fi

if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "Patient") | .extension != null' > /dev/null 2>&1; then
    test_pass "Patient resource has identifier systems extension"
else
    test_fail "Patient resource missing identifier systems extension"
fi

echo ""

# 3. Patient Match Tests
echo "3. PATIENT MATCH TESTS (PDQm/PIXm)"
echo "-----------------------------------"

# Test identifier search
PATIENT_SEARCH=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789")

if echo "$PATIENT_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "GET /Patient?identifier=... returns Bundle"
else
    test_fail "Patient search does not return Bundle"
fi

ENTRY_COUNT=$(echo "$PATIENT_SEARCH" | jq '.entry | length')
if [ "$ENTRY_COUNT" -gt 0 ]; then
    test_pass "Patient search returns at least one patient"
    PATIENT_ID=$(echo "$PATIENT_SEARCH" | jq -r '.entry[0].resource.id')
    test_info "Found patient ID: $PATIENT_ID"
else
    test_fail "Patient search returned no results"
    PATIENT_ID="patient-a"  # Fallback for subsequent tests
fi

if echo "$PATIENT_SEARCH" | jq -e '.entry[0].resource.resourceType == "Patient"' > /dev/null 2>&1; then
    test_pass "Bundle contains Patient resource"
else
    test_fail "Bundle does not contain Patient resource"
fi

# Test with different identifier system
PATIENT_SEARCH2=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=https://national.example/id|PAT-A-001")
if echo "$PATIENT_SEARCH2" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Multiple identifier systems supported"
else
    test_fail "Multiple identifier systems not working"
fi

# Test invalid identifier
INVALID_SEARCH=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=invalid|999999999")
if echo "$INVALID_SEARCH" | jq -e '.resourceType == "Bundle" and (.entry == null or .entry | length == 0)' > /dev/null 2>&1; then
    test_pass "Invalid identifier returns empty Bundle"
else
    test_fail "Invalid identifier handling incorrect"
fi

echo ""

# 4. Document Exchange Tests (MHD)
echo "4. DOCUMENT EXCHANGE TESTS (MHD)"
echo "---------------------------------"

if [ -z "$PATIENT_ID" ]; then
    PATIENT_ID="patient-a"
fi

# ITI-67: Find Document References
DOC_SEARCH=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=Patient/$PATIENT_ID&status=current")

if echo "$DOC_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "ITI-67: GET /DocumentReference returns Bundle"
else
    test_fail "ITI-67: DocumentReference search failed"
fi

DOC_COUNT=$(echo "$DOC_SEARCH" | jq '.entry | length')
if [ "$DOC_COUNT" -gt 0 ]; then
    test_pass "DocumentReference search returns documents"
    
    DOC_REF=$(echo "$DOC_SEARCH" | jq -r '.entry[0].resource')
    if echo "$DOC_REF" | jq -e '.resourceType == "DocumentReference"' > /dev/null 2>&1; then
        test_pass "DocumentReference has correct structure"
    else
        test_fail "DocumentReference structure incorrect"
    fi
    
    # Extract Binary reference
    BINARY_URL=$(echo "$DOC_REF" | jq -r '.content[0].attachment.url // empty')
    if [ -n "$BINARY_URL" ]; then
        test_pass "DocumentReference references Binary"
        
        # ITI-68: Retrieve Document
        BINARY_ID=$(basename "$BINARY_URL")
        BINARY_RESPONSE=$(curl -s -w "\n%{http_code}" "$FHIR_BASE/fhir/Binary/$BINARY_ID")
        HTTP_CODE=$(echo "$BINARY_RESPONSE" | tail -n1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            test_pass "ITI-68: GET /Binary/{id} returns document content"
        else
            test_fail "ITI-68: Binary retrieval failed (HTTP $HTTP_CODE)"
        fi
    else
        test_info "No Binary URL found in DocumentReference (may be attachment-based)"
    fi
else
    test_fail "No DocumentReferences found for patient"
fi

# Test type filtering
DOC_TYPE_SEARCH=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=Patient/$PATIENT_ID&type=http://loinc.org|60591-5")
if echo "$DOC_TYPE_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Document type filtering works"
else
    test_fail "Document type filtering failed"
fi

echo ""

# 5. Resource Access Tests (QEDm PCC-44)
echo "5. RESOURCE ACCESS TESTS (QEDm PCC-44)"
echo "--------------------------------------"

if [ -z "$PATIENT_ID" ]; then
    PATIENT_ID="patient-a"
fi

# Test each resource type
for RESOURCE in Condition Observation AllergyIntolerance MedicationStatement Encounter; do
    RESOURCE_SEARCH=$(curl -s "$FHIR_BASE/fhir/$RESOURCE?patient=Patient/$PATIENT_ID")
    
    if echo "$RESOURCE_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
        test_pass "GET /$RESOURCE?patient=... returns Bundle"
        
        RES_COUNT=$(echo "$RESOURCE_SEARCH" | jq '.entry | length')
        if [ "$RES_COUNT" -gt 0 ]; then
            test_pass "$RESOURCE query returns results"
        else
            test_info "$RESOURCE query returned empty (may be expected)"
        fi
    else
        test_fail "GET /$RESOURCE?patient=... failed"
    fi
done

# Test patient-scoped requirement (non-patient query should fail or return empty)
NON_PATIENT_SEARCH=$(curl -s "$FHIR_BASE/fhir/Condition")
if echo "$NON_PATIENT_SEARCH" | jq -e '.resourceType == "Bundle" and (.entry == null or .entry | length == 0)' > /dev/null 2>&1; then
    test_pass "Non-patient-scoped queries return empty (patient-scoped requirement enforced)"
else
    test_info "Non-patient-scoped query returned results (may be acceptable for demo)"
fi

# Test search parameters
CONDITION_SEARCH=$(curl -s "$FHIR_BASE/fhir/Condition?patient=Patient/$PATIENT_ID&clinical-status=active")
if echo "$CONDITION_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Search parameters work (clinical-status)"
else
    test_fail "Search parameters not working"
fi

echo ""

# 6. Integration Tests
echo "6. INTEGRATION TESTS"
echo "-------------------"

# Full flow: Capability Discovery → Patient Match → Document Query → Document Retrieve
test_info "Testing full document exchange flow..."

METADATA_OK=0
PATIENT_OK=0

curl -s "$API_BASE/metadata" | jq -e '.resourceType == "CapabilityStatement"' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    METADATA_OK=1
    curl -s "$FHIR_BASE/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789" | jq -e '.entry | length > 0' > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        PATIENT_OK=1
        PAT_ID=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789" | jq -r '.entry[0].resource.id')
        curl -s "$FHIR_BASE/fhir/DocumentReference?patient=Patient/$PAT_ID" | jq -e '.entry | length > 0' > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            test_pass "Full document exchange flow works"
        else
            test_fail "Document query step failed in integration flow"
        fi
    else
        test_fail "Patient match step failed in integration flow"
    fi
else
    test_fail "Capability discovery step failed in integration flow"
fi

# Full flow: Capability Discovery → Patient Match → Resource Queries
test_info "Testing full resource access flow..."

if [ $METADATA_OK -eq 1 ]; then
    if [ $PATIENT_OK -eq 1 ]; then
        curl -s "$FHIR_BASE/fhir/Condition?patient=Patient/$PAT_ID" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            test_pass "Full resource access flow works"
        else
            test_fail "Resource query step failed in integration flow"
        fi
    fi
fi

# Demo UI check
UI_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$DEMO_UI")
if [ "$UI_CHECK" = "200" ]; then
    test_pass "Demo UI loads correctly"
else
    test_fail "Demo UI not accessible (HTTP $UI_CHECK)"
fi

echo ""

# 7. Error Handling Tests
echo "7. ERROR HANDLING TESTS"
echo "-----------------------"

# Invalid endpoint
INVALID_ENDPOINT=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/invalid-endpoint")
if [ "$INVALID_ENDPOINT" = "404" ] || [ "$INVALID_ENDPOINT" = "405" ]; then
    test_pass "Invalid endpoints return appropriate error"
else
    test_info "Invalid endpoint returned HTTP $INVALID_ENDPOINT (may be acceptable)"
fi

# Malformed request (missing required parameter)
MALFORMED=$(curl -s "$FHIR_BASE/fhir/DocumentReference" | jq -e '.resourceType == "Bundle"')
if [ $? -eq 0 ]; then
    test_info "Malformed request handled (may return empty Bundle)"
else
    test_info "Malformed request handling checked"
fi

echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
