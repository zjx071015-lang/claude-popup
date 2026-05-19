#!/usr/bin/env python3
"""Bridge script called by Claude Code hooks to display popup dialogs.

Usage:
    python popup-bridge.py ask       # Handles AskUserQuestion hooks
    python popup-bridge.py permission # Handles permission request hooks

Input is read from stdin as JSON (provided by Claude Code's hook system).
Output is written to stdout as JSON.

Exit codes:
    0 = allow/answered (tool proceeds)
    1 = denied/cancelled (tool blocked, reason on stderr)
"""

import json
import os
import sys


def _find_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def handle_ask():
    """Handle AskUserQuestion hook. Displays questions in a popup dialog."""
    project_root = _find_project_root()
    sys.path.insert(0, project_root)

    from claude_popup.dialog import show_question_dialog

    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("没有收到输入数据\n")
        sys.exit(1)

    try:
        hook_data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write("无法解析 JSON 输入\n")
        sys.exit(1)

    questions = hook_data.get("tool_input", {}).get("questions", [])

    if not questions:
        sys.stderr.write("未找到问题数据\n")
        sys.exit(1)

    result = show_question_dialog(questions)

    if result.get("action") == "cancel":
        sys.stderr.write("用户取消了弹窗\n")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


def handle_permission():
    """Handle permission request hook. Shows allow/deny popup."""
    project_root = _find_project_root()
    sys.path.insert(0, project_root)

    from claude_popup.dialog import show_permission_dialog

    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("没有收到输入数据\n")
        sys.exit(1)

    try:
        hook_data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write("无法解析 JSON 输入\n")
        sys.exit(1)

    tool_name = hook_data.get("tool_name", "未知工具")
    tool_input = hook_data.get("tool_input", {})

    result = show_permission_dialog(tool_name, tool_input)

    if result.get("allowed"):
        sys.exit(0)
    else:
        sys.stderr.write("用户在弹窗中拒绝了权限请求\n")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("用法: popup-bridge.py <ask|permission>\n")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "ask":
        handle_ask()
    elif mode == "permission":
        handle_permission()
    else:
        sys.stderr.write(f"未知模式: {mode}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
