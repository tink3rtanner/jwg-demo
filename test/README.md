# Test Suite for EU Health Data API Demo

This directory contains a comprehensive test plan and execution scripts for validating the EU Health Data API demo implementation.

## Test Files

### 1. `test_plan.md`
Complete test plan covering all aspects of the implementation:
- Infrastructure tests
- Capability Discovery
- Patient Match (PDQm/PIXm)
- Document Exchange (MHD)
- Resource Access (QEDm)
- Integration tests
- Error handling

### 2. `run_tests.sh` ⚡
**Automated runtime test script** - Executes all API tests when services are running.

**Requirements:**
- Docker services running
- `curl` command available
- `jq` command available (for JSON parsing)

**Usage:**
```bash
# Start services first
cd ../docker
docker compose up -d
# Wait ~30 seconds for services to start

# Run tests
cd ../test
./run_tests.sh
```

**Output:**
- Colored pass/fail indicators
- Detailed test results
- Summary with pass/fail counts

### 3. `validate_structure.sh` ✅
**Structure validation script** - Validates code without requiring running services.

**Requirements:**
- Python3 (for syntax validation)
- Optional: Docker (for compose validation)
- Optional: jq (for JSON validation)

**Usage:**
```bash
./validate_structure.sh
```

**Validates:**
- All required files exist
- Python syntax is correct
- YAML/JSON files are valid
- IG alignment (keywords, no admin endpoints)
- Configuration structure

### 4. `MANUAL_TEST_CHECKLIST.md` 📋
**Step-by-step manual testing guide** for browser and curl-based testing.

**Use when:**
- You want to test interactively
- You need to verify UI functionality
- You want to understand the flows step-by-step

**Includes:**
- Browser UI testing steps
- curl command examples
- Expected results for each test
- Integration flow verification

### 5. `TEST_EXECUTION_SUMMARY.md`
Summary document explaining the test suite structure and execution.

## Quick Start

### Option 1: Structure Validation (No Docker)
```bash
cd /workspace/test
./validate_structure.sh
```

### Option 2: Full Runtime Tests (Docker Required)
```bash
# Terminal 1: Start services
cd /workspace/docker
docker compose up -d

# Terminal 2: Run tests
cd /workspace/test
./run_tests.sh
```

### Option 3: Manual Testing
```bash
# Start services
cd /workspace/docker
docker compose up -d

# Follow the checklist
cat /workspace/test/MANUAL_TEST_CHECKLIST.md
# Or open in browser: http://localhost:8083
```

## Test Results

### Structure Validation Results ✅
- ✅ Python syntax: Valid
- ✅ YAML config: Valid
- ✅ JSON examples: Valid
- ✅ IG alignment: Verified (instantiates, MHD, QEDm, PDQm/PIXm)
- ✅ No admin endpoints: Confirmed removed

### Runtime Tests (Execute when Docker available)
The automated test script will verify:
- Service health and connectivity
- Capability Discovery endpoint
- Patient Match functionality
- Document Exchange (MHD ITI-67, ITI-68)
- Resource Access (QEDm PCC-44)
- Integration flows
- Error handling

## Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| File Structure | 11 files | ✅ Validated |
| Python Syntax | 2 files | ✅ Validated |
| YAML Config | 1 file | ✅ Validated |
| JSON Examples | 12 files | ✅ Validated |
| IG Alignment | Keywords | ✅ Validated |
| Capability Discovery | 7 tests | ⏳ Runtime |
| Patient Match | 5 tests | ⏳ Runtime |
| Document Exchange | 4 tests | ⏳ Runtime |
| Resource Access | 8 tests | ⏳ Runtime |
| Integration | 2 flows | ⏳ Runtime |
| Error Handling | 3 tests | ⏳ Runtime |

## Expected Outcomes

When all tests pass:
- ✅ All services start successfully
- ✅ CapabilityStatement correctly declares capabilities
- ✅ Patient match works with identifier systems
- ✅ Document exchange (MHD) functional
- ✅ Resource access (QEDm) functional
- ✅ Integration flows work end-to-end
- ✅ Error handling appropriate

## Troubleshooting

### Tests fail to connect
- Ensure Docker services are running: `docker compose ps`
- Check service logs: `docker compose logs`
- Verify ports are accessible: `curl http://localhost:8082/metadata`

### Structure validation fails
- Check Python version: `python3 --version`
- Verify file paths are correct
- Check file permissions

### Manual tests don't work
- Verify services are healthy
- Check browser console for errors
- Verify seed data loaded: `curl http://localhost:8082/fhir/Patient`

## Next Steps

1. **Run structure validation** (works now):
   ```bash
   ./validate_structure.sh
   ```

2. **When Docker available, run full suite**:
   ```bash
   ./run_tests.sh
   ```

3. **Use manual checklist** for interactive verification

4. **Review test results** and address any failures
