#!/usr/bin/env python3
"""One-time setup: configure Claude Code hooks to use popup dialogs.

This script adds PreToolUse hooks to ~/.claude/settings.json that intercept
AskUserQuestion and permission prompts, routing them through the popup bridge.

Run: python setup_hooks.py
Undo: python setup_hooks.py --undo
"""

import json
import os
import sys
from pathlib import Path


SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
POPUP_HOOK_KEY = "claude-popup-bridge"


def get_project_root():
    return Path(__file__).parent.resolve()


def get_bridge_path():
    return get_project_root() / "scripts" / "popup-bridge.py"


def load_settings():
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    print(f"Updated: {SETTINGS_PATH}")


def install():
    settings = load_settings()
    bridge_py = str(get_bridge_path())
    python_exe = sys.executable

    question_hook = {
        "matcher": "AskUserQuestion",
        "command": f'"{python_exe}" "{bridge_py}" ask',
    }

    permission_hook = {
        "matcher": "",
        "command": f'"{python_exe}" "{bridge_py}" permission',
    }

    hooks = settings.get("hooks", {})

    # Add AskUserQuestion hook
    pre_hooks = hooks.get("PreToolUse", [])
    existing_commands = {h.get("command", "") for h in pre_hooks}

    changed = False

    if question_hook["command"] not in existing_commands:
        pre_hooks.append(question_hook)
        changed = True
        print("Added AskUserQuestion popup hook")

    if permission_hook["command"] not in existing_commands:
        pre_hooks.append(permission_hook)
        changed = True
        print("Added permission popup hook")

    hooks["PreToolUse"] = pre_hooks
    settings["hooks"] = hooks

    if changed:
        save_settings(settings)
        print("Setup complete - popup dialogs are now active!")
    else:
        print("Hooks already configured - nothing to do.")


def uninstall():
    settings = load_settings()
    hooks = settings.get("hooks", {})
    pre_hooks = hooks.get("PreToolUse", [])

    bridge_py = str(get_bridge_path())
    original_count = len(pre_hooks)

    pre_hooks = [
        h
        for h in pre_hooks
        if bridge_py not in h.get("command", "")
    ]

    if len(pre_hooks) < original_count:
        hooks["PreToolUse"] = pre_hooks
        if pre_hooks:
            settings["hooks"] = hooks
        elif "hooks" in settings:
            del settings["hooks"]
        save_settings(settings)
        print("Removed popup hooks - back to default terminal prompts.")
    else:
        print("No popup hooks found - nothing to undo.")


def main():
    if "--undo" in sys.argv or "-u" in sys.argv:
        uninstall()
    else:
        print("=" * 60)
        print("  Claude Popup - Setup")
        print("=" * 60)
        print()
        install()
        print()
        print("Tip: run 'python setup_hooks.py --undo' to remove popup hooks.")


if __name__ == "__main__":
    main()
