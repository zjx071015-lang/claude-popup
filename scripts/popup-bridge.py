#!/usr/bin/env python3
"""Bridge script called by Claude Code hooks to display popup dialogs.

Usage:
    python popup-bridge.py ask       # Handles AskUserQuestion hooks
    python popup-bridge.py permission # Handles permission request hooks

Input is read from stdin as JSON (provided by Claude Code's hook system).
Output is written to stdout as JSON.
"""

import json
import os
import sys


def _find_project_root():
    """Find the project root relative to this script."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def handle_ask():
    """Handle AskUserQuestion hook. Displays questions in a popup dialog."""
    project_root = _find_project_root()
    sys.path.insert(0, project_root)

    from claude_popup.dialog import show_question_dialog

    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"action": "cancel", "reason": "no input"}))
        return

    try:
        hook_data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"action": "cancel", "reason": "invalid json"}))
        return

    # Extract questions from hook context
    # The hook provides tool_input which contains the questions
    questions = hook_data.get("tool_input", {}).get("questions", [])

    if not questions:
        print(json.dumps({"action": "cancel", "reason": "no questions found"}))
        return

    result = show_question_dialog(questions)
    print(json.dumps(result, ensure_ascii=False))


def handle_permission():
    """Handle permission request hook. Shows allow/deny popup."""
    project_root = _find_project_root()
    sys.path.insert(0, project_root)

    from claude_popup.dialog import show_permission_dialog

    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"allowed": False, "reason": "no input"}))
        return

    try:
        hook_data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"allowed": False, "reason": "invalid json"}))
        return

    tool_name = hook_data.get("tool_name", "Unknown Tool")
    tool_input = hook_data.get("tool_input", {})

    result = show_permission_dialog(tool_name, tool_input)
    print(json.dumps(result, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: popup-bridge.py <ask|permission>"}))
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "ask":
        handle_ask()
    elif mode == "permission":
        handle_permission()
    else:
        print(json.dumps({"error": f"unknown mode: {mode}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
