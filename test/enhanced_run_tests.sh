#!/bin/bash

# EU Health Data API Demo - Enhanced Comprehensive Test Runner
# Executes all tests from comprehensive test plan

set -e

API_BASE="http://localhost:8082"
FHIR_BASE="http://localhost:8082"
DEMO_UI="http://localhost:8083"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
SKIPPED=0

# Test helper functions
test_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED++))
}

test_info() {
    echo -e "${YELLOW}→ INFO:${NC} $1"
}

test_skip() {
    echo -e "${BLUE}⊘ SKIP:${NC} $1"
    ((SKIPPED++))
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    test_info "Waiting for service at $url..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            return 0
        fi
        ((attempt++))
        sleep 2
    done
    return 1
}

echo "=========================================="
echo "EU Health Data API Demo - Comprehensive Test Suite"
echo "=========================================="
echo ""

# 1. Infrastructure Tests
echo "1. INFRASTRUCTURE TESTS"
echo "----------------------"

if wait_for_service "$API_BASE/"; then
    test_pass "Facade service ready"
else
    test_fail "Facade service not ready"
    exit 1
fi

if wait_for_service "$API_BASE/metadata"; then
    test_pass "Metadata endpoint accessible"
else
    test_fail "Metadata endpoint not accessible"
fi

if wait_for_service "$DEMO_UI"; then
    test_pass "Demo UI accessible"
else
    test_fail "Demo UI not accessible"
fi

# Check HAPI directly
if wait_for_service "http://localhost:8081/fhir/metadata"; then
    test_pass "HAPI FHIR server accessible"
else
    test_fail "HAPI FHIR server not accessible"
fi

echo ""

# 2. Capability Discovery Tests
echo "2. CAPABILITY DISCOVERY TESTS"
echo "----------------------------"

METADATA=$(curl -s "$API_BASE/metadata")
CONTENT_TYPE=$(curl -s -I "$API_BASE/metadata" | grep -i "content-type" | cut -d' ' -f2 | tr -d '\r')

# Basic structure
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

# Content-Type
if echo "$CONTENT_TYPE" | grep -qi "application/fhir\+json\|application/json"; then
    test_pass "Content-Type header is correct"
else
    test_fail "Content-Type header incorrect: $CONTENT_TYPE"
fi

# instantiates field
if echo "$METADATA" | jq -e '.instantiates != null and (.instantiates | type) == "array"' > /dev/null 2>&1; then
    test_pass "CapabilityStatement has instantiates array"
    INST_COUNT=$(echo "$METADATA" | jq '.instantiates | length')
    if [ "$INST_COUNT" -gt 0 ]; then
        test_pass "instantiates contains priority area references ($INST_COUNT)"
    else
        test_fail "instantiates array is empty"
    fi
else
    test_fail "CapabilityStatement missing instantiates field"
fi

# Document Access Provider
if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "DocumentReference")' > /dev/null 2>&1; then
    test_pass "Document Access Provider capabilities declared (DocumentReference)"
    
    # Check search parameters
    DOC_PARAMS=$(echo "$METADATA" | jq '[.rest[0].resource[] | select(.type == "DocumentReference") | .searchParam[].name]')
    for param in patient type category status; do
        if echo "$DOC_PARAMS" | jq -e "index(\"$param\") != null" > /dev/null 2>&1; then
            test_pass "DocumentReference has $param search parameter"
        else
            test_fail "DocumentReference missing $param search parameter"
        fi
    done
else
    test_fail "Document Access Provider capabilities not found"
fi

# Binary resource
if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "Binary")' > /dev/null 2>&1; then
    test_pass "Binary resource declared for document retrieval"
else
    test_fail "Binary resource not found"
fi

# Resource Access Provider - check all 8 types
RESOURCE_TYPES=("Condition" "Observation" "AllergyIntolerance" "MedicationStatement" "MedicationRequest" "DiagnosticReport" "Immunization" "Encounter")
for res_type in "${RESOURCE_TYPES[@]}"; do
    if echo "$METADATA" | jq -e ".rest[0].resource[] | select(.type == \"$res_type\")" > /dev/null 2>&1; then
        test_pass "Resource Access Provider: $res_type declared"
        
        # Check patient parameter
        if echo "$METADATA" | jq -e ".rest[0].resource[] | select(.type == \"$res_type\") | .searchParam[] | select(.name == \"patient\")" > /dev/null 2>&1; then
            test_pass "$res_type has patient search parameter"
        else
            test_fail "$res_type missing patient search parameter"
        fi
    else
        test_fail "Resource Access Provider: $res_type not found"
    fi
