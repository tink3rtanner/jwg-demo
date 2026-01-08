# EU Health Data API Demo - Comprehensive Test Plan

## Test Environment
- Docker Compose stack
- All services running on localhost
- Test data seeded via seed service
- HAPI FHIR server as backend

## Test Categories

### 1. Infrastructure Tests
- [ ] All services start successfully
- [ ] Services are healthy and reachable
- [ ] Seed data loads correctly
- [ ] PostgreSQL database accessible
- [ ] HAPI FHIR server responds to /metadata
- [ ] Facade service proxies correctly
- [ ] Demo UI serves static files
- [ ] All ports are accessible (8080, 8081, 8082, 8083)

### 2. Capability Discovery Tests
- [ ] GET /metadata returns CapabilityStatement
- [ ] CapabilityStatement has correct structure
- [ ] resourceType is "CapabilityStatement"
- [ ] fhirVersion is "4.0.1"
- [ ] instantiates field exists and is array
- [ ] instantiates references priority area capability statements
- [ ] instantiates URLs follow correct format
- [ ] Document Access Provider capabilities declared (MHD)
- [ ] Resource Access Provider capabilities declared (QEDm)
- [ ] Patient resource declared with correct interactions
- [ ] Patient resource has identifier systems extension
- [ ] Extension URL is correct for supported-identifier
- [ ] DocumentReference resource declared
- [ ] DocumentReference has all required search parameters (patient, type, category, status)
- [ ] Binary resource declared for document retrieval
- [ ] All QEDm resource types declared (8 types)
- [ ] Each resource type has patient search parameter
- [ ] Search parameters have correct types
- [ ] Documentation strings reference correct transactions (ITI-67, ITI-68, PCC-44)
- [ ] Content-Type header is application/fhir+json

### 3. Patient Match Tests (PDQm/PIXm)

#### Basic Patient Demographics Query (Required)
- [ ] GET /Patient?identifier=system|value returns Bundle
- [ ] Bundle has resourceType "Bundle"
- [ ] Bundle contains Patient resources
- [ ] Patient has correct identifier system
- [ ] Patient has correct identifier value
- [ ] Multiple identifier systems supported
- [ ] Invalid identifier returns empty Bundle (not error)
- [ ] Patient.id can be used for subsequent queries
- [ ] Patient resource has required fields (name, birthDate, etc.)

#### Mobile Patient Demographics Query (ITI-78) - Optional
- [ ] GET /Patient?family=Smith&given=John returns Bundle
- [ ] Demographics search works with family name
- [ ] Demographics search works with given name
- [ ] Demographics search works with birthdate
- [ ] Combined demographics parameters work
- [ ] Partial matches handled correctly

#### Patient Demographics Match (ITI-119) - Optional
- [ ] POST /Patient/$match accepts Parameters resource
- [ ] $match operation returns Bundle with matches
- [ ] Match scores included in response (if supported)
- [ ] Multiple candidate matches returned
- [ ] Invalid demographic data handled gracefully

### 4. Document Exchange Tests (MHD)

#### ITI-67: Find Document References
- [ ] GET /DocumentReference?patient=Patient/{id} returns Bundle
- [ ] Bundle contains DocumentReference resources
- [ ] DocumentReference has correct structure
- [ ] DocumentReference.status is "current"
- [ ] DocumentReference.type uses LOINC codes
- [ ] DocumentReference.subject references Patient
- [ ] DocumentReference.content contains attachment
- [ ] Attachment has contentType
- [ ] Attachment has url pointing to Binary
- [ ] Type filtering works: ?type=http://loinc.org|60591-5
- [ ] Status filtering works: ?status=current
- [ ] Category filtering works: ?category=REPORTS
- [ ] Combined search parameters work
- [ ] Empty results return empty Bundle (not error)
- [ ] Invalid patient ID handled correctly

#### ITI-68: Retrieve Document
- [ ] GET /Binary/{id} returns document content
- [ ] Binary resource has correct contentType
- [ ] Binary content is accessible
- [ ] Binary ID from DocumentReference works
- [ ] Invalid Binary ID returns 404
- [ ] Content-Type header matches attachment.contentType
- [ ] Binary can be retrieved directly

