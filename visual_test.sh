#!/bin/bash
# Visual testing helper for ASCII demo
# Re-runs the demo to iterate on visuals

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
ORANGE='\033[38;5;208m'
GREEN='\033[38;5;114m'
GRAY='\033[38;5;245m'
CYAN='\033[38;5;123m'
YELLOW='\033[38;5;221m'
RED='\033[38;5;203m'
RESET='\033[0m'

show_help() {
    echo ""
    echo -e "${ORANGE}╭─────────────────────────────────────────────────╮${RESET}"
    echo -e "${ORANGE}│${RESET}  ${ORANGE}ASCII Demo Visual Tester${RESET}                       ${ORANGE}│${RESET}"
    echo -e "${ORANGE}╰─────────────────────────────────────────────────╯${RESET}"
    echo ""
    echo "Usage: ./visual_test.sh [options]"
    echo ""
    echo -e "${CYAN}Scenarios:${RESET}"
    echo -e "  -s, --success     ${GREEN}✓${RESET} All tests pass (default)"
    echo -e "  -f, --failure     ${RED}✗${RESET} Tests fail scenario"
    echo -e "  -x, --mixed       ${YELLOW}⚠${RESET} Mixed pass/fail scenario"
    echo ""
    echo -e "${CYAN}Options:${RESET}"
    echo "  -l, --live        Run live mode (requires running API)"
    echo "  -n, --no-anim     Disable animations"
    echo "  -w, --watch       Watch mode (re-run on file change)"
    echo "  -a, --all         Run all scenarios in sequence"
    echo "  -h, --help        Show this help"
    echo ""
    echo -e "${CYAN}Examples:${RESET}"
    echo "  ./visual_test.sh              # Run success mock demo"
    echo "  ./visual_test.sh -f           # Run failure scenario"
    echo "  ./visual_test.sh -x -n        # Mixed scenario, no animation"  
    echo "  ./visual_test.sh -a           # Run all scenarios"
    echo "  ./visual_test.sh -w           # Watch mode for iterating"
    echo ""
}

MODE="--mock success"
ANIM=""
WATCH=false
ALL_SCENARIOS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--success)
            MODE="--mock success"
            shift
            ;;
        -f|--failure)
            MODE="--mock failure"
            shift
            ;;
        -x|--mixed)
            MODE="--mock mixed"
            shift
            ;;
        -l|--live)
            MODE=""
            shift
            ;;
        -n|--no-anim)
            ANIM="--no-animation"
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -a|--all)
            ALL_SCENARIOS=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

run_demo() {
    python3 "$SCRIPT_DIR/demo/ascii_demo.py" $MODE $ANIM
}

run_all_scenarios() {
    echo -e "\n${ORANGE}Running all scenarios...${RESET}\n"
    
    echo -e "${GREEN}━━━ SUCCESS SCENARIO ━━━${RESET}"
    python3 "$SCRIPT_DIR/demo/ascii_demo.py" --mock success $ANIM
    echo -e "\n${GRAY}Press Enter for next scenario...${RESET}"
    read -r
    
    echo -e "${YELLOW}━━━ MIXED SCENARIO ━━━${RESET}"
    python3 "$SCRIPT_DIR/demo/ascii_demo.py" --mock mixed $ANIM
    echo -e "\n${GRAY}Press Enter for next scenario...${RESET}"
    read -r
    
    echo -e "${RED}━━━ FAILURE SCENARIO ━━━${RESET}"
    python3 "$SCRIPT_DIR/demo/ascii_demo.py" --mock failure $ANIM
    
    echo -e "\n${ORANGE}All scenarios complete!${RESET}\n"
}

if [ "$ALL_SCENARIOS" = true ]; then
    run_all_scenarios
elif [ "$WATCH" = true ]; then
    echo -e "${ORANGE}Watch mode${RESET} - Press Ctrl+C to exit"
    echo -e "${GRAY}Watching demo/ascii_demo.py for changes...${RESET}"
    echo ""
    
    # Check if inotifywait is available
    if command -v inotifywait &> /dev/null; then
        while true; do
            run_demo
            echo ""
            echo -e "${GRAY}Waiting for changes... (Press Ctrl+C to exit)${RESET}"
            inotifywait -q -e modify "$SCRIPT_DIR/demo/ascii_demo.py" 2>/dev/null || sleep 2
            clear
        done
    else
        # Fallback: simple loop with user input
        while true; do
            run_demo
            echo ""
            echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
            echo -e "${ORANGE}Press Enter to re-run, or Ctrl+C to exit${RESET}"
            read -r
            clear
        done
    fi
else
    run_demo
fi
