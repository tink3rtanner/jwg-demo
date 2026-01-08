# Manual Test Checklist

Use this checklist when testing the demo manually after starting Docker services.

## Prerequisites
```bash
cd docker
docker compose up -d
# Wait ~30 seconds for services to start
docker compose ps  # Verify all services are running
```

## Test Execution

### 1. Capability Discovery

- [ ] Open browser: http://localhost:8083
- [ ] Click "Capability Discovery" tab
- [ ] Click "Execute Capability Discovery" button
- [ ] Verify:
  - [ ] Status shows success (green checkmark)
  - [ ] Response shows CapabilityStatement JSON
  - [ ] CapabilityStatement has `instantiates` field
  - [ ] CapabilityStatement has DocumentReference resource
  - [ ] CapabilityStatement has Binary resource
  - [ ] CapabilityStatement has Condition/Observation resources
  - [ ] Patient resource has extension for identifier systems
  - [ ] FHIR version is 4.0.1
- [ ] Check conformance checklist items are checked

### 2. Patient Match (PDQm/PIXm)

- [ ] Click "Patient Match (PDQm/PIXm)" tab
- [ ] Enter identifier: `123456789`
- [ ] Select system: `urn:oid:2.16.840.1.113883.2.4.6.3`
- [ ] Click "Execute Patient Match"
- [ ] Verify:
  - [ ] Status shows success
  - [ ] Response shows Bundle with Patient resource
  - [ ] Patient has correct identifier
  - [ ] Patient ID is displayed (e.g., "patient-a")
- [ ] Test with different identifier system:
  - [ ] Change to: `https://national.example/id` with value `PAT-A-001`
  - [ ] Verify it works
- [ ] Test invalid identifier:
  - [ ] Use identifier: `999999999`
  - [ ] Verify returns empty Bundle (not error)

### 3. Document Exchange (MHD)

- [ ] Click "Document Exchange (MHD)" tab
- [ ] Enter Patient ID (from previous test or use: `patient-a`)
- [ ] Click "List Documents"
- [ ] Verify:
  - [ ] Status shows success
  - [ ] Response shows Bundle with DocumentReference(s)
  - [ ] DocumentReference has type, status, patient reference
  - [ ] DocumentReference has content with attachment/Binary reference
- [ ] Test document retrieval:
  - [ ] Note the Binary ID from DocumentReference
  - [ ] Manually test: `curl http://localhost:8082/fhir/Binary/{id}`
  - [ ] Verify Binary content is returned

### 4. Resource Access (QEDm)

- [ ] Click "Resource Access (QEDm)" tab
- [ ] Enter Patient ID (from previous test or use: `patient-a`)
- [ ] Click "Query Resources"
- [ ] Verify:
  - [ ] Status shows success
  - [ ] Response shows JSON with multiple resource types
  - [ ] Each resource type (Condition, Observation, etc.) has results
  - [ ] All resources reference the patient
- [ ] Test individual resource queries:
  - [ ] `curl http://localhost:8082/fhir/Condition?patient=Patient/patient-a`
  - [ ] `curl http://localhost:8082/fhir/Observation?patient=Patient/patient-a`
  - [ ] `curl http://localhost:8082/fhir/AllergyIntolerance?patient=Patient/patient-a`
  - [ ] Verify all return Bundles

### 5. Integration Flow Test

**Full Document Exchange Flow:**
- [ ] Start fresh (clear browser cache if needed)
- [ ] Execute Capability Discovery → verify DocumentReference in capabilities
- [ ] Execute Patient Match → get Patient ID
- [ ] Execute Document Query → get DocumentReference
- [ ] Retrieve Binary document
- [ ] Verify end-to-end flow works

**Full Resource Access Flow:**
- [ ] Execute Capability Discovery → verify Condition/Observation in capabilities
- [ ] Execute Patient Match → get Patient ID
- [ ] Execute Resource Queries → get multiple resource types
- [ ] Verify end-to-end flow works

### 6. Direct API Tests (curl)

```bash
# Capability Discovery
curl http://localhost:8082/metadata | jq .

# Patient Match
curl "http://localhost:8082/fhir/Patient?identifier=urn:oid:2.16.840.1.113883.2.4.6.3|123456789" | jq .

# Document Exchange (ITI-67)
curl "http://localhost:8082/fhir/DocumentReference?patient=Patient/patient-a&status=current" | jq .

# Resource Access (PCC-44)
curl "http://localhost:8082/fhir/Condition?patient=Patient/patient-a" | jq .
curl "http://localhost:8082/fhir/Observation?patient=Patient/patient-a" | jq .
```

### 7. Error Handling

- [ ] Test invalid endpoint: `curl http://localhost:8082/invalid` → should return 404
- [ ] Test missing patient parameter: `curl http://localhost:8082/fhir/Condition` → should return empty Bundle or error
- [ ] Test invalid patient ID: `curl http://localhost:8082/fhir/Patient/invalid-id` → should return 404

### 8. Seed Data Verification

- [ ] Verify seed data loaded:
  ```bash
  curl "http://localhost:8082/fhir/Patient" | jq '.entry | length'
  # Should return at least 2 patients
  
  curl "http://localhost:8082/fhir/DocumentReference" | jq '.entry | length'
  # Should return at least 2 DocumentReferences
  ```

## Expected Results Summary

✅ All capability discovery checks pass
✅ Patient match works with both identifier systems
✅ Document exchange returns DocumentReferences and allows Binary retrieval
✅ Resource access returns patient-scoped resources
✅ Integration flows work end-to-end
✅ Error handling is appropriate
✅ Seed data is loaded correctly

## Issues Found

Document any issues or unexpected behavior here:

1. 
2. 
3. 
