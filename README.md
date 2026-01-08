# EU Health Data API Demo

A Docker-based sandbox implementation of the [EU Health Data API](https://build.fhir.org/ig/euridice-org/jwg-api/en/) specification, demonstrating the 5-actor model with document and resource exchange patterns.

## Architecture

This demo implements the following actors from the EU Health Data API IG:

1. **Document Producer** (client) - Publishes documents via MHD ITI-65
2. **Document Access Provider** (server) - Serves documents via MHD ITI-67, ITI-68
3. **Document Consumer** (client) - Queries and retrieves documents
4. **Resource Access Provider** (server) - Provides resource queries via QEDm PCC-44
5. **Resource Consumer** (client) - Queries discrete FHIR resources

## Components

- **HAPI FHIR Server** - FHIR R4 server with PostgreSQL persistence
- **Facade Service** - FastAPI service that generates IG-aligned CapabilityStatements and proxies to HAPI
- **Demo UI** - Interactive web interface demonstrating all flows
- **Seed Service** - Loads demo data (2 patients with EPS documents and resources)

## Quick Start

```bash
# Start all services
cd docker
docker compose up -d

# Wait for services to be ready (about 30 seconds)
docker compose ps

# Access the demo UI
open http://localhost:8083

# Access the FHIR API directly
curl http://localhost:8082/metadata
```

## Transactions Implemented

### Capability Discovery
- `GET /metadata` - Returns CapabilityStatement with `instantiates` for priority areas

### Patient Match (PDQm/PIXm)
- `GET /Patient?identifier=system|value` - Basic identifier search (required)
- `GET /Patient?family=...&given=...&birthdate=...` - Demographics query (optional)
- `POST /Patient/$match` - Fuzzy patient matching (optional)

### Document Exchange (MHD)
- **ITI-67**: `GET /DocumentReference?patient=...&type=...&status=current` - Find Document References
- **ITI-68**: `GET /Binary/{id}` - Retrieve Document
- **ITI-65**: `POST /` (Bundle with DocumentReference + Binary) - Publish Document

### Resource Access (QEDm)
- **PCC-44**: `GET /{ResourceType}?patient=...` - Query existing data
  - All queries must be patient-scoped
  - Read/search only (no create/update/delete)
  - Supported resources: Condition, Observation, AllergyIntolerance, MedicationStatement, MedicationRequest, DiagnosticReport, Immunization, Encounter

## Configuration

Edit `config/config.yaml` to configure:
- Priority areas (EPS, MPD, Laboratory, etc.)
- Document vs Resource access capabilities
- Supported identifier systems
- Authorization settings (SMART Backend Services)

## Demo Data

The seed service loads:
- 2 demo patients with identifiers
- EPS DocumentReferences for each patient
- Associated resources (Conditions, Observations, Allergies, Medications, Encounters)

## Ports

- `8080` - Traefik reverse proxy
- `8081` - HAPI FHIR server (direct access)
- `8082` - Facade service (API)
- `8083` - Demo UI

## Notes

- Authorization is currently disabled for demo purposes (per IG, SMART Backend Services is required in production)
- All services bind to localhost only for security
- The demo uses FHIR R4 (4.0.1)

## References

- [EU Health Data API IG](https://build.fhir.org/ig/euridice-org/jwg-api/en/)
- [IHE MHD](https://profiles.ihe.net/ITI/MHD/)
- [IHE QEDm](https://profiles.ihe.net/PCC/QEDm/)
- [IHE PDQm/PIXm](https://profiles.ihe.net/ITI/PDQm/)
- [SMART Backend Services](https://build.fhir.org/ig/HL7/smart-app-launch/backend-services.html)
