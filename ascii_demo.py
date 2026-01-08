#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  EU Health Data API - Claude Code Style ASCII Demo                            ║
║  Interactive test suite with beautiful terminal animations                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import time
import json
import sys
import os
import random
import threading
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any
from enum import Enum

# Try to import httpx, fall back to requests
try:
    import httpx
    HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import requests as httpx
        HTTP_CLIENT = "requests"
    except ImportError:
        HTTP_CLIENT = None

# ═══════════════════════════════════════════════════════════════════════════════
# ANSI Color & Style Constants
# ═══════════════════════════════════════════════════════════════════════════════

class Style:
    """Terminal styles and colors (Claude Code aesthetic)"""
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Primary palette (Claude Code inspired)
    ORANGE = '\033[38;5;208m'      # Primary accent
    PEACH = '\033[38;5;216m'       # Soft accent
    CORAL = '\033[38;5;209m'       # Warm accent
    
    # Functional colors
    SUCCESS = '\033[38;5;114m'     # Green - success
    ERROR = '\033[38;5;203m'       # Red - error
    WARNING = '\033[38;5;221m'     # Yellow - warning
    INFO = '\033[38;5;117m'        # Blue - info
    
    # Neutrals
    WHITE = '\033[38;5;255m'
    GRAY = '\033[38;5;245m'
    DARK_GRAY = '\033[38;5;238m'
    LIGHT_GRAY = '\033[38;5;250m'
    
    # Special
    PURPLE = '\033[38;5;141m'
    CYAN = '\033[38;5;123m'
    PINK = '\033[38;5;218m'
    
    # Background
    BG_DARK = '\033[48;5;234m'
    BG_DARKER = '\033[48;5;232m'
    BG_HIGHLIGHT = '\033[48;5;236m'
    BG_SUCCESS = '\033[48;5;22m'
    BG_ERROR = '\033[48;5;52m'

# ═══════════════════════════════════════════════════════════════════════════════
# Animation Frames
# ═══════════════════════════════════════════════════════════════════════════════

class Spinners:
    """Collection of spinner animations"""
    DOTS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    BOUNCE = ["⠁", "⠂", "⠄", "⠂"]
    ARROWS = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
    PULSE = ["◜", "◠", "◝", "◞", "◡", "◟"]
    BOUNCE_BAR = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"]
    MOON = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    DOTS_BOUNCE = ["   ", ".  ", ".. ", "...", " ..", "  .", "   "]
    BRAILLE = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    WAVE = ["▁▂▃▄▅▆▇█▇▆▅▄▃▂▁", "▂▃▄▅▆▇█▇▆▅▄▃▂▁▁", "▃▄▅▆▇█▇▆▅▄▃▂▁▁▂", 
            "▄▅▆▇█▇▆▅▄▃▂▁▁▂▃", "▅▆▇█▇▆▅▄▃▂▁▁▂▃▄", "▆▇█▇▆▅▄▃▂▁▁▂▃▄▅",
            "▇█▇▆▅▄▃▂▁▁▂▃▄▅▆", "█▇▆▅▄▃▂▁▁▂▃▄▅▆▇"]

class Icons:
    """Status icons"""
    CHECK = "✓"
    CROSS = "✗"
    ARROW = "→"
    BULLET = "•"
    STAR = "★"
    DIAMOND = "◆"
    CIRCLE = "●"
    CIRCLE_EMPTY = "○"
    BOX = "■"
    BOX_EMPTY = "□"
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    SKIP = "⊘"
    INFO = "ℹ"
    WARN = "⚠"
    ROCKET = "🚀"
    SPARKLES = "✨"
    FIRE = "🔥"
    HEART = "❤"
    BOLT = "⚡"

