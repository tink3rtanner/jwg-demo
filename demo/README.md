# ASCII Demo Suite (IG-Aware)

Claude-style ASCII terminal UI for running test cases against the Euridice JWG-API sandbox.

## Integration Status

**IG-Integrated**: This demo reads from `/config/config.yaml` and validates against the actual Implementation Guide structure:
- Loads transaction definitions from IG config
- Validates responses against IG profiles and requirements
- Uses test patients and endpoints from configuration
- Aligned with the repo's config-driven architecture

**Repo Integration**:
- Reads from `/config/config.yaml` (shared with facade service)
- Uses IG transaction definitions
- Can be embedded in `/services/demo-ui` or run standalone
- Ready for docker-compose integration

## Features

- 🎨 Claude-style formatted output with colors and boxes
- ✨ Cute visual bounces and animations
- 📋 Test suite covering all major transactions (T1-T5)
- 🔍 Detailed validation and error reporting
- 🎯 Interactive or batch execution modes

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run all tests (uses /config/config.yaml)

```bash
python ascii_demo.py
```

### Run with custom config

```bash
python ascii_demo.py --config /path/to/config.yaml
```

### Override base URL from config

```bash
python ascii_demo.py --base-url http://localhost:8080
```

### Run interactively (pause between tests)

```bash
python ascii_demo.py --interactive
```

### Demo mode (preview UI without server)

```bash
python ascii_demo.py --demo
```

## Test Cases

- **T1: Inspect** - CapabilityStatement validation
- **T2: Find Patient** - GET and POST patient search
- **T3: Document Access** - List and retrieve DocumentReferences
- **T4: Resource Query** - QEDM-style resource queries
- **T5: Admin Export** - Export functionality

## Integration

This demo can be:
1. Run standalone against any FHIR server
2. Integrated into the `/services/demo-ui` service
3. Used in CI/CD pipelines for smoke tests
4. Embedded in the docker-compose stack
