#!/usr/bin/env bash
# vibe-kline installer
#
# Usage:
#   ./install.sh                          # interactive
#   ./install.sh --global                 # global install (~/.claude/hooks/)
#   ./install.sh --project [path]         # project install (default: cwd)
#   ./install.sh --init [path]            # copy kline.html to a project (global mode helper)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLOBAL_HOOKS="$HOME/.claude/hooks"
KLINE_HOME="${KLINE_HOME:-$HOME/.claude/kline}"

# ── Colors ────────────────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RESET='\033[0m'

info()    { echo -e "${CYAN}▸${RESET} $*"; }
success() { echo -e "${GREEN}✓${RESET} $*"; }
warn()    { echo -e "${YELLOW}!${RESET} $*"; }
header()  { echo -e "\n${BOLD}$*${RESET}"; }

resolve_path() {
    # Expand ~ and resolve to absolute path
    echo "${1/#\~/$HOME}"
}

copy_hooks() {
    local dest="$1"
    mkdir -p "$dest"
    cp "$SCRIPT_DIR/hooks/"*.py "$dest/"
    chmod +x "$dest/"*.py
    success "Hooks → $dest"
}

print_serve_hint() {
    local dir="$1"
    echo ""
    info "Start the chart server from your project directory:"
    echo ""
    echo "    cd $(realpath "$dir") && python -m http.server 38080"
    echo ""
    info "Then open: ${BOLD}http://localhost:38080/kline.html${RESET}"
    echo ""
}

kline_html_source() {
    # Return the kline.html to use as template (repo copy takes priority)
    if [[ -f "$SCRIPT_DIR/kline.html" ]]; then
        echo "$SCRIPT_DIR/kline.html"
    elif [[ -f "$KLINE_HOME/kline.html" ]]; then
        echo "$KLINE_HOME/kline.html"
    else
        echo ""
    fi
}

# ── Mode: --init (copy kline.html into a project) ─────────────────────────
if [[ "$1" == "--init" ]]; then
    TARGET_DIR="$(resolve_path "${2:-$(pwd)}")"
    header "vibe-kline: init project at $TARGET_DIR"
    src="$(kline_html_source)"
    if [[ -z "$src" ]]; then
        warn "kline.html template not found. Run the installer first."
        exit 1
    fi
    cp "$src" "$TARGET_DIR/kline.html"
    success "kline.html → $TARGET_DIR"
    print_serve_hint "$TARGET_DIR"
    exit 0
fi

# ── Mode selection ────────────────────────────────────────────────────────
header "vibe-kline installer"
echo "Track Claude Code edits as real-time K-line candlestick charts."
echo ""

MODE=""
TARGET_DIR=""

case "$1" in
    --global)  MODE="global" ;;
    --project) MODE="project"; TARGET_DIR="$(resolve_path "${2:-}")" ;;
    "")        ;; # interactive
    *)         warn "Unknown option: $1"; exit 1 ;;
esac

if [[ -z "$MODE" ]]; then
    echo "Choose installation mode:"
    echo ""
    echo "  1) ${BOLD}Global${RESET}   — tracks all projects automatically"
    echo "              hooks → ~/.claude/hooks/"
    echo "              kline.html auto-copied into each project on first edit"
    echo ""
    echo "  2) ${BOLD}Project${RESET}  — tracks a single project only"
    echo "              hooks → <project>/.claude/hooks/"
    echo "              kline.html → <project>/"
    echo ""
    read -rp "Choice [1/2]: " choice
    case "$choice" in
        1) MODE="global" ;;
        2) MODE="project" ;;
        *) warn "Invalid choice."; exit 1 ;;
    esac
fi

# ── Global install ────────────────────────────────────────────────────────
if [[ "$MODE" == "global" ]]; then
    header "Global install"

    for f in pre_tool_use.py post_tool_use.py kline_utils.py; do
        if [[ -f "$GLOBAL_HOOKS/$f" ]]; then
            warn "$GLOBAL_HOOKS/$f already exists and will be overwritten."
        fi
    done
    read -rp "Continue? [y/N] " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

    copy_hooks "$GLOBAL_HOOKS"

    mkdir -p "$KLINE_HOME"
    cp "$SCRIPT_DIR/kline.html" "$KLINE_HOME/kline.html"
    success "Template → $KLINE_HOME/kline.html"

    # Persist KLINE_HOME in shell rc files
    for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [[ -f "$rc" ]] && ! grep -q "KLINE_HOME" "$rc"; then
            printf '\n# vibe-kline\nexport KLINE_HOME="%s"\n' "$KLINE_HOME" >> "$rc"
            success "KLINE_HOME added to $rc"
        fi
    done

    echo ""
    success "Global install complete!"
    echo ""
    info "In any project, start editing with Claude Code, then run:"
    echo ""
    echo "    python -m http.server 38080"
    echo ""
    info "Open: ${BOLD}http://localhost:38080/kline.html${RESET}"
    echo ""
    warn "kline.html is auto-copied to each project on your first edit."
    warn "To copy it immediately: ${BOLD}./install.sh --init [project-path]${RESET}"
fi

# ── Project install ───────────────────────────────────────────────────────
if [[ "$MODE" == "project" ]]; then
    # Prompt for target if not given via CLI or interactive
    if [[ -z "$TARGET_DIR" ]]; then
        echo ""
        read -rp "Project path [$(pwd)]: " raw_input
        TARGET_DIR="$(resolve_path "${raw_input:-$(pwd)}")"
    fi
    TARGET_DIR="${TARGET_DIR:-.}"

    if [[ ! -d "$TARGET_DIR" ]]; then
        warn "Directory not found: $TARGET_DIR"
        exit 1
    fi

    header "Project install → $(realpath "$TARGET_DIR")"

    copy_hooks "$TARGET_DIR/.claude/hooks"

    src="$(kline_html_source)"
    if [[ -n "$src" ]]; then
        cp "$src" "$TARGET_DIR/kline.html"
        success "kline.html → $TARGET_DIR"
    fi

    echo ""
    success "Project install complete!"
    print_serve_hint "$TARGET_DIR"

    echo ""
    info "Add to .gitignore (optional):"
    echo ""
    echo "    kline.html"
    echo "    kline_data.json"
    echo "    .claude/kline_data.json"
fi