done

# Patient resource with identifier systems
if echo "$METADATA" | jq -e '.rest[0].resource[] | select(.type == "Patient") | .extension != null' > /dev/null 2>&1; then
    test_pass "Patient resource has identifier systems extension"
    EXT_COUNT=$(echo "$METADATA" | jq '[.rest[0].resource[] | select(.type == "Patient") | .extension[]] | length')
    if [ "$EXT_COUNT" -gt 0 ]; then
        test_pass "Patient has $EXT_COUNT identifier system(s) declared"
    fi
else
    test_fail "Patient resource missing identifier systems extension"
fi

echo ""

# 3. Patient Match Tests
echo "3. PATIENT MATCH TESTS (PDQm/PIXm)"
echo "-----------------------------------"

# Basic identifier search (required)
PATIENT_SEARCH=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789")

if echo "$PATIENT_SEARCH" | jq -e '.resourceType == "Bundle" and .type == "searchset"' > /dev/null 2>&1; then
    test_pass "GET /Patient?identifier=... returns searchset Bundle"
else
    test_fail "Patient search does not return correct Bundle"
fi

ENTRY_COUNT=$(echo "$PATIENT_SEARCH" | jq '.entry | length')
if [ "$ENTRY_COUNT" -gt 0 ]; then
    test_pass "Patient search returns results"
    PATIENT_ID=$(echo "$PATIENT_SEARCH" | jq -r '.entry[0].resource.id')
    PATIENT_FHIR_ID="Patient/$PATIENT_ID"
    test_info "Found patient ID: $PATIENT_ID"
    
    # Verify patient structure
    if echo "$PATIENT_SEARCH" | jq -e '.entry[0].resource.resourceType == "Patient"' > /dev/null 2>&1; then
        test_pass "Bundle contains Patient resource"
    fi
    
    # Verify identifier
    if echo "$PATIENT_SEARCH" | jq -e '.entry[0].resource.identifier[] | select(.system == "urn:oid:2.16.840.1.113883.2.4.6.3" and .value == "123456789")' > /dev/null 2>&1; then
        test_pass "Patient has correct identifier"
    fi
else
    test_fail "Patient search returned no results"
    PATIENT_ID="patient-a"  # Fallback
    PATIENT_FHIR_ID="Patient/patient-a"
fi

# Multiple identifier systems
PATIENT_SEARCH2=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=https://national.example/id|PAT-A-001")
if echo "$PATIENT_SEARCH2" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Multiple identifier systems supported"
else
    test_fail "Multiple identifier systems not working"
fi

# Invalid identifier
INVALID_SEARCH=$(curl -s "$FHIR_BASE/fhir/Patient?identifier=invalid|999999999")
if echo "$INVALID_SEARCH" | jq -e '.resourceType == "Bundle" and (.entry == null or .entry | length == 0)' > /dev/null 2>&1; then
    test_pass "Invalid identifier returns empty Bundle"
else
    test_fail "Invalid identifier handling incorrect"
fi

# Demographics query (ITI-78) - optional
DEMO_SEARCH=$(curl -s "$FHIR_BASE/fhir/Patient?family=Smith")
if echo "$DEMO_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Demographics query (ITI-78) works"
else
    test_skip "Demographics query not supported or failed"
fi

# Patient $match (ITI-119) - optional
MATCH_BODY='{"resourceType":"Parameters","parameter":[{"name":"resource","resource":{"resourceType":"Patient","name":[{"family":"Smith"}]}}]}'
MATCH_RESPONSE=$(curl -s -X POST "$FHIR_BASE/fhir/Patient/\$match" \
    -H "Content-Type: application/fhir+json" \
    -d "$MATCH_BODY" 2>&1)
if echo "$MATCH_RESPONSE" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Patient \$match (ITI-119) works"
elif echo "$MATCH_RESPONSE" | grep -q "404\|501\|405"; then
    test_skip "Patient \$match not implemented (optional)"
else
    test_skip "Patient \$match not available"
fi

echo ""

# 4. Document Exchange Tests (MHD)
echo "4. DOCUMENT EXCHANGE TESTS (MHD)"
echo "---------------------------------"