# ═══════════════════════════════════════════════════════════════════════════════
# Core UI Components
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear terminal and move cursor to home"""
    print("\033[2J\033[H", end="", flush=True)

def hide_cursor():
    """Hide terminal cursor"""
    print("\033[?25l", end="", flush=True)

def show_cursor():
    """Show terminal cursor"""
    print("\033[?25h", end="", flush=True)

def move_cursor(x: int, y: int):
    """Move cursor to position"""
    print(f"\033[{y};{x}H", end="", flush=True)

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24

def print_at(x: int, y: int, text: str):
    """Print text at specific position"""
    move_cursor(x, y)
    print(text, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Animation Classes
# ═══════════════════════════════════════════════════════════════════════════════

class Spinner:
    """Animated spinner with customizable frames"""
    def __init__(self, text: str = "", frames: List[str] = None, color: str = Style.ORANGE):
        self.text = text
        self.frames = frames or Spinners.DOTS
        self.color = color
        self._running = False
        self._thread = None
        self._frame_idx = 0
    
    def _animate(self):
        while self._running:
            frame = self.frames[self._frame_idx % len(self.frames)]
            print(f"\r{self.color}{frame}{Style.RESET} {self.text}", end="", flush=True)
            self._frame_idx += 1
            time.sleep(0.08)
    
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self
    
    def stop(self, success: bool = True, message: str = None):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.2)
        
        icon = f"{Style.SUCCESS}{Icons.CHECK}" if success else f"{Style.ERROR}{Icons.CROSS}"
        msg = message or self.text
        print(f"\r{icon}{Style.RESET} {msg}                    ")
        return self
    
    def update(self, text: str):
        self.text = text

def spinner_animation(text: str, duration: float = 1.0, frames: List[str] = None):
    """Simple spinner animation for a duration"""
    frames = frames or Spinners.DOTS
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        print(f"\r{Style.ORANGE}{frame}{Style.RESET} {text}", end="", flush=True)
        time.sleep(0.08)
        i += 1
    print(f"\r{Style.SUCCESS}{Icons.CHECK}{Style.RESET} {text}                    ")

def bounce_animation(text: str, duration: float = 0.8):
    """Bouncing dot animation"""
    frames = Spinners.BOUNCE_BAR
    colors = [Style.ORANGE, Style.PEACH, Style.CORAL, Style.WARNING, Style.SUCCESS]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        color = colors[i % len(colors)]
        print(f"\r{color}{frame}{Style.RESET} {text}", end="", flush=True)
        time.sleep(0.05)
        i += 1
    print(f"\r{Style.SUCCESS}{Icons.CHECK}{Style.RESET} {text}                    ")

def wave_animation(text: str, duration: float = 1.0):
    """Wave animation effect"""
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        wave = Spinners.WAVE[i % len(Spinners.WAVE)]
        print(f"\r{Style.CYAN}{wave}{Style.RESET} {text}", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{Style.SUCCESS}{'█' * 15}{Style.RESET} {text}                    ")

def typing_effect(text: str, delay: float = 0.03, color: str = Style.WHITE):
    """Typewriter effect for text"""
    for char in text:
        print(f"{color}{char}{Style.RESET}", end="", flush=True)
        time.sleep(delay)
    print()

def rainbow_text(text: str) -> str:
    """Apply rainbow colors to text"""
    colors = [Style.ERROR, Style.ORANGE, Style.WARNING, Style.SUCCESS, Style.CYAN, Style.PURPLE, Style.PINK]
    result = ""
    for i, char in enumerate(text):
        if char != " ":
            result += f"{colors[i % len(colors)]}{char}"
        else:
            result += char
    return result + Style.RESET

def progress_bar(current: int, total: int, width: int = 40, 
                 fill_char: str = "█", empty_char: str = "░",
                 color: str = Style.SUCCESS) -> str:
    """Generate a progress bar string"""
    filled = int(width * current / total) if total > 0 else 0
    bar = fill_char * filled + empty_char * (width - filled)
    pct = (current / total * 100) if total > 0 else 0
    return f"{color}{bar}{Style.RESET} {pct:5.1f}%"

# ═══════════════════════════════════════════════════════════════════════════════
# Box Drawing & Layouts
# ═══════════════════════════════════════════════════════════════════════════════

class Box:
    """ASCII box drawing characters"""
    # Single line
    H = "─"
    V = "│"
    TL = "┌"
    TR = "┐"
    BL = "└"
    BR = "┘"
    T = "┬"
    B = "┴"
    L = "├"
    R = "┤"
    X = "┼"
    
    # Double line
    DH = "═"
    DV = "║"
    DTL = "╔"
    DTR = "╗"
    DBL = "╚"
    DBR = "╝"
    
    # Rounded
    RTL = "╭"
    RTR = "╮"
    RBL = "╰"
    RBR = "╯"

def draw_box(width: int, height: int, title: str = "", 
             style: str = "rounded", color: str = Style.ORANGE) -> List[str]:
    """Draw an ASCII box with optional title"""
    if style == "rounded":
        tl, tr, bl, br = Box.RTL, Box.RTR, Box.RBL, Box.RBR
        h, v = Box.H, Box.V
    elif style == "double":
        tl, tr, bl, br = Box.DTL, Box.DTR, Box.DBL, Box.DBR
        h, v = Box.DH, Box.DV
    else:
        tl, tr, bl, br = Box.TL, Box.TR, Box.BL, Box.BR
        h, v = Box.H, Box.V
    
    lines = []
    
    # Top border with title
    if title:
        title_padded = f" {title} "
        padding = width - 2 - len(title_padded)
        top = f"{color}{tl}{h}{Style.BOLD}{Style.WHITE}{title_padded}{Style.RESET}{color}{h * padding}{tr}{Style.RESET}"
    else:
        top = f"{color}{tl}{h * (width - 2)}{tr}{Style.RESET}"
    lines.append(top)
    
    # Middle
    for _ in range(height - 2):
        lines.append(f"{color}{v}{Style.RESET}{' ' * (width - 2)}{color}{v}{Style.RESET}")
    
    # Bottom
    lines.append(f"{color}{bl}{h * (width - 2)}{br}{Style.RESET}")
    
    return lines

def print_box(lines: List[str], content: List[str] = None, padding: int = 1):
    """Print a box with optional content"""
    for i, line in enumerate(lines):
        print(line)
        if content and 0 < i < len(lines) - 1 and (i - 1) < len(content):
            # Overlay content
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# Claude Code Style Header
# ═══════════════════════════════════════════════════════════════════════════════

CLAUDE_LOGO = r"""
   _____ _                 _        _____           _      
  / ____| |               | |      / ____|         | |     
 | |    | | __ _ _   _  __| | ___ | |     ___   __| | ___ 
 | |    | |/ _` | | | |/ _` |/ _ \| |    / _ \ / _` |/ _ \
 | |____| | (_| | |_| | (_| |  __/| |___| (_) | (_| |  __/
  \_____|_|\__,_|\__,_|\__,_|\___| \_____\___/ \__,_|\___|
"""

def print_claude_header():
    """Print Claude Code style header"""
    width = 78
    
    print()
    print(f"{Style.ORANGE}╔{'═' * (width-2)}╗{Style.RESET}")
    print(f"{Style.ORANGE}║{Style.RESET}{' ' * (width-2)}{Style.ORANGE}║{Style.RESET}")
    
    # Logo - cleaner minimal version
    logo_lines = [
        "┌────────────────────────────────────────────────────────────────────┐",
        "│  ███████╗██╗   ██╗    ██╗  ██╗███████╗ █████╗ ██╗  ████████╗██╗  │",
        "│  ██╔════╝██║   ██║    ██║  ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  │",
        "│  █████╗  ██║   ██║    ███████║█████╗  ███████║██║     ██║   ██║  │",
        "│  ██╔══╝  ██║   ██║    ██╔══██║██╔══╝  ██╔══██║██║     ██║   ██║  │",
        "│  ███████╗╚██████╔╝    ██║  ██║███████╗██║  ██║███████╗██║   ██║  │",
        "│  ╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  │",
        "└────────────────────────────────────────────────────────────────────┘",
    ]
    
    for line in logo_lines:
        padding = (width - 2 - len(line)) // 2
        padded = ' ' * padding + line + ' ' * (width - 2 - padding - len(line))
        print(f"{Style.ORANGE}║{Style.PEACH}{padded}{Style.RESET}{Style.ORANGE}║{Style.RESET}")
    
    print(f"{Style.ORANGE}║{Style.RESET}{' ' * (width-2)}{Style.ORANGE}║{Style.RESET}")
    
    subtitle = "API Demo Suite • Claude Code Style"
    sub_padding = (width - 2 - len(subtitle)) // 2
    print(f"{Style.ORANGE}║{Style.RESET}{' ' * sub_padding}{Style.BOLD}{Style.WHITE}{subtitle}{Style.RESET}{' ' * (width - 2 - sub_padding - len(subtitle))}{Style.ORANGE}║{Style.RESET}")
    
    info = "MHD • QEDm • PDQm/PIXm • 5-Actor Model"
    info_padding = (width - 2 - len(info)) // 2
    print(f"{Style.ORANGE}║{Style.RESET}{' ' * info_padding}{Style.DIM}{Style.GRAY}{info}{Style.RESET}{' ' * (width - 2 - info_padding - len(info))}{Style.ORANGE}║{Style.RESET}")
    
    print(f"{Style.ORANGE}║{Style.RESET}{' ' * (width-2)}{Style.ORANGE}║{Style.RESET}")
    print(f"{Style.ORANGE}╚{'═' * (width-2)}╝{Style.RESET}")
    print()

def print_minimal_header():
    """Print a minimal Claude-style header"""
    print()
    print(f"  {Style.ORANGE}●{Style.PEACH}●{Style.CORAL}●{Style.RESET}  {Style.BOLD}EU Health Data API Demo{Style.RESET}")
    print(f"  {Style.DIM}{Style.GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET}")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# Test Result Types
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    status: TestStatus
    duration: float = 0.0
    message: str = ""
    details: Dict[str, Any] = None

@dataclass 
class TestSuite:
    """Collection of test results"""
    name: str
    results: List[TestResult] = None
    
    def __post_init__(self):
        self.results = self.results or []
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)
    
    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
    
    @property
    def total(self) -> int:
        return len(self.results)

# ═══════════════════════════════════════════════════════════════════════════════
# Test Printing Functions
# ═══════════════════════════════════════════════════════════════════════════════

def print_section_header(title: str, icon: str = "◆", color: str = Style.ORANGE):
    """Print a section header"""
    print()
    print(f"  {color}{icon}{Style.RESET} {Style.BOLD}{title}{Style.RESET}")
    print(f"  {Style.DARK_GRAY}{'─' * 55}{Style.RESET}")

def print_test_result(result: TestResult, indent: int = 4):
    """Print a single test result"""
    prefix = " " * indent
    
    if result.status == TestStatus.PASSED:
        icon = f"{Style.SUCCESS}{Icons.CHECK}{Style.RESET}"
        name_style = Style.WHITE
    elif result.status == TestStatus.FAILED:
        icon = f"{Style.ERROR}{Icons.CROSS}{Style.RESET}"
        name_style = Style.ERROR
    elif result.status == TestStatus.SKIPPED:
        icon = f"{Style.WARNING}{Icons.SKIP}{Style.RESET}"
        name_style = Style.GRAY
    elif result.status == TestStatus.RUNNING:
        icon = f"{Style.CYAN}{Icons.ARROW}{Style.RESET}"
        name_style = Style.CYAN
    else:
        icon = f"{Style.GRAY}{Icons.CIRCLE_EMPTY}{Style.RESET}"
        name_style = Style.GRAY
    
    # Main line
    duration_str = f" {Style.DIM}({result.duration:.0f}ms){Style.RESET}" if result.duration > 0 else ""
    print(f"{prefix}{icon} {name_style}{result.name}{Style.RESET}{duration_str}")
    
    # Message/details
    if result.message:
        print(f"{prefix}  {Style.DIM}{Style.GRAY}└─ {result.message}{Style.RESET}")

def print_test_group(name: str, results: List[TestResult]):
    """Print a group of test results"""
    passed = sum(1 for r in results if r.status == TestStatus.PASSED)
    total = len(results)
    
    if passed == total:
        status_icon = f"{Style.SUCCESS}{Icons.CHECK}{Style.RESET}"
    elif passed > 0:
        status_icon = f"{Style.WARNING}{Icons.WARN}{Style.RESET}"
    else:
        status_icon = f"{Style.ERROR}{Icons.CROSS}{Style.RESET}"
    
    print(f"\n  {status_icon} {Style.BOLD}{name}{Style.RESET} {Style.DIM}({passed}/{total}){Style.RESET}")
    
    for result in results:
        print_test_result(result)

def print_json_preview(data: dict, max_lines: int = 8, indent: int = 4):
    """Print JSON preview in Claude style"""
    prefix = " " * indent
    json_str = json.dumps(data, indent=2)
    lines = json_str.split('\n')
    
    print(f"{prefix}{Style.BG_HIGHLIGHT}")
    for line in lines[:max_lines]:
        # Syntax highlighting
        highlighted = line
        highlighted = highlighted.replace('":', f'"{Style.CYAN}:{Style.RESET}{Style.BG_HIGHLIGHT}')
        highlighted = highlighted.replace('": "', f'{Style.CYAN}": "{Style.SUCCESS}')
        highlighted = highlighted.replace('",', f'{Style.SUCCESS}",{Style.RESET}{Style.BG_HIGHLIGHT}')
        highlighted = highlighted.replace('"', f'{Style.PEACH}"{Style.RESET}{Style.BG_HIGHLIGHT}')
        print(f"{prefix}  {Style.BG_HIGHLIGHT}{highlighted}{Style.RESET}")
    
    if len(lines) > max_lines:
        print(f"{prefix}  {Style.DIM}... {len(lines) - max_lines} more lines{Style.RESET}")
    print(f"{prefix}{Style.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
# Summary Display
# ═══════════════════════════════════════════════════════════════════════════════

def print_summary_box(suite: TestSuite):
    """Print a summary box for test results"""
    width = 50
    
    # Calculate pass rate
    pass_rate = (suite.passed / suite.total * 100) if suite.total > 0 else 0
    
    # Determine overall status color
    if suite.failed == 0:
        status_color = Style.SUCCESS
        status_icon = Icons.SPARKLES
        status_text = "ALL TESTS PASSED"
    elif suite.passed > suite.failed:
        status_color = Style.WARNING
        status_icon = Icons.WARN
        status_text = "SOME TESTS FAILED"
    else:
        status_color = Style.ERROR
        status_icon = Icons.CROSS
        status_text = "TESTS FAILED"
    
    print()
    print(f"  {Style.ORANGE}╭{'─' * (width-2)}╮{Style.RESET}")
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * (width-2)}{Style.ORANGE}│{Style.RESET}")
    
    # Status line
    status_line = f"{status_icon} {status_text}"
    padding = (width - 4 - len(status_line)) // 2
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * padding}{status_color}{Style.BOLD}{status_line}{Style.RESET}{' ' * (width - 4 - padding - len(status_line))}{Style.ORANGE}│{Style.RESET}")
    
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * (width-2)}{Style.ORANGE}│{Style.RESET}")
    print(f"  {Style.ORANGE}├{'─' * (width-2)}┤{Style.RESET}")
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * (width-2)}{Style.ORANGE}│{Style.RESET}")
    
    # Stats
    stats = [
        (f"{Icons.CHECK} Passed", suite.passed, Style.SUCCESS),
        (f"{Icons.CROSS} Failed", suite.failed, Style.ERROR),
        (f"{Icons.SKIP} Skipped", suite.skipped, Style.WARNING),
    ]
    
    for label, count, color in stats:
        stat_text = f"  {label}: {count}"
        print(f"  {Style.ORANGE}│{Style.RESET}  {color}{stat_text:<20}{Style.RESET}{' ' * (width - 24)}{Style.ORANGE}│{Style.RESET}")
    
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * (width-2)}{Style.ORANGE}│{Style.RESET}")
    
    # Progress bar
    bar = progress_bar(suite.passed, suite.total, width=width-10)
    print(f"  {Style.ORANGE}│{Style.RESET}  {bar}  {Style.ORANGE}│{Style.RESET}")
    
    print(f"  {Style.ORANGE}│{Style.RESET}{' ' * (width-2)}{Style.ORANGE}│{Style.RESET}")
    print(f"  {Style.ORANGE}╰{'─' * (width-2)}╯{Style.RESET}")
    print()

def print_celebration():
    """Print celebration animation for all tests passing"""
    frames = [
        ["     ", "  🎉  ", "     "],
        [" 🎉  ", "  ✨  ", "  🎉 "],
        ["🎉 🎊", " ✨✨ ", "🎊 🎉"],
        [" 🎊  ", "  🎉  ", "  🎊 "],
    ]
    
    for _ in range(2):
        for frame in frames:
            print("\r", end="")
            for line in frame:
                print(f"  {line}")
            time.sleep(0.2)
            print("\033[3A", end="")  # Move up 3 lines
    
    print("\n\n\n")

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Client Wrapper
# ═══════════════════════════════════════════════════════════════════════════════

class APIClient:
    """Simple HTTP client for API testing"""
    
    def __init__(self, base_url: str = "http://localhost:8082"):
        self.base_url = base_url.rstrip("/")
    
    def get(self, path: str, params: dict = None, timeout: float = 5.0) -> tuple:
        """Make GET request, return (status_code, json_data or None, error)"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        if HTTP_CLIENT is None:
            return (0, None, "No HTTP client available (install httpx or requests)")
        
        try:
            if HTTP_CLIENT == "httpx":
                response = httpx.get(url, params=params, timeout=timeout)
            else:
                response = httpx.get(url, params=params, timeout=timeout)
            
            try:
                data = response.json()
            except:
                data = None
            
            return (response.status_code, data, None)
        except Exception as e:
            return (0, None, str(e))
    
    def is_available(self) -> bool:
        """Check if API is available"""
        status, _, error = self.get("/", timeout=2.0)
        return status == 200 or status == 404  # 404 is fine, means server is up

# ═══════════════════════════════════════════════════════════════════════════════
# Test Cases
# ═══════════════════════════════════════════════════════════════════════════════

def run_capability_discovery_tests(client: APIClient) -> List[TestResult]:
    """Run capability discovery tests"""
    results = []
    
    # Test 1: Metadata endpoint
    start = time.time()
    status, data, error = client.get("/metadata")
    duration = (time.time() - start) * 1000
    
    if error:
        results.append(TestResult(
            name="GET /metadata",
            status=TestStatus.FAILED,
            duration=duration,
            message=f"Connection error: {error}"
        ))
        return results
    
    if status == 200 and data:
        results.append(TestResult(
            name="GET /metadata",
            status=TestStatus.PASSED,
            duration=duration,
            message=f"Status: {status}"
        ))
        
        # Test 2: ResourceType
        if data.get("resourceType") == "CapabilityStatement":
            results.append(TestResult(
                name="ResourceType is CapabilityStatement",
                status=TestStatus.PASSED,
                message="Valid FHIR CapabilityStatement"
            ))
        else:
            results.append(TestResult(
                name="ResourceType is CapabilityStatement",
                status=TestStatus.FAILED,
                message=f"Got: {data.get('resourceType')}"
            ))
        
        # Test 3: FHIR version
        if data.get("fhirVersion") == "4.0.1":
            results.append(TestResult(
                name="FHIR Version is 4.0.1",
                status=TestStatus.PASSED
            ))
        else:
            results.append(TestResult(
                name="FHIR Version is 4.0.1",
                status=TestStatus.FAILED,
                message=f"Got: {data.get('fhirVersion')}"
            ))
        
        # Test 4: Instantiates
        instantiates = data.get("instantiates", [])
        if instantiates:
            results.append(TestResult(
                name="Priority areas declared (instantiates)",
                status=TestStatus.PASSED,
                message=f"{len(instantiates)} priority area(s)"
            ))
        else:
            results.append(TestResult(
                name="Priority areas declared (instantiates)",
                status=TestStatus.SKIPPED,
                message="No priority areas declared"
            ))
        
        # Test 5: Resource types
        resources = data.get("rest", [{}])[0].get("resource", [])
        resource_types = [r.get("type") for r in resources]
        
        for res_type in ["DocumentReference", "Binary", "Patient", "Condition"]:
            if res_type in resource_types:
                results.append(TestResult(
                    name=f"{res_type} resource declared",
                    status=TestStatus.PASSED
                ))
            else:
                results.append(TestResult(
                    name=f"{res_type} resource declared",
                    status=TestStatus.FAILED,
                    message="Not found in CapabilityStatement"
                ))
    else:
        results.append(TestResult(
            name="GET /metadata",
            status=TestStatus.FAILED,
            duration=duration,
            message=f"Status: {status}"
        ))
    
    return results

def run_patient_match_tests(client: APIClient) -> tuple:
    """Run patient match tests, return (results, patient_id)"""
    results = []
    patient_id = None
    
    # Test 1: Patient search by identifier
    start = time.time()
    status, data, error = client.get(
        "/fhir/Patient",
        params={"identifier": "urn:oid:2.16.840.1.113883.2.4.6.3|123456789"}
    )
    duration = (time.time() - start) * 1000
    
    if error:
        results.append(TestResult(
            name="GET /Patient?identifier=...",
            status=TestStatus.FAILED,
            duration=duration,
            message=error
        ))
        return results, patient_id
    
    if status == 200 and data:
        results.append(TestResult(
            name="GET /Patient?identifier=...",
            status=TestStatus.PASSED,
            duration=duration,
            message=f"Status: {status}"
        ))
        
        # Check bundle structure
        if data.get("resourceType") == "Bundle":
            results.append(TestResult(
                name="Returns FHIR Bundle",
                status=TestStatus.PASSED
            ))
            
            entries = data.get("entry", [])
            if entries:
                patient = entries[0].get("resource", {})
                patient_id = patient.get("id")
                results.append(TestResult(
                    name="Patient found in Bundle",
                    status=TestStatus.PASSED,
                    message=f"ID: {patient_id}"
                ))
            else:
                results.append(TestResult(
                    name="Patient found in Bundle",
                    status=TestStatus.FAILED,
                    message="Empty bundle"
                ))
        else:
            results.append(TestResult(
                name="Returns FHIR Bundle",
                status=TestStatus.FAILED,
                message=f"Got: {data.get('resourceType')}"
            ))
    else:
        results.append(TestResult(
            name="GET /Patient?identifier=...",
            status=TestStatus.FAILED,
            duration=duration,
            message=f"Status: {status}"
        ))
    
    return results, patient_id

def run_document_tests(client: APIClient, patient_id: str) -> List[TestResult]:
    """Run document exchange tests (MHD)"""
    results = []
    
    if not patient_id:
        results.append(TestResult(
            name="ITI-67: Find DocumentReferences",
            status=TestStatus.SKIPPED,
            message="No patient ID available"
        ))
        return results
    
    # Test 1: Find DocumentReferences
    start = time.time()
    status, data, error = client.get(
        "/fhir/DocumentReference",
        params={"patient": f"Patient/{patient_id}", "status": "current"}
    )
    duration = (time.time() - start) * 1000
    
    if error:
        results.append(TestResult(
            name="ITI-67: Find DocumentReferences",
            status=TestStatus.FAILED,
            duration=duration,
            message=error
        ))
        return results
    
    if status == 200 and data and data.get("resourceType") == "Bundle":
        entries = data.get("entry", [])
        results.append(TestResult(
            name="ITI-67: Find DocumentReferences",
            status=TestStatus.PASSED,
            duration=duration,
            message=f"Found {len(entries)} document(s)"
        ))
        
        if entries:
            doc_ref = entries[0].get("resource", {})
            
            # Check document structure
            if doc_ref.get("status") == "current":
                results.append(TestResult(
                    name="DocumentReference has status=current",
                    status=TestStatus.PASSED
                ))
            
            # Check for binary reference
            content = doc_ref.get("content", [])
            if content:
                attachment = content[0].get("attachment", {})
                binary_url = attachment.get("url", "")
                
                if binary_url:
                    binary_id = binary_url.split("/")[-1]
                    results.append(TestResult(
                        name="DocumentReference has Binary URL",
                        status=TestStatus.PASSED,
                        message=f"Binary/{binary_id}"
                    ))
                    
                    # Test ITI-68: Retrieve Binary
                    start = time.time()
                    bin_status, _, bin_error = client.get(f"/fhir/Binary/{binary_id}")
                    bin_duration = (time.time() - start) * 1000
                    
                    if bin_status == 200:
                        results.append(TestResult(
                            name="ITI-68: Retrieve Binary",
                            status=TestStatus.PASSED,
                            duration=bin_duration
                        ))
                    else:
                        results.append(TestResult(
                            name="ITI-68: Retrieve Binary",
                            status=TestStatus.FAILED,
                            duration=bin_duration,
                            message=f"Status: {bin_status}"
                        ))
    else:
        results.append(TestResult(
            name="ITI-67: Find DocumentReferences",
            status=TestStatus.FAILED,
            duration=duration,
            message=f"Status: {status}"
        ))
    
    return results

def run_resource_access_tests(client: APIClient, patient_id: str) -> List[TestResult]:
    """Run resource access tests (QEDm PCC-44)"""
    results = []
    
    if not patient_id:
        results.append(TestResult(
            name="Resource Access Tests",
            status=TestStatus.SKIPPED,
            message="No patient ID available"
        ))
        return results
    
    resource_types = ["Condition", "Observation", "AllergyIntolerance", "MedicationStatement", "Encounter"]
    
    for res_type in resource_types:
        start = time.time()
        status, data, error = client.get(
            f"/fhir/{res_type}",
            params={"patient": f"Patient/{patient_id}"}
        )
        duration = (time.time() - start) * 1000
        
        if error:
            results.append(TestResult(
                name=f"GET /{res_type}?patient=...",
                status=TestStatus.FAILED,
                duration=duration,
                message=error
            ))
            continue
        
        if status == 200 and data and data.get("resourceType") == "Bundle":
            entries = data.get("entry", [])
            results.append(TestResult(
                name=f"GET /{res_type}?patient=...",
                status=TestStatus.PASSED if entries else TestStatus.SKIPPED,
                duration=duration,
                message=f"{len(entries)} result(s)"
            ))
        else:
            results.append(TestResult(
                name=f"GET /{res_type}?patient=...",
                status=TestStatus.FAILED,
                duration=duration,
                message=f"Status: {status}"
            ))
    
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# Main Demo Runner
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo(base_url: str = "http://localhost:8082", animated: bool = True):
    """Run the complete demo suite"""
    
    clear_screen()
    print_claude_header()
    
    client = APIClient(base_url)
    suite = TestSuite(name="EU Health Data API Tests")
    
    # Check service availability
    print(f"  {Style.GRAY}Checking API availability...{Style.RESET}")
    
    if animated:
        spinner_animation("Connecting to API", duration=0.5)
    
    if not client.is_available():
        print()
        print(f"  {Style.ERROR}{Icons.CROSS} API not available at {base_url}{Style.RESET}")
        print()
        print(f"  {Style.WARNING}Please ensure services are running:{Style.RESET}")
        print(f"  {Style.DIM}  cd docker && docker compose up -d{Style.RESET}")
        print()
        return 1
    
    print(f"  {Style.SUCCESS}{Icons.CHECK}{Style.RESET} API available at {Style.CYAN}{base_url}{Style.RESET}")
    print()
    
    # Run test suites
    print_section_header("1. Capability Discovery", "◆", Style.ORANGE)
    if animated:
        bounce_animation("Testing CapabilityStatement...", 0.6)
    cap_results = run_capability_discovery_tests(client)
    for r in cap_results:
        print_test_result(r)
        suite.results.append(r)
    
    print_section_header("2. Patient Match (PDQm/PIXm)", "◆", Style.PURPLE)
    if animated:
        bounce_animation("Testing patient search...", 0.6)
    patient_results, patient_id = run_patient_match_tests(client)
    for r in patient_results:
        print_test_result(r)
        suite.results.append(r)
    
    if patient_id:
        print(f"\n    {Style.DIM}Using patient: {Style.CYAN}{patient_id}{Style.RESET}")
    
    print_section_header("3. Document Exchange (MHD)", "◆", Style.CORAL)
    if animated:
        bounce_animation("Testing document queries...", 0.6)
    doc_results = run_document_tests(client, patient_id)
    for r in doc_results:
        print_test_result(r)
        suite.results.append(r)
    
    print_section_header("4. Resource Access (QEDm PCC-44)", "◆", Style.SUCCESS)
    if animated:
        wave_animation("Testing resource queries...", 0.8)
    res_results = run_resource_access_tests(client, patient_id)
    for r in res_results:
        print_test_result(r)
        suite.results.append(r)
    
    # Summary
    print()
    print(f"  {Style.ORANGE}{'═' * 55}{Style.RESET}")
    print_summary_box(suite)
    
    if suite.failed == 0 and animated:
        print_celebration()
    
    # Footer
    print(f"  {Style.GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET}")
    print(f"  {Style.DIM}Demo UI:{Style.RESET} {Style.CYAN}http://localhost:8083{Style.RESET}")
    print(f"  {Style.DIM}API Base:{Style.RESET} {Style.CYAN}{base_url}{Style.RESET}")
    print(f"  {Style.GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET}")
    print()
    
    return 0 if suite.failed == 0 else 1

# ═══════════════════════════════════════════════════════════════════════════════
# Interactive Menu
# ═══════════════════════════════════════════════════════════════════════════════

def interactive_menu():
    """Show interactive menu for demo options"""
    clear_screen()
    print_minimal_header()
    
    options = [
        ("Run Full Test Suite", "run_all"),
        ("Capability Discovery Only", "capability"),
        ("Patient Match Only", "patient"),
        ("Document Tests Only", "document"),
        ("Resource Tests Only", "resource"),
        ("Exit", "exit"),
    ]
    
    print(f"  {Style.BOLD}Select an option:{Style.RESET}\n")
    
    for i, (label, _) in enumerate(options, 1):
        print(f"    {Style.ORANGE}{i}{Style.RESET}  {label}")
    
    print()
    
    try:
        choice = input(f"  {Style.GRAY}Enter choice [1-{len(options)}]: {Style.RESET}")
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(options):
            return options[choice_idx][1]
    except (ValueError, KeyboardInterrupt):
        pass
    
    return "exit"

# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def run_mock_demo(animated: bool = True, scenario: str = "success"):
    """Run demo with mock data for visual testing
    
    Scenarios:
        - success: All tests pass
        - failure: Some tests fail
        - mixed: Mix of pass/fail/skip
    """
    
    clear_screen()
    print_claude_header()
    
    suite = TestSuite(name="EU Health Data API Tests")
    
    scenario_labels = {
        "success": f"{Style.SUCCESS}SUCCESS{Style.RESET}",
        "failure": f"{Style.ERROR}FAILURE{Style.RESET}",
        "mixed": f"{Style.WARNING}MIXED{Style.RESET}",
    }
    
    print(f"  {Style.GRAY}Running in MOCK mode ({scenario_labels.get(scenario, scenario)})...{Style.RESET}")
    print()
    
    if animated:
        spinner_animation("Connecting to API", duration=0.5)
    
    print(f"  {Style.SUCCESS}{Icons.CHECK}{Style.RESET} Mock API ready")
    print()
    
    # Mock Capability Discovery
    print_section_header("1. Capability Discovery", "◆", Style.ORANGE)
    if animated:
        bounce_animation("Testing CapabilityStatement...", 0.4)
    
    if scenario == "failure":
        mock_cap_results = [
            TestResult("GET /metadata", TestStatus.FAILED, 45.2, "Connection refused"),
            TestResult("ResourceType is CapabilityStatement", TestStatus.SKIPPED, message="Skipped due to connection error"),
        ]
    elif scenario == "mixed":
        mock_cap_results = [
            TestResult("GET /metadata", TestStatus.PASSED, 45.2, "Status: 200"),
            TestResult("ResourceType is CapabilityStatement", TestStatus.PASSED),
            TestResult("FHIR Version is 4.0.1", TestStatus.FAILED, message="Got: 4.0.0"),
            TestResult("Priority areas declared (instantiates)", TestStatus.PASSED, message="2 priority area(s)"),
            TestResult("DocumentReference resource declared", TestStatus.PASSED),
            TestResult("Binary resource declared", TestStatus.FAILED, message="Not found in CapabilityStatement"),
            TestResult("Patient resource declared", TestStatus.PASSED),
            TestResult("Condition resource declared", TestStatus.PASSED),
        ]
    else:  # success
        mock_cap_results = [
            TestResult("GET /metadata", TestStatus.PASSED, 45.2, "Status: 200"),
            TestResult("ResourceType is CapabilityStatement", TestStatus.PASSED),
            TestResult("FHIR Version is 4.0.1", TestStatus.PASSED),
            TestResult("Priority areas declared (instantiates)", TestStatus.PASSED, message="2 priority area(s)"),
            TestResult("DocumentReference resource declared", TestStatus.PASSED),
            TestResult("Binary resource declared", TestStatus.PASSED),
            TestResult("Patient resource declared", TestStatus.PASSED),
            TestResult("Condition resource declared", TestStatus.PASSED),
        ]
    
    for r in mock_cap_results:
        print_test_result(r)
        suite.results.append(r)
    
    # Mock Patient Match
    print_section_header("2. Patient Match (PDQm/PIXm)", "◆", Style.PURPLE)
    if animated:
        bounce_animation("Testing patient search...", 0.4)
    
    if scenario == "failure":
        mock_patient_results = [
            TestResult("GET /Patient?identifier=...", TestStatus.FAILED, 62.1, "Status: 500"),
            TestResult("Returns FHIR Bundle", TestStatus.SKIPPED),
            TestResult("Patient found in Bundle", TestStatus.SKIPPED),
        ]
    elif scenario == "mixed":
        mock_patient_results = [
            TestResult("GET /Patient?identifier=...", TestStatus.PASSED, 62.1, "Status: 200"),
            TestResult("Returns FHIR Bundle", TestStatus.PASSED),
            TestResult("Patient found in Bundle", TestStatus.FAILED, message="Empty bundle"),
        ]
    else:
        mock_patient_results = [
            TestResult("GET /Patient?identifier=...", TestStatus.PASSED, 62.1, "Status: 200"),
            TestResult("Returns FHIR Bundle", TestStatus.PASSED),
            TestResult("Patient found in Bundle", TestStatus.PASSED, message="ID: patient-a"),
        ]
    
    for r in mock_patient_results:
        print_test_result(r)
        suite.results.append(r)
    
    if scenario not in ["failure"]:
        print(f"\n    {Style.DIM}Using patient: {Style.CYAN}patient-a{Style.RESET}")
    
    # Mock Document Exchange
    print_section_header("3. Document Exchange (MHD)", "◆", Style.CORAL)
    if animated:
        bounce_animation("Testing document queries...", 0.4)
    
    if scenario == "failure":
        mock_doc_results = [
            TestResult("ITI-67: Find DocumentReferences", TestStatus.SKIPPED, message="No patient ID available"),
        ]
    elif scenario == "mixed":
        mock_doc_results = [
            TestResult("ITI-67: Find DocumentReferences", TestStatus.PASSED, 78.3, "Found 2 document(s)"),
            TestResult("DocumentReference has status=current", TestStatus.PASSED),
            TestResult("DocumentReference has Binary URL", TestStatus.PASSED, message="Binary/eps-binary-a"),
            TestResult("ITI-68: Retrieve Binary", TestStatus.FAILED, 134.1, "Status: 404"),
        ]
    else:
        mock_doc_results = [
            TestResult("ITI-67: Find DocumentReferences", TestStatus.PASSED, 78.3, "Found 2 document(s)"),
            TestResult("DocumentReference has status=current", TestStatus.PASSED),
            TestResult("DocumentReference has Binary URL", TestStatus.PASSED, message="Binary/eps-binary-a"),
            TestResult("ITI-68: Retrieve Binary", TestStatus.PASSED, 34.1),
        ]
    
    for r in mock_doc_results:
        print_test_result(r)
        suite.results.append(r)
    
    # Mock Resource Access
    print_section_header("4. Resource Access (QEDm PCC-44)", "◆", Style.SUCCESS)
    if animated:
        wave_animation("Testing resource queries...", 0.6)
    
    if scenario == "failure":
        mock_res_results = [
            TestResult("Resource Access Tests", TestStatus.SKIPPED, message="No patient ID available"),
        ]
    elif scenario == "mixed":
        mock_res_results = [
            TestResult("GET /Condition?patient=...", TestStatus.PASSED, 41.2, "2 result(s)"),
            TestResult("GET /Observation?patient=...", TestStatus.FAILED, 138.7, "Timeout"),
            TestResult("GET /AllergyIntolerance?patient=...", TestStatus.PASSED, 29.4, "1 result(s)"),
            TestResult("GET /MedicationStatement?patient=...", TestStatus.SKIPPED, 25.1, "0 result(s)"),
            TestResult("GET /Encounter?patient=...", TestStatus.FAILED, 233.8, "Status: 503"),
        ]
    else:
        mock_res_results = [
            TestResult("GET /Condition?patient=...", TestStatus.PASSED, 41.2, "2 result(s)"),
            TestResult("GET /Observation?patient=...", TestStatus.PASSED, 38.7, "3 result(s)"),
            TestResult("GET /AllergyIntolerance?patient=...", TestStatus.PASSED, 29.4, "1 result(s)"),
            TestResult("GET /MedicationStatement?patient=...", TestStatus.SKIPPED, 25.1, "0 result(s)"),
            TestResult("GET /Encounter?patient=...", TestStatus.PASSED, 33.8, "1 result(s)"),
        ]
    
    for r in mock_res_results:
        print_test_result(r)
        suite.results.append(r)
    
    # Summary
    print()
    print(f"  {Style.ORANGE}{'═' * 55}{Style.RESET}")
    print_summary_box(suite)
    
    if suite.failed == 0 and animated:
        print_celebration()
    
    # Footer
    print(f"  {Style.GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET}")
    print(f"  {Style.DIM}Mode:{Style.RESET}    {Style.WARNING}MOCK (visual testing){Style.RESET}")
    print(f"  {Style.DIM}Demo UI:{Style.RESET} {Style.CYAN}http://localhost:8083{Style.RESET}")
    print(f"  {Style.DIM}API Base:{Style.RESET} {Style.CYAN}http://localhost:8082{Style.RESET}")
    print(f"  {Style.GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET}")
    print()
    
    return 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="EU Health Data API Demo Suite (Claude Code Style)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ascii_demo.py                    Run full test suite
  python ascii_demo.py --mock             Run with mock data (visual testing)
  python ascii_demo.py --no-animation     Run without animations
  python ascii_demo.py --url http://...   Custom API URL
  python ascii_demo.py --interactive      Interactive menu mode
        """
    )
    
    parser.add_argument(
        "--url", "-u",
        default="http://localhost:8082",
        help="API base URL (default: http://localhost:8082)"
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Disable animations"
    )
    parser.add_argument(
        "--mock", "-m",
        nargs="?",
        const="success",
        default=None,
        choices=["success", "failure", "mixed"],
        help="Run with mock data for visual testing (scenarios: success, failure, mixed)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive menu mode"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mock is not None:
            return run_mock_demo(not args.no_animation, scenario=args.mock)
        elif args.interactive:
            while True:
                choice = interactive_menu()
                if choice == "exit":
                    break
                elif choice == "run_all":
                    run_demo(args.url, not args.no_animation)
                    input(f"\n  {Style.GRAY}Press Enter to continue...{Style.RESET}")
                else:
                    print(f"\n  {Style.WARNING}Individual tests coming soon!{Style.RESET}")
                    time.sleep(1)
        else:
            return run_demo(args.url, not args.no_animation)
    except KeyboardInterrupt:
        print(f"\n\n  {Style.WARNING}{Icons.WARN} Demo interrupted{Style.RESET}\n")
        return 130
    finally:
        show_cursor()

if __name__ == "__main__":
    sys.exit(main() or 0)
