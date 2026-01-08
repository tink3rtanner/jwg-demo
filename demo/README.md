# ASCII Demo Suite

Claude-style ASCII terminal UI for running test cases against the Euridice JWG-API sandbox.

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

### Run all tests

```bash
python ascii_demo.py
```

### Run interactively (pause between tests)

```bash
python ascii_demo.py --interactive
```

### Run a specific test

```bash
python ascii_demo.py --test t1-inspect
```

### Custom base URL

```bash
python ascii_demo.py --base-url http://localhost:8080
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
