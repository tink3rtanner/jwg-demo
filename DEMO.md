# EU Health Data API Demo - Quick Start

## Run the ASCII Demo

```bash
# Make sure services are running
cd docker
docker compose up -d

# Wait ~30 seconds, then run the demo
cd ..
python3 demo_runner.py
```

### Mock Mode (No Docker Required)

Test the ASCII UI without running services:

```bash
# Success scenario - all tests pass
python3 demo_runner.py --mock

# Failure scenario - connection errors
python3 demo_runner.py --mock failure

# Mixed scenario - some pass, some fail
python3 demo_runner.py --mock mixed

# Without animations (faster)
python3 demo_runner.py --mock --no-animation
```

### Visual Testing Helper

Use the helper script to iterate on visuals:

```bash
./visual_test.sh              # Run success scenario
./visual_test.sh -f           # Failure scenario
./visual_test.sh -x           # Mixed scenario
./visual_test.sh -a           # Run all scenarios
./visual_test.sh -w           # Watch mode (re-run on changes)
./visual_test.sh -n           # No animations
```

## What You'll See

The demo runner shows:
- ✨ Bouncing animations and wave effects
- 🎨 Claude Code-style colors (orange accent)
- 📊 Test results with visual indicators (✓ ✗ ⊘)
- 📋 JSON previews with syntax highlighting
- 📈 Summary box with progress bar
- 🎉 Celebration animation when all tests pass

## Demo UI

Open in browser: http://localhost:8083

**Tabs:**
1. **Capability Discovery** - GET /metadata
2. **Patient Match** - PDQm/PIXm identifier search
3. **Document Consumer** - ITI-67/68 (query/retrieve)
4. **Document Producer** - ITI-65 (publish) ⭐ NEW
5. **Resource Access** - QEDm PCC-44 (query all resources)

## All 5 Actors Covered

✅ Document Producer (ITI-65)
✅ Document Access Provider (ITI-67, ITI-68)
✅ Document Consumer (ITI-67, ITI-68)
✅ Resource Access Provider (PCC-44)
✅ Resource Consumer (PCC-44)

## Test Suite

```bash
# Structure validation (no Docker needed)
./test/validate_structure.sh

# Full automated tests (Docker required)
./test/enhanced_run_tests.sh

# Manual checklist
cat test/MANUAL_TEST_CHECKLIST.md
```

Enjoy the demo! 🚀