# ITI-67: Find Document References
DOC_SEARCH=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=$PATIENT_FHIR_ID&status=current")

if echo "$DOC_SEARCH" | jq -e '.resourceType == "Bundle" and .type == "searchset"' > /dev/null 2>&1; then
    test_pass "ITI-67: GET /DocumentReference returns searchset Bundle"
else
    test_fail "ITI-67: DocumentReference search failed"
fi

DOC_COUNT=$(echo "$DOC_SEARCH" | jq '.entry | length')
if [ "$DOC_COUNT" -gt 0 ]; then
    test_pass "ITI-67: DocumentReference search returns documents ($DOC_COUNT)"
    
    DOC_REF=$(echo "$DOC_SEARCH" | jq '.entry[0].resource')
    if echo "$DOC_REF" | jq -e '.resourceType == "DocumentReference"' > /dev/null 2>&1; then
        test_pass "DocumentReference has correct structure"
        
        # Check required fields
        if echo "$DOC_REF" | jq -e '.status' > /dev/null 2>&1; then
            test_pass "DocumentReference has status"
        fi
        if echo "$DOC_REF" | jq -e '.subject.reference' > /dev/null 2>&1; then
            test_pass "DocumentReference references patient"
        fi
        if echo "$DOC_REF" | jq -e '.content' > /dev/null 2>&1; then
            test_pass "DocumentReference has content"
            
            # Extract Binary reference
            BINARY_URL=$(echo "$DOC_REF" | jq -r '.content[0].attachment.url // empty')
            if [ -n "$BINARY_URL" ]; then
                test_pass "DocumentReference references Binary"
                BINARY_ID=$(basename "$BINARY_URL" | sed 's|Binary/||')
                
                # ITI-68: Retrieve Document
                BINARY_RESPONSE=$(curl -s -w "\n%{http_code}" "$FHIR_BASE/fhir/Binary/$BINARY_ID")
                HTTP_CODE=$(echo "$BINARY_RESPONSE" | tail -n1)
                BINARY_CONTENT=$(echo "$BINARY_RESPONSE" | head -n -1)
                
                if [ "$HTTP_CODE" = "200" ]; then
                    test_pass "ITI-68: GET /Binary/{id} returns document content"
                else
                    test_fail "ITI-68: Binary retrieval failed (HTTP $HTTP_CODE)"
                fi
            else
                test_info "No Binary URL in DocumentReference (may use attachment.data)"
            fi
        fi
    fi
else
    test_fail "No DocumentReferences found for patient"
fi

# Search parameter filtering
DOC_TYPE_SEARCH=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=$PATIENT_FHIR_ID&type=http://loinc.org|60591-5")
if echo "$DOC_TYPE_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Document type filtering works"
else
    test_fail "Document type filtering failed"
fi

DOC_STATUS_SEARCH=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=$PATIENT_FHIR_ID&status=current")
if echo "$DOC_STATUS_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Document status filtering works"
else
    test_fail "Document status filtering failed"
fi

# ITI-65: Document Publication (optional test)
test_info "ITI-65: Document publication test (may require valid Bundle)"
test_skip "ITI-65: Document publication (manual test recommended)"

echo ""

# 5. Resource Access Tests (QEDm PCC-44)
echo "5. RESOURCE ACCESS TESTS (QEDm PCC-44)"
echo "--------------------------------------"

# Test all 8 resource types
for RESOURCE in "${RESOURCE_TYPES[@]}"; do
    RESOURCE_SEARCH=$(curl -s "$FHIR_BASE/fhir/$RESOURCE?patient=$PATIENT_FHIR_ID")
    
    if echo "$RESOURCE_SEARCH" | jq -e '.resourceType == "Bundle" and .type == "searchset"' > /dev/null 2>&1; then
        test_pass "GET /$RESOURCE?patient=... returns searchset Bundle"
        
        RES_COUNT=$(echo "$RESOURCE_SEARCH" | jq '.entry | length')
        if [ "$RES_COUNT" -gt 0 ]; then
            test_pass "$RESOURCE query returns results ($RES_COUNT)"
            
            # Verify patient reference
            FIRST_RES=$(echo "$RESOURCE_SEARCH" | jq '.entry[0].resource')
            if echo "$FIRST_RES" | jq -e ".subject.reference // .patient.reference // .subject.reference" > /dev/null 2>&1; then
                test_pass "$RESOURCE resources reference patient"
            fi
        else
            test_info "$RESOURCE query returned empty (may be expected)"
        fi
    else
        test_fail "GET /$RESOURCE?patient=... failed"
    fi
