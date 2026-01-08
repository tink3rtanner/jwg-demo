# ASCII Demo Integration Guide

## Standalone Usage

The ASCII demo can run independently:

```bash
# Install dependencies
pip install -r requirements.txt

# Run in demo mode (no server needed)
python demo/ascii_demo.py --demo

# Run against a server
python demo/ascii_demo.py --base-url http://localhost:8080
```

## Integration Options

### Option 1: Standalone Script
Keep it as-is in `/demo/` and call it from:
- CI/CD pipelines
- Docker health checks
- Manual testing scripts

### Option 2: Embed in Demo UI Service
Move to `/services/demo-ui/` and:
- Add as a backend endpoint: `POST /api/run-tests`
- Expose via web UI with live output streaming
- Use WebSocket for real-time test progress

### Option 3: Docker Service
Create a dedicated test service in docker-compose:

```yaml
services:
  test-runner:
    build: ./demo
    command: python ascii_demo.py --base-url http://fhir:8080
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
