#!/bin/bash

# Structural validation tests - can run without Docker
# Validates code structure, configuration, and file presence

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

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

echo "=========================================="
echo "EU Health Data API Demo - Structure Validation"
echo "=========================================="
echo ""

# Check required files exist
echo "1. FILE STRUCTURE VALIDATION"
echo "---------------------------"

REQUIRED_FILES=(
    "/workspace/docker/compose.yml"
    "/workspace/services/facade/main.py"
    "/workspace/services/facade/Dockerfile"
    "/workspace/services/demo-ui/index.html"
    "/workspace/services/demo-ui/app.js"
    "/workspace/services/demo-ui/Dockerfile"
    "/workspace/services/seed/seed.py"
    "/workspace/services/seed/Dockerfile"
    "/workspace/config/config.yaml"
    "/workspace/examples/patient_a.json"
    "/workspace/examples/patient_b.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "File exists: $file"
    else
        test_fail "File missing: $file"
    fi
done

echo ""

# Validate Docker Compose
echo "2. DOCKER COMPOSE VALIDATION"
echo "---------------------------"

if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    cd /workspace/docker
    if docker compose config -q 2>/dev/null || docker-compose config -q 2>/dev/null; then
        test_pass "Docker Compose file is valid"
    else
        test_fail "Docker Compose file has errors"
    fi
    cd - > /dev/null
else
    test_info "Docker not available - skipping compose validation"
fi

echo ""

# Validate Python syntax
echo "3. PYTHON SYNTAX VALIDATION"
echo "--------------------------"

if command -v python3 &> /dev/null; then
    if python3 -m py_compile /workspace/services/facade/main.py 2>/dev/null; then
        test_pass "Facade Python syntax is valid"
    else
        test_fail "Facade Python syntax errors"
    fi
    
    if python3 -m py_compile /workspace/services/seed/seed.py 2>/dev/null; then
        test_pass "Seed Python syntax is valid"
    else
        test_fail "Seed Python syntax errors"
    fi
else
    test_info "Python3 not available - skipping syntax validation"
fi

echo ""

# Validate YAML
echo "4. YAML VALIDATION"
echo "-----------------"

if command -v python3 &> /dev/null; then
    python3 << 'EOF'
import yaml
import sys

try:
    with open('/workspace/config/config.yaml', 'r') as f:
        yaml.safe_load(f)
    print("✓ PASS: Config YAML is valid")
except Exception as e:
    print(f"✗ FAIL: Config YAML error: {e}")
    sys.exit(1)
EOF
    if [ $? -eq 0 ]; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
else
    test_info "Python3 not available - skipping YAML validation"
fi

echo ""

# Validate JSON examples
echo "5. JSON EXAMPLE VALIDATION"
echo "--------------------------"

if command -v jq &> /dev/null || command -v python3 &> /dev/null; then
    for json_file in /workspace/examples/*.json; do
        if [ -f "$json_file" ]; then
            if command -v jq &> /dev/null; then
                if jq empty "$json_file" 2>/dev/null; then
                    test_pass "JSON valid: $(basename $json_file)"
                else
                    test_fail "JSON invalid: $(basename $json_file)"
                fi
            elif command -v python3 &> /dev/null; then
                if python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
                    test_pass "JSON valid: $(basename $json_file)"
                else
                    test_fail "JSON invalid: $(basename $json_file)"
                fi
            fi
        fi
    done
else
    test_info "jq or python3 not available - skipping JSON validation"
fi

echo ""

# Check for IG alignment in code
echo "6. IG ALIGNMENT VALIDATION"
echo "-------------------------"

# Check facade for IG keywords
if grep -q "instantiates" /workspace/services/facade/main.py; then
    test_pass "Facade uses 'instantiates' for priority areas"
else
    test_fail "Facade missing 'instantiates' implementation"
fi

if grep -q "MHD ITI-67\|ITI-68\|ITI-65" /workspace/services/facade/main.py; then
    test_pass "Facade references MHD transactions"
else
    test_fail "Facade missing MHD transaction references"
fi

if grep -q "QEDm\|PCC-44" /workspace/services/facade/main.py; then
    test_pass "Facade references QEDm transactions"
else
    test_fail "Facade missing QEDm transaction references"
fi

if grep -q "PDQm\|PIXm" /workspace/services/facade/main.py; then
    test_pass "Facade references PDQm/PIXm"
else
    test_fail "Facade missing PDQm/PIXm references"
fi

# Check no admin endpoints
if grep -q "admin/import\|admin/export" /workspace/services/facade/main.py; then
    test_fail "Facade still contains admin endpoints (should be removed)"
else
    test_pass "Facade does not contain admin endpoints"
fi

echo ""

# Check config structure
echo "7. CONFIGURATION VALIDATION"
echo "--------------------------"

if grep -q "supported_priority_areas" /workspace/config/config.yaml; then
    test_pass "Config has priority areas"
else
    test_fail "Config missing priority areas"
fi

if grep -q "interfaces:" /workspace/config/config.yaml; then
    test_pass "Config has interfaces section"
else
    test_fail "Config missing interfaces section"
fi

if grep -q "supported_identifier_systems" /workspace/config/config.yaml; then
    test_pass "Config has identifier systems"
else
    test_fail "Config missing identifier systems"
fi

echo ""

# Summary
echo "=========================================="
echo "VALIDATION SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All validations passed!${NC}"
    exit 0
else
    echo -e "${RED}Some validations failed.${NC}"
    exit 1
fi