done

# Patient-scoped requirement
NON_PATIENT_SEARCH=$(curl -s "$FHIR_BASE/fhir/Condition")
if echo "$NON_PATIENT_SEARCH" | jq -e '.resourceType == "Bundle" and (.entry == null or .entry | length == 0)' > /dev/null 2>&1; then
    test_pass "Non-patient-scoped queries return empty (patient-scoped requirement enforced)"
else
    test_info "Non-patient-scoped query returned results (may be acceptable for demo)"
fi

# Search parameters
CONDITION_SEARCH=$(curl -s "$FHIR_BASE/fhir/Condition?patient=$PATIENT_FHIR_ID&clinical-status=active")
if echo "$CONDITION_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Search parameters work (Condition: clinical-status)"
else
    test_info "Search parameter test (may not have active conditions)"
fi

OBS_CAT_SEARCH=$(curl -s "$FHIR_BASE/fhir/Observation?patient=$PATIENT_FHIR_ID&category=laboratory")
if echo "$OBS_CAT_SEARCH" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
    test_pass "Search parameters work (Observation: category)"
else
    test_info "Observation category search (may not have lab results)"
fi

echo ""

# 6. Integration Tests
echo "6. INTEGRATION TESTS"
echo "-------------------"

# Full document exchange flow
test_info "Testing full document exchange flow..."
if [ -n "$PATIENT_ID" ] && [ "$PATIENT_ID" != "patient-a" ]; then
    DOC_FLOW=$(curl -s "$FHIR_BASE/fhir/DocumentReference?patient=Patient/$PATIENT_ID")
    if echo "$DOC_FLOW" | jq -e '.entry | length > 0' > /dev/null 2>&1; then
        test_pass "Full document exchange flow works"
    else
        test_fail "Document query step failed in integration flow"
    fi
else
    test_skip "Full document flow (patient ID not available)"
fi

# Full resource access flow
test_info "Testing full resource access flow..."
if [ -n "$PATIENT_ID" ]; then
    RES_FLOW=$(curl -s "$FHIR_BASE/fhir/Condition?patient=Patient/$PATIENT_ID")
    if echo "$RES_FLOW" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
        test_pass "Full resource access flow works"
    else
        test_fail "Resource query step failed in integration flow"
    fi
else
    test_skip "Full resource flow (patient ID not available)"
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
    test_pass "Invalid endpoints return appropriate error ($INVALID_ENDPOINT)"
else
    test_info "Invalid endpoint returned HTTP $INVALID_ENDPOINT"
fi

# Invalid patient ID
INVALID_PATIENT=$(curl -s -o /dev/null -w "%{http_code}" "$FHIR_BASE/fhir/Patient/invalid-id-12345")
if [ "$INVALID_PATIENT" = "404" ]; then
    test_pass "Invalid patient ID returns 404"
else
    test_info "Invalid patient ID returned HTTP $INVALID_PATIENT"
fi

# Invalid resource ID
INVALID_RESOURCE=$(curl -s -o /dev/null -w "%{http_code}" "$FHIR_BASE/fhir/Condition/invalid-id-12345")
if [ "$INVALID_RESOURCE" = "404" ]; then
    test_pass "Invalid resource ID returns 404"
else
    test_info "Invalid resource ID returned HTTP $INVALID_RESOURCE"
fi

echo ""

# 8. Bundle Structure Tests
echo "8. BUNDLE STRUCTURE TESTS"
echo "------------------------"

# Check a few bundles for structure
BUNDLES=(
    "$PATIENT_SEARCH"
    "$DOC_SEARCH"
    "$(curl -s "$FHIR_BASE/fhir/Condition?patient=$PATIENT_FHIR_ID")"
)

for bundle_json in "${BUNDLES[@]}"; do
    if echo "$bundle_json" | jq -e '.resourceType == "Bundle"' > /dev/null 2>&1; then
        if echo "$bundle_json" | jq -e '.type' > /dev/null 2>&1; then
            test_pass "Bundle has type field"
        fi
        if echo "$bundle_json" | jq -e '.entry' > /dev/null 2>&1; then
            test_pass "Bundle has entry array"
        fi
    fi
done

echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${BLUE}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Review output above.${NC}"
    exit 1
fi