#### ITI-65: Provide Document Bundle (Document Publication)
- [ ] POST / with Bundle creates DocumentReference
- [ ] Bundle contains DocumentReference and Binary
- [ ] DocumentReference created successfully
- [ ] Binary created successfully
- [ ] DocumentReference links to Binary correctly
- [ ] Published document appears in ITI-67 queries
- [ ] Bundle transaction type is correct
- [ ] All required fields present in published document

### 5. Resource Access Tests (QEDm PCC-44)

#### Core Resources (All 8 types)
- [ ] GET /Condition?patient=Patient/{id} returns Bundle
- [ ] GET /Observation?patient=Patient/{id} returns Bundle
- [ ] GET /AllergyIntolerance?patient=Patient/{id} returns Bundle
- [ ] GET /MedicationStatement?patient=Patient/{id} returns Bundle
- [ ] GET /MedicationRequest?patient=Patient/{id} returns Bundle
- [ ] GET /DiagnosticReport?patient=Patient/{id} returns Bundle
- [ ] GET /Immunization?patient=Patient/{id} returns Bundle
- [ ] GET /Encounter?patient=Patient/{id} returns Bundle

#### Patient-Scoped Requirement
- [ ] All queries require patient parameter
- [ ] GET /Condition (no patient) returns empty Bundle or error
- [ ] Patient parameter format: Patient/{id} works
- [ ] Patient parameter format: {id} works (if supported)
- [ ] Invalid patient ID handled correctly

#### Search Parameters
- [ ] Condition: clinical-status parameter works
- [ ] Observation: category parameter works
- [ ] Observation: date parameter works
- [ ] MedicationStatement: status parameter works
- [ ] MedicationRequest: status parameter works
- [ ] DiagnosticReport: category parameter works
- [ ] Immunization: date parameter works
- [ ] Encounter: date parameter works
- [ ] Combined search parameters work
- [ ] Date range queries work (ge, le, etc.)

#### Resource Structure
- [ ] Each resource references patient correctly
- [ ] Resources have required fields
- [ ] Resources conform to FHIR R4 structure
- [ ] Bundle structure is correct
- [ ] Bundle.total is accurate
- [ ] Bundle.entry contains fullUrl and resource

### 6. Integration Tests

#### Full Document Exchange Flow
- [ ] Capability Discovery → verify DocumentReference in capabilities
- [ ] Patient Match → get Patient ID
- [ ] Document Query (ITI-67) → get DocumentReference
- [ ] Document Retrieve (ITI-68) → get Binary content
- [ ] Verify end-to-end flow works
- [ ] Verify data consistency across steps

#### Full Resource Access Flow
- [ ] Capability Discovery → verify resource types in capabilities
- [ ] Patient Match → get Patient ID
- [ ] Resource Queries → get multiple resource types
- [ ] Verify all resource types accessible
- [ ] Verify patient-scoped queries work
- [ ] Verify end-to-end flow works

#### Document Publication Flow
- [ ] Create Bundle with DocumentReference + Binary
- [ ] POST Bundle to publish document
- [ ] Verify document appears in queries
- [ ] Verify Binary is accessible
- [ ] Verify DocumentReference links correctly

#### Cross-Patient Tests
- [ ] Patient A has documents and resources
- [ ] Patient B has documents and resources
- [ ] Queries return correct data for each patient
- [ ] No cross-patient data leakage

### 7. Demo UI Tests
- [ ] Demo UI loads at http://localhost:8083
- [ ] All tabs are accessible
- [ ] Capability Discovery tab functional
- [ ] Patient Match tab functional
- [ ] Document Exchange tab functional
- [ ] Resource Access tab functional
- [ ] Execute buttons work
- [ ] Request/response displays correctly
- [ ] Status indicators work (success/error/pending)
- [ ] Conformance checklists update correctly
- [ ] Mermaid diagrams render
- [ ] curl commands display correctly
- [ ] JSON formatting is readable
- [ ] Patient ID flows between tabs

