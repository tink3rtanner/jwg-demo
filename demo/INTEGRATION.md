# ASCII Demo Integration Guide

## IG-Aware Configuration

The demo is **integrated with the repo structure**:
- Reads from `/config/config.yaml` (shared with facade service)
- Uses IG transaction definitions from config
- Validates against IG profiles and requirements
- Uses test patients and endpoints from configuration

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default config (/config/config.yaml)
python demo/ascii_demo.py

# Run with custom config
python demo/ascii_demo.py --config /path/to/config.yaml

# Override base URL
python demo/ascii_demo.py --base-url http://localhost:8080

# Demo mode (preview UI)
python demo/ascii_demo.py --demo
```

## Integration Options

### Option 1: Standalone Script (Current)
Runs from `/demo/` and reads shared config:
- CI/CD pipelines
- Docker health checks
- Manual testing scripts
- **Uses same config as facade service**

### Option 2: Embed in Demo UI Service
Move to `/services/demo-ui/` and:
- Import `IGDemRunner` class
- Add as backend endpoint: `POST /api/run-tests`
- Stream output via WebSocket
- Share config with facade via `/config/config.yaml`

### Option 3: Docker Service
Add to docker-compose:

```yaml
services:
  test-runner:
    build: ./demo
    command: python ascii_demo.py
    volumes:
      - ./config:/config:ro  # Read shared config
    depends_on:
      - fhir-server
    profiles:
      - test
```

## Extending Test Cases

Add new tests by extending the `_load_test_cases()` method:

```python
TestCase(
    id="custom-test",
    name="Custom Test",
    description="Test description",
    transaction="TX",
    endpoint="/custom/endpoint",
    method="GET",
    expected_status=200,
    validator=self._validate_custom
)
```

## Custom Validators

Validators return `(bool, str)` tuple:

```python
def _validate_custom(self, response: requests.Response) -> tuple[bool, str]:
    try:
        data = response.json()
        # Your validation logic
        return True, "✓ Validation passed"
    except Exception as e:
        return False, f"Validation error: {str(e)}"
```
