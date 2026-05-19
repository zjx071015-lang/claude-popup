# Claude Popup

GUI popup dialogs for Claude Code. When Claude asks you a question or requests permission, a native Windows popup dialog appears instead of terminal text prompts.

## Features

- **Question Popups** — `AskUserQuestion` calls render as GUI forms with radio buttons, checkboxes, and option descriptions
- **Permission Popups** — Tool permission requests show an Allow/Deny dialog with tool details
- **No dependencies** — Uses Python's built-in `tkinter`, no `pip install` needed
- **One-command setup** — Single script configures all hooks

## Requirements

- Windows (uses tkinter)
- Python 3.8+
- Claude Code

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/claude-popup.git
cd claude-popup

# 2. Run setup
python setup_hooks.py

# 3. Done — popups will appear on the next Claude Code question
```

To remove the popup hooks and go back to terminal prompts:

```bash
python setup_hooks.py --undo
```

## How It Works

```
Claude Code → PreToolUse Hook → popup-bridge.py → tkinter Dialog → Your Choice → Claude Code
```

The setup script adds `PreToolUse` hooks to `~/.claude/settings.json`. When Claude Code is about to call `AskUserQuestion` or request a tool permission, it invokes the bridge script which renders a GUI popup. Your selection is passed back to Claude Code.

## Project Structure

```
claude-popup/
├── claude_popup/       # Python package
│   ├── __init__.py
│   └── dialog.py       # tkinter dialog implementations
├── scripts/
│   └── popup-bridge.py # CLI bridge for Claude Code hooks
├── setup_hooks.py      # One-time hook configuration
├── pyproject.toml
└── README.md
```

## Manual Hook Configuration

If you prefer to configure hooks manually, add this to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "command": "python \"C:/path/to/claude-popup/scripts/popup-bridge.py\" ask"
      },
      {
        "matcher": "",
        "command": "python \"C:/path/to/claude-popup/scripts/popup-bridge.py\" permission"
      }
    ]
  }
}
```

## License

MIT
