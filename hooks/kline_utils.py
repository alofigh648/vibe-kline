"""Shared utilities for vibe-kline hooks."""
import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── Project directory detection ───────────────────────────────────────────
# Global install  → hooks live in ~/.claude/hooks/  → discover project at runtime
# Project install → hooks live in <proj>/.claude/hooks/ → go 3 levels up

_HOOKS_DIR = Path(__file__).parent
_GLOBAL_HOOKS_DIR = Path.home() / '.claude' / 'hooks'
_IS_GLOBAL = _HOOKS_DIR.resolve() == _GLOBAL_HOOKS_DIR.resolve()

# Where the kline.html template lives in global mode
KLINE_HOME = Path(os.environ.get('KLINE_HOME', Path.home() / '.claude' / 'kline'))


def _find_project_dir() -> Path:
    """Return git root of cwd, or cwd itself."""
    try:
        r = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, cwd=Path.cwd(), timeout=3,
        )
        if r.returncode == 0:
            return Path(r.stdout.strip())
    except Exception:
        pass
    return Path.cwd()


if _IS_GLOBAL:
    PROJECT_DIR = _find_project_dir()
else:
    PROJECT_DIR = _HOOKS_DIR.parent.parent.parent

DATA_FILE   = PROJECT_DIR / '.claude' / 'kline_data.json'
PUBLIC_JSON = PROJECT_DIR / 'kline_data.json'
HTML_FILE   = PROJECT_DIR / 'kline.html'

# ── File filtering ────────────────────────────────────────────────────────
FILE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.c', '.cpp', '.h', '.hpp',
    '.rs', '.rb', '.php', '.swift', '.kt', '.cs', '.html', '.css', '.scss', '.sass',
    '.vue', '.svelte', '.yaml', '.yml', '.toml', '.sh', '.bash', '.sql', '.lua',
}

IGNORE_DIRS = {
    '.git', '.claude', 'node_modules', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'target', 'vendor', '.idea', '.vscode',
    'coverage', '.pytest_cache', '.mypy_cache', '.tox', 'out', '.output',
}

IGNORE_FILES = {'kline.html'}


def count_lines() -> int:
    total = 0
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fname in files:
            if fname in IGNORE_FILES:
                continue
            if Path(fname).suffix.lower() in FILE_EXTENSIONS:
                try:
                    content = (Path(root) / fname).read_bytes()
                    total += content.count(b'\n')
                    if content and not content.endswith(b'\n'):
                        total += 1
                except (OSError, IOError):
                    pass
    return total


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {'candles': [], 'commits': [], 'pending_open': None}


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    export = {'candles': data['candles'], 'commits': data.get('commits', [])}
    PUBLIC_JSON.write_text(json.dumps(export, separators=(',', ':')))
    _ensure_html()
    _update_html(export)


def _ensure_html() -> None:
    """Copy kline.html template to project dir if missing (global-mode convenience)."""
    if HTML_FILE.exists():
        return
    template = KLINE_HOME / 'kline.html'
    if template.exists():
        HTML_FILE.write_text(template.read_text())


def _update_html(export: dict) -> None:
    if not HTML_FILE.exists():
        return
    try:
        html = HTML_FILE.read_text()
        payload = json.dumps(export, separators=(',', ':'))
        new_block = (
            '/* KLINE_DATA_START */\n'
            f'window.KLINE_DATA={payload};\n'
            '/* KLINE_DATA_END */'
        )
        new_html = re.sub(
            r'/\* KLINE_DATA_START \*/.*?/\* KLINE_DATA_END \*/',
            new_block, html, flags=re.DOTALL,
        )
        HTML_FILE.write_text(new_html)
    except (OSError, re.error):
        pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
