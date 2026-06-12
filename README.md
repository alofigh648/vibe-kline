# vibe-kline

> Real-time K-line candlestick charts for your Claude Code sessions.  
> Every file edit becomes a candle. Watch your coding session unfold like a trading chart.

[中文文档](README.zh.md)

---

## What it does

`vibe-kline` hooks into [Claude Code](https://claude.ai/code) and records each file edit as a candlestick:

- **Open / Close** — total project line count before and after the edit
- **Delta** — lines added (green) or removed (red)
- **Session bands** — alternating tints per conversation
- **Commit markers** — gold ◆ on git commits, hover for message and hash
- **Activity heatmap** — 14-day edit intensity grid by hour of day

The chart polls for new data automatically — keep it open in a tab while you code.

## Requirements

- Python 3.9+
- [Claude Code](https://claude.ai/code)
- Git (recommended; falls back to `cwd` without it)

## Install

Clone vibe-kline **anywhere on your machine** — it does not need to live inside your project:

```bash
git clone https://github.com/alofigh648/vibe-kline.git ~/tools/vibe-kline
cd ~/tools/vibe-kline
./install.sh
```

Choose between two modes:

### Global — all projects (recommended)

```bash
./install.sh --global
```

Hooks are installed to `~/.claude/hooks/` and run for every Claude Code session on your machine. `kline.html` is auto-copied into each project on your first edit, or immediately with:

```bash
./install.sh --init /path/to/my-project
```

### Project — single project only

```bash
./install.sh --project /path/to/my-project
```

Hooks and `kline.html` go into the specified project directory. No path? Defaults to the current directory:

```bash
cd /path/to/my-project
./install.sh --project
```

## Usage

**1. Start the server** from your project directory (once per session):

```bash
cd /path/to/my-project
python -m http.server 38080
```

**2. Open the chart:**

```
http://localhost:38080/kline.html
```

Start coding with Claude Code — candles appear in real time.

## Chart features

| Feature | Description |
|---|---|
| K-line candles | Color = file type · Brightness = delta magnitude |
| MA line | Adaptive moving average · click legend to toggle |
| Bollinger Bands | Click the **BB带** button |
| Session bands | Each Claude Code conversation gets its own color band |
| Commit markers | ◆ at git commits · hover for hash and message |
| Time gap badges | Amber badge when >30 min gap between edits |
| Activity heatmap | 14-day grid (hour × day) in the sidebar |
| Replay | ▶ button to replay the entire session |
| File focus | Click a file in the leaderboard to highlight its candles |
| Export | Save the current view as PNG |

## Keyboard shortcuts

| Key | Action |
|---|---|
| `← →` | Navigate candles |
| `+` / `-` | Zoom in / out |
| `Space` | Jump to latest |
| `Home` | Jump to first candle |
| `Esc` | Cancel file focus |

## Data files

| File | Description |
|---|---|
| `.claude/kline_data.json` | Full internal data (keep private) |
| `kline_data.json` | Public export polled by the chart |
| `kline.html` | Self-contained chart viewer |

Suggested `.gitignore` additions:

```
kline.html
kline_data.json
.claude/kline_data.json
```

Or commit `kline.html` to share a session snapshot with your team.

## How it works

```
Claude Code edit
    │
    ├── PreToolUse hook  → snapshot line count  (candle open)
    │
    └── PostToolUse hook → count again (close) → append candle → patch kline.html
                                ↑
                       kline_utils.py resolves project root via git or cwd
```

Data is patched directly into `kline.html` between marker comments — no database, no build step.

## Uninstall

**Global:**
```bash
rm ~/.claude/hooks/pre_tool_use.py \
   ~/.claude/hooks/post_tool_use.py \
   ~/.claude/hooks/kline_utils.py
```

**Project:**
```bash
rm .claude/hooks/pre_tool_use.py \
   .claude/hooks/post_tool_use.py \
   .claude/hooks/kline_utils.py
```

## License

MIT
