#!/usr/bin/env python3
"""PreToolUse hook: snapshot line count before the edit (becomes candle open)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kline_utils import count_lines, load_data, save_data, now_iso

FILE_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}


def main():
    hook_input = json.load(sys.stdin)
    if hook_input.get('tool_name', '') not in FILE_TOOLS:
        return

    file_path = hook_input.get('tool_input', {}).get('file_path', '')
    data = load_data()
    data['pending_open'] = {
        'lines':      count_lines(),
        'file':       str(Path(file_path).name) if file_path else '',
        'session_id': hook_input.get('session_id', ''),
        'time':       now_iso(),
    }
    save_data(data)


if __name__ == '__main__':
    main()
