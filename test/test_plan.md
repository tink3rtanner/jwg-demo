# EU Health Data API Demo - Test Plan

## Test Environment
- Docker Compose stack
- All services running on localhost
- Test data seeded via seed service

## Test Categories

### 1. Infrastructure Tests
- [ ] All services start successfully
- [ ] Services are healthy and reachable
- [ ] Seed data loads correctly

### 2. Capability Discovery Tests
- [ ] GET /metadata returns CapabilityStatement
- [ ] CapabilityStatement has correct structure
- [ ] instantiates field references priority areas
- [ ] Document Access Provider capabilities declared (MHD)
- [ ] Resource Access Provider capabilities declared (QEDm)
- [ ] Patient resource with identifier systems extension
- [ ] FHIR version is 4.0.1

### 3. Patient Match Tests (PDQm/PIXm)
- [ ] GET /Patient?identifier=system|value returns Bundle
- [ ] Bundle contains Patient resources
- [ ] Patient has correct identifier
- [ ] Multiple identifier systems supported
- [ ] Invalid identifier returns empty Bundle
- [ ] Patient.id can be used for subsequent queries

### 4. Document Exchange Tests (MHD)
- [ ] ITI-67: GET /DocumentReference?patient=... returns Bundle
- [ ] DocumentReference has correct structure
- [ ] DocumentReference references Binary
- [ ] ITI-68: GET /Binary/{id} returns document content
- [ ] Document type filtering works (type parameter)
- [ ] Status filtering works (status=current)
- [ ] Category filtering works

### 5. Resource Access Tests (QEDm PCC-44)
- [ ] GET /Condition?patient=... returns Bundle
- [ ] GET /Observation?patient=... returns Bundle
- [ ] GET /AllergyIntolerance?patient=... returns Bundle
- [ ] GET /MedicationStatement?patient=... returns Bundle
- [ ] GET /Encounter?patient=... returns Bundle
- [ ] Patient-scoped queries work
- [ ] Non-patient-scoped queries rejected or return empty
- [ ] Search parameters work (clinical-status, category, date)

### 6. Integration Tests
- [ ] Full flow: Capability Discovery → Patient Match → Document Query → Document Retrieve
- [ ] Full flow: Capability Discovery → Patient Match → Resource Queries
- [ ] Demo UI loads and displays correctly
- [ ] All tabs in demo UI functional

### 7. Error Handling Tests
- [ ] Invalid endpoints return 404
- [ ] Malformed requests return 400
- [ ] Missing required parameters handled correctly

## Test Execution Order
1. Infrastructure setup
2. Capability Discovery
3. Patient Match
4. Document Exchange
5. Resource Access
6. Integration flows
7. Error handling