### 8. Error Handling Tests
- [ ] Invalid endpoints return 404
- [ ] Malformed requests return 400
- [ ] Missing required parameters handled correctly
- [ ] Invalid patient ID returns 404 or empty Bundle
- [ ] Invalid resource ID returns 404
- [ ] Invalid search parameters handled gracefully
- [ ] Malformed JSON returns 400
- [ ] Unsupported HTTP methods return 405
- [ ] Error responses include appropriate status codes
- [ ] Error messages are informative

### 9. Content-Type and Headers Tests
- [ ] GET /metadata returns application/fhir+json
- [ ] GET /fhir/* returns application/fhir+json
- [ ] POST /fhir/* accepts application/fhir+json
- [ ] Accept header respected
- [ ] Content-Type header correct in responses
- [ ] CORS headers present (if applicable)

### 10. Bundle Structure Tests
- [ ] All Bundles have resourceType "Bundle"
- [ ] All Bundles have type field
- [ ] Search result Bundles have type "searchset"
- [ ] Collection Bundles have type "collection"
- [ ] Bundle.entry array structure correct
- [ ] Bundle.entry has fullUrl
- [ ] Bundle.entry has resource
- [ ] Bundle.total accurate (if present)
- [ ] Empty Bundles have empty entry array

### 11. Profile and Extension Tests
- [ ] CapabilityStatement uses correct profiles
- [ ] Patient uses correct profile
- [ ] DocumentReference uses correct profile
- [ ] Extensions use correct URLs
- [ ] Identifier systems extension format correct
- [ ] Priority area instantiates format correct

### 12. Priority Area Tests
- [ ] EPS priority area declared in instantiates
- [ ] Instantiates URLs reference correct capability statements
- [ ] Multiple priority areas supported (if configured)
- [ ] Priority area affects available resources

### 13. Seed Data Validation
- [ ] At least 2 patients loaded
- [ ] Each patient has identifiers
- [ ] Each patient has DocumentReferences
- [ ] DocumentReferences link to Binary resources
- [ ] Each patient has associated resources
- [ ] Resources reference correct patients
- [ ] Organization and Practitioner resources loaded
- [ ] All seed data is valid FHIR

### 14. Performance and Scalability Tests
- [ ] Capability Discovery responds quickly (< 1s)
- [ ] Patient search responds quickly (< 1s)
- [ ] Document queries respond quickly (< 2s)
- [ ] Resource queries respond quickly (< 2s)
- [ ] Multiple concurrent requests handled
- [ ] No memory leaks in long-running tests

### 15. Security Tests (Basic)
- [ ] Services bind to localhost only
- [ ] No sensitive data in error messages
- [ ] CORS configured appropriately
- [ ] No admin endpoints exposed (removed per IG)
- [ ] Authorization endpoints stubbed (if auth disabled)

## Test Execution Order
1. Infrastructure setup and health checks
2. Seed data validation
3. Capability Discovery (foundation for all other tests)
4. Patient Match (required for subsequent tests)
5. Document Exchange (ITI-67, ITI-68, ITI-65)
6. Resource Access (all 8 resource types)
7. Integration flows (end-to-end)
8. Demo UI functionality
9. Error handling
10. Content-Type and headers
11. Bundle structure validation
12. Profile and extension validation
13. Performance checks

## Test Data Requirements
- 2+ patients with different identifier systems
- DocumentReferences for each patient
- Binary resources linked to DocumentReferences
- Resources of all 8 types for each patient
- Organization and Practitioner resources
- Valid FHIR R4 structure throughout

## Success Criteria
- All infrastructure tests pass
- All capability discovery tests pass
- All patient match tests pass (required + optional)
- All document exchange tests pass (ITI-67, ITI-68, ITI-65)
- All resource access tests pass (all 8 types)
- All integration flows work end-to-end
- Demo UI fully functional
- Error handling appropriate
- All responses valid FHIR R4
- Performance acceptable

## Known Limitations (Demo)
- Authorization disabled (SMART Backend Services not implemented)
- No audit logging
- No consent management
- Limited error detail (for security)
- No bulk export ($export operation)
- No cross-border routing
