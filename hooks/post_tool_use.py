#!/usr/bin/env python3
"""PostToolUse hook: seal one candle per file edit, detect new git commits."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kline_utils import count_lines, load_data, save_data, now_iso, PROJECT_DIR

FILE_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}


def get_latest_commit() -> dict | None:
    try:
        r = subprocess.run(
            ['git', 'log', '-1', '--format=%H\t%s\t%aI'],
            capture_output=True, text=True, cwd=PROJECT_DIR, timeout=3,
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split('\t', 2)
            if len(parts) == 3:
                return {'hash': parts[0], 'message': parts[1], 'time': parts[2]}
    except Exception:
        pass
    return None


def main():
    hook_input = json.load(sys.stdin)
    if hook_input.get('tool_name', '') not in FILE_TOOLS:
        return

    data = load_data()
    pending = data.pop('pending_open', None)

    open_lines  = pending['lines'] if pending else count_lines()
    close_lines = count_lines()
    delta       = close_lines - open_lines

    candle = {
        'n':          len(data['candles']) + 1,
        'time':       now_iso(),
        'file':       pending['file'] if pending else '',
        'session_id': pending['session_id'] if pending else hook_input.get('session_id', ''),
        'open':       open_lines,
        'close':      close_lines,
        'high':       max(open_lines, close_lines),
        'low':        min(open_lines, close_lines),
        'delta':      delta,
    }
    data['candles'].append(candle)

    commit = get_latest_commit()
    if commit:
        known = {c['hash'] for c in data.get('commits', [])}
        if commit['hash'] not in known:
            commit['after_candle_n'] = candle['n']
            data.setdefault('commits', []).append(commit)

    save_data(data)


if __name__ == '__main__':
    main()
