# EU Health Data API Demo - Quick Start

## Run the ASCII Demo

```bash
# Make sure services are running
cd docker
docker compose up -d

# Wait ~30 seconds, then install dependencies and run the demo
cd ..
pip install -r requirements.txt
python3 demo_runner.py
```

## What You'll See

The demo runner shows:
- ✨ Bouncing animations
- 🎨 Claude code-style colors
- 📊 Test results with visual indicators
- 📋 JSON previews
- 📈 Summary statistics

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
