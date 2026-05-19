"""Tkinter-based popup dialogs for Claude Code interactions."""

import json
import sys
import tkinter as tk
from tkinter import ttk


def show_question_dialog(questions: list) -> dict:
    """Show a GUI dialog for Claude Code AskUserQuestion.

    Args:
        questions: List of question objects, each with:
            - question (str): The question text
            - header (str): Short label
            - options (list): List of {label, description, preview?} objects
            - multiSelect (bool): Whether multiple answers allowed

    Returns:
        dict: {"answers": {question_text: answer}, "annotations": {...}}
        or {"action": "cancel"} if user closes the window.
    """
    root = tk.Tk()
    root.title("Claude Code - Question")
    root.resizable(True, True)

    # Center on screen
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w = min(700, sw - 100)
    h = min(600, sh - 100)
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(400, 300)

    result: dict = {"action": "cancel"}
    question_vars: list = []

    # Scrollable canvas
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_frame")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Resize canvas window when container resizes
    def _on_canvas_resize(event):
        canvas.itemconfig("scroll_frame", width=event.width)

    canvas.bind("<Configure>", _on_canvas_resize)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    for qi, q in enumerate(questions):
        question_text = q.get("question", "")
        header = q.get("header", f"Question {qi + 1}")
        options = q.get("options", [])
        multi = q.get("multiSelect", False)

        # Section frame with border
        section = ttk.LabelFrame(scroll_frame, text=header, padding=10)
        section.pack(fill="x", padx=10, pady=(10 if qi == 0 else 5))

        # Question label
        label = ttk.Label(
            section, text=question_text, wraplength=w - 80, font=("", 10, "bold")
        )
        label.pack(anchor="w", pady=(0, 8))

        # Options
        if multi:
            var_list = []
            for oi, opt in enumerate(options):
                var = tk.BooleanVar(value=False)
                var_list.append(var)
                cb = ttk.Checkbutton(
                    section,
                    text=opt.get("label", f"Option {oi + 1}"),
                    variable=var,
                )
                cb.pack(anchor="w", pady=2)
                desc = opt.get("description", "")
                if desc:
                    ttk.Label(
                        section, text=desc, wraplength=w - 120, foreground="gray"
                    ).pack(anchor="w", padx=(24, 0), pady=(0, 4))
            question_vars.append({"question": question_text, "vars": var_list, "multi": True, "options": options})
        else:
            var = tk.StringVar(value="")
            question_vars.append({"question": question_text, "var": var, "multi": False, "options": options})
            for oi, opt in enumerate(options):
                value = opt.get("label", f"Option {oi + 1}")
                rb = ttk.Radiobutton(
                    section, text=opt.get("label", ""), variable=var, value=value
                )
                rb.pack(anchor="w", pady=2)
                desc = opt.get("description", "")
                if desc:
                    ttk.Label(
                        section, text=desc, wraplength=w - 120, foreground="gray"
                    ).pack(anchor="w", padx=(24, 0), pady=(0, 4))

    # Buttons at bottom (outside scroll area)
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="x", padx=10, pady=10)

    def _on_submit():
        answers = {}
        annotations = {}
        for qv in question_vars:
            q_text = qv["question"]
            if qv["multi"]:
                selected = [
                    qv["options"][i]["label"]
                    for i, v in enumerate(qv["vars"])
                    if v.get()
                ]
                answers[q_text] = selected
            else:
                selected = qv["var"].get()
                answers[q_text] = selected if selected else None
        result["action"] = "submit"
        result["answers"] = answers
        result["annotations"] = annotations
        root.destroy()

    def _on_cancel():
        result["action"] = "cancel"
        root.destroy()

    cancel_btn = ttk.Button(btn_frame, text="Cancel", command=_on_cancel)
    cancel_btn.pack(side="right", padx=(5, 0))
    submit_btn = ttk.Button(btn_frame, text="Submit", command=_on_submit)
    submit_btn.pack(side="right")

    # Keyboard shortcuts
    root.bind("<Escape>", lambda e: _on_cancel())
    root.bind("<Control-Return>", lambda e: _on_submit())

    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    root.mainloop()

    return result


def show_permission_dialog(tool_name: str, tool_input: dict) -> dict:
    """Show a permission request popup.

    Args:
        tool_name: Name of the tool requesting permission.
        tool_input: The tool's input parameters.

    Returns:
        dict: {"allowed": True/False, "reason": "..."}
    """
    root = tk.Tk()
    root.title("Claude Code - Permission Required")
    root.resizable(False, False)

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w = 480
    h = 320
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    result: dict = {"allowed": False}

    # Icon / header
    header_frame = ttk.Frame(root)
    header_frame.pack(fill="x", padx=16, pady=(16, 8))

    ttk.Label(
        header_frame, text="⏳ Permission Request", font=("", 12, "bold")
    ).pack(anchor="w")

    # Tool info
    info_frame = ttk.LabelFrame(root, text="Tool", padding=10)
    info_frame.pack(fill="both", expand=True, padx=16, pady=8)

    ttk.Label(
        info_frame, text=f"Claude wants to use:", font=("", 9)
    ).pack(anchor="w")
    ttk.Label(
        info_frame, text=tool_name, font=("", 11, "bold"), foreground="blue"
    ).pack(anchor="w", pady=(2, 8))

    # Show params summary
    if tool_input:
        param_text = json.dumps(tool_input, indent=2, ensure_ascii=False)
        if len(param_text) > 500:
            param_text = param_text[:500] + "\n... (truncated)"
        param_box = tk.Text(info_frame, height=6, width=50, wrap=tk.WORD)
        param_box.insert("1.0", param_text)
        param_box.configure(state="disabled")
        param_box.pack(fill="both", expand=True)

    # Buttons
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="x", padx=16, pady=16)

    def _allow():
        result["allowed"] = True
        root.destroy()

    def _deny():
        result["allowed"] = False
        root.destroy()

    deny_btn = ttk.Button(btn_frame, text="Deny", command=_deny)
    deny_btn.pack(side="right", padx=(5, 0))
    allow_btn = ttk.Button(btn_frame, text="Allow", command=_allow)
    allow_btn.pack(side="right")

    root.bind("<Escape>", lambda e: _deny())
    root.bind("<Return>", lambda e: _allow())

    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    root.mainloop()

    return result
