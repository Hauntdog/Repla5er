#!/usr/bin/env python3
"""
⚡ REPLA5ER - Live & Interactive Terminal/GUI/Web Text & Number Replacer
Usage:
  1. CLI Stream Mode:
     echo "status is OFFLINE" | ./replacer.py OFFLINE ONLINE
     echo "value is 42" | ./replacer.py 42 99
     cat data.txt | ./replacer.py 100 200 -w
     cat log.txt | ./replacer.py error warning -i

  2. Graphical GUI Mode:
     ./replacer.py --gui

  3. Terminal TUI Mode:
     ./replacer.py --tui

  4. Interactive CLI (Default if stdin is TTY & no args):
     ./replacer.py
"""

import sys
import re
import argparse
import os

# --- CORE REPLACEMENT ENGINE ---

def replace_text(text: str, find_str: str, replace_str: str,
                 whole_word: bool = True,
                 ignore_case: bool = False,
                 math_mode: bool = False,
                 min_val: float = None,
                 max_val: float = None) -> tuple[str, int]:
    """
    Replaces words or numbers in `text` based on find/replace parameters or math formulas.
    Returns (transformed_text, count_of_replacements).
    """
    if not text:
        return "", 0

    count = 0

    # Helper function to compute math replacements (+10, -5, *2, /2, etc.)
    def apply_math(val: float, expr: str) -> float:
        expr = expr.strip()
        if expr.startswith('+'):
            return val + float(expr[1:])
        elif expr.startswith('-'):
            return val - float(expr[1:])
        elif expr.startswith('*'):
            return val * float(expr[1:])
        elif expr.startswith('/'):
            denom = float(expr[1:])
            return val / denom if denom != 0 else val
        elif 'x' in expr or 'n' in expr:
            # simple formula e.g. x + 10
            safe_expr = expr.replace('x', str(val)).replace('n', str(val))
            # Safe evaluation of basic arithmetic
            if re.match(r'^[0-9.\s+\-*/()]+$', safe_expr):
                return float(eval(safe_expr))
        try:
            return float(expr)
        except ValueError:
            return val

    # Mode A: Math mode or replace ALL numbers in range
    if math_mode or (not find_str and (min_val is not None or max_val is not None)):
        # Match any floating point or integer number
        pattern = re.compile(r'(?<![\d.])(-?\d+(?:\.\d+)?)(?![\d.])')

        def replacer_fn(match):
            nonlocal count
            num_str = match.group(1)
            try:
                num_val = float(num_str) if '.' in num_str else int(num_str)
                # Check range filter if specified
                if min_val is not None and num_val < min_val:
                    return num_str
                if max_val is not None and num_val > max_val:
                    return num_str

                count += 1
                if math_mode and replace_str:
                    res = apply_math(float(num_val), replace_str)
                    # Preserve integer formatting if original was integer and result is integer
                    if isinstance(num_val, int) and res.is_integer():
                        return str(int(res))
                    return f"{res:.4g}"
                else:
                    return replace_str if replace_str else num_str
            except Exception:
                return num_str

        new_text = pattern.sub(replacer_fn, text)
        return new_text, count

    # Mode B: Specific target find string (words or numbers)
    if not find_str:
        return text, 0

    escaped_find = re.escape(find_str)
    flags = re.IGNORECASE if ignore_case else 0

    if whole_word:
        # Check if find_str is a pure number pattern (e.g. 42 or -3.14)
        if re.match(r'^-?\d+(?:\.\d+)?$', find_str):
            pattern_str = rf'(?<![\d.]){escaped_find}(?![\d.])'
        else:
            # For words/text: apply word boundary checks
            prefix = r'(?<!\w)' if re.match(r'^\w', find_str) else ''
            suffix = r'(?!\w)' if re.search(r'\w$', find_str) else ''
            pattern_str = f'{prefix}{escaped_find}{suffix}'
        pattern = re.compile(pattern_str, flags)
    else:
        pattern = re.compile(escaped_find, flags)

    def target_replacer(match):
        nonlocal count
        count += 1
        matched_str = match.group(0)
        if replace_str.startswith(('+', '-', '*', '/')) and replace_str[1:].strip().replace('.', '', 1).isdigit():
            # Support math modifier on specific target find e.g. target 42 -> replace +10 => 52
            try:
                orig = float(matched_str)
                res = apply_math(orig, replace_str)
                return str(int(res)) if res.is_integer() else f"{res:.4g}"
            except ValueError:
                return replace_str
        return replace_str

    new_text = pattern.sub(target_replacer, text)
    return new_text, count

# Alias for backwards compatibility
replace_numbers_in_text = replace_text


# --- TKINTER DARK TERMINAL GUI MODE ---

def launch_gui(initial_text: str = ""):
    """Launches modern Dark Terminal GUI using Tkinter."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
    except ImportError:
        print("[Error] Tkinter library is not installed or supported in this environment.", file=sys.stderr)
        sys.exit(1)

    root = tk.Tk()
    root.title("⚡ REPLA5ER - Terminal Text & Number Replacer GUI")
    root.geometry("980x680")
    root.minsize(750, 500)

    # Color Palette - Dark Cyber Terminal Aesthetic
    BG_DARK = "#0f172a"        # Deep slate navy
    BG_CARD = "#1e293b"        # Card frame background
    BG_INPUT = "#0f172a"       # Text area background
    FG_TEXT = "#f8fafc"        # Crisp white text
    FG_MUTED = "#94a3b8"       # Muted gray text
    ACCENT_CYAN = "#38bdf8"    # Neon cyan
    ACCENT_GREEN = "#10b981"   # Emerald green
    ACCENT_ROSE = "#f43f5e"    # Rose red accent
    BORDER_COL = "#334155"     # Border slate

    root.configure(bg=BG_DARK)

    # Styling for TTK Widgets
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=BG_DARK)
    style.configure("Card.TFrame", background=BG_CARD, relief="flat", borderwidth=1)
    style.configure("TLabel", background=BG_CARD, foreground=FG_TEXT, font=("Inter", 10))
    style.configure("Header.TLabel", background=BG_DARK, foreground=ACCENT_CYAN, font=("Monospace", 16, "bold"))
    style.configure("SubHeader.TLabel", background=BG_DARK, foreground=FG_MUTED, font=("Inter", 9))
    style.configure("TCheckbutton", background=BG_CARD, foreground=FG_TEXT, font=("Inter", 9))
    style.map("TCheckbutton", background=[("active", BG_CARD)], foreground=[("active", ACCENT_CYAN)])

    # Custom Monospace Text Font
    MONO_FONT = ("DejaVu Sans Mono", 10) if sys.platform.startswith("linux") else ("Consolas", 10)

    # --- TOP HEADER ---
    header_frame = tk.Frame(root, bg=BG_DARK, pady=10, padx=15)
    header_frame.pack(fill="x")

    lbl_title = tk.Label(header_frame, text="⚡ REPLA5ER", font=("Monospace", 18, "bold"), fg=ACCENT_CYAN, bg=BG_DARK)
    lbl_title.pack(side="left")

    lbl_subtitle = tk.Label(header_frame, text=" | Live Interactive Terminal Text & Number Replacer", font=("Inter", 11), fg=FG_MUTED, bg=BG_DARK)
    lbl_subtitle.pack(side="left", padx=5, pady=4)

    # --- CONTROLS PANEL ---
    controls_card = tk.Frame(root, bg=BG_CARD, highlightbackground=BORDER_COL, highlightthickness=1, bd=0, padx=15, pady=12)
    controls_card.pack(fill="x", padx=15, pady=5)

    # Grid layout for inputs
    # Row 0: Find & Replace
    tk.Label(controls_card, text="Find (Word / Number):", bg=BG_CARD, fg=FG_TEXT, font=("Inter", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=4)
    ent_find = tk.Entry(controls_card, bg=BG_INPUT, fg=ACCENT_CYAN, insertbackground=FG_TEXT,
                        font=MONO_FONT, relief="solid", bd=1, highlightcolor=ACCENT_CYAN)
    ent_find.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
    ent_find.insert(0, "42")

    tk.Label(controls_card, text="Replace (Word / Number / Math e.g. +10):", bg=BG_CARD, fg=FG_TEXT, font=("Inter", 9, "bold")).grid(row=0, column=2, sticky="w", padx=10, pady=4)
    ent_replace = tk.Entry(controls_card, bg=BG_INPUT, fg=ACCENT_GREEN, insertbackground=FG_TEXT,
                           font=MONO_FONT, relief="solid", bd=1, highlightcolor=ACCENT_GREEN)
    ent_replace.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
    ent_replace.insert(0, "99")

    # Row 1: Options (Whole word, Ignore case, Math mode)
    var_whole = tk.BooleanVar(value=True)
    chk_whole = tk.Checkbutton(controls_card, text="Whole words/numbers only (-w)", variable=var_whole,
                               bg=BG_CARD, fg=FG_TEXT, selectcolor=BG_DARK, activebackground=BG_CARD,
                               activeforeground=ACCENT_CYAN, font=("Inter", 9))
    chk_whole.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=4)

    var_ignore = tk.BooleanVar(value=False)
    chk_ignore = tk.Checkbutton(controls_card, text="Ignore case (-i)", variable=var_ignore,
                                bg=BG_CARD, fg=FG_TEXT, selectcolor=BG_DARK, activebackground=BG_CARD,
                                activeforeground=ACCENT_CYAN, font=("Inter", 9))
    chk_ignore.grid(row=1, column=2, sticky="w", padx=10, pady=4)

    var_math = tk.BooleanVar(value=False)
    chk_math = tk.Checkbutton(controls_card, text="Math Mode (all numbers)", variable=var_math,
                              bg=BG_CARD, fg=FG_TEXT, selectcolor=BG_DARK, activebackground=BG_CARD,
                              activeforeground=ACCENT_GREEN, font=("Inter", 9))
    chk_math.grid(row=1, column=3, sticky="w", padx=5, pady=4)

    # Row 2: Range Filter
    var_range = tk.BooleanVar(value=False)
    chk_range = tk.Checkbutton(controls_card, text="Range Filter:", variable=var_range,
                               bg=BG_CARD, fg=FG_TEXT, selectcolor=BG_DARK, activebackground=BG_CARD,
                               activeforeground=ACCENT_CYAN, font=("Inter", 9))
    chk_range.grid(row=2, column=0, sticky="w", padx=5, pady=4)

    range_frame = tk.Frame(controls_card, bg=BG_CARD)
    range_frame.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=4)

    tk.Label(range_frame, text="Min:", bg=BG_CARD, fg=FG_MUTED, font=("Inter", 8)).pack(side="left")
    ent_min = tk.Entry(range_frame, width=8, bg=BG_INPUT, fg=FG_TEXT, font=MONO_FONT, bd=1, relief="solid")
    ent_min.pack(side="left", padx=4)

    tk.Label(range_frame, text="Max:", bg=BG_CARD, fg=FG_MUTED, font=("Inter", 8)).pack(side="left", padx=(10, 0))
    ent_max = tk.Entry(range_frame, width=8, bg=BG_INPUT, fg=FG_TEXT, font=MONO_FONT, bd=1, relief="solid")
    ent_max.pack(side="left", padx=4)

    controls_card.columnconfigure(1, weight=1)
    controls_card.columnconfigure(3, weight=1)

    # --- BUTTON ACTIONS BAR ---
    btn_bar = tk.Frame(root, bg=BG_DARK, padx=15, pady=6)
    btn_bar.pack(fill="x")

    # Custom styled flat buttons
    def make_btn(parent, text, command, bg_col, fg_col="#000000"):
        btn = tk.Button(parent, text=text, command=command, bg=bg_col, fg=fg_col,
                        font=("Inter", 9, "bold"), relief="flat", bd=0, padx=12, pady=5,
                        activebackground=bg_col, cursor="hand2")
        return btn

    # --- TEXT PANES (SPLIT INPUT & OUTPUT PREVIEW) ---
    panes_frame = tk.Frame(root, bg=BG_DARK, padx=15, pady=5)
    panes_frame.pack(fill="both", expand=True)

    # Input Side
    left_frame = tk.Frame(panes_frame, bg=BG_CARD, highlightbackground=BORDER_COL, highlightthickness=1)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

    lbl_in = tk.Label(left_frame, text=" 📥 INPUT TEXT / STDIN ", bg=BG_CARD, fg=ACCENT_CYAN, font=("Monospace", 9, "bold"), anchor="w", pady=4)
    lbl_in.pack(fill="x")

    txt_input = tk.Text(left_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground=ACCENT_CYAN,
                        font=MONO_FONT, bd=0, padx=10, pady=8, wrap="word", undo=True)
    txt_input.pack(fill="both", expand=True)

    # Output Side
    right_frame = tk.Frame(panes_frame, bg=BG_CARD, highlightbackground=BORDER_COL, highlightthickness=1)
    right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

    lbl_out = tk.Label(right_frame, text=" 📤 LIVE TRANSFORMED OUTPUT ", bg=BG_CARD, fg=ACCENT_GREEN, font=("Monospace", 9, "bold"), anchor="w", pady=4)
    lbl_out.pack(fill="x")

    txt_output = tk.Text(right_frame, bg=BG_INPUT, fg=ACCENT_GREEN, insertbackground=FG_TEXT,
                         font=MONO_FONT, bd=0, padx=10, pady=8, wrap="word")
    txt_output.pack(fill="both", expand=True)

    # Status Bar
    status_bar = tk.Frame(root, bg=BG_CARD, height=28, padx=15)
    status_bar.pack(fill="x", side="bottom")

    lbl_status = tk.Label(status_bar, text="Ready | 0 replacements", bg=BG_CARD, fg=FG_MUTED, font=("Inter", 9))
    lbl_status.pack(side="left", pady=3)

    # --- LIVE UPDATE CONTROLLER ---
    def update_transformation(*args):
        inp = txt_input.get("1.0", "end-1c")
        find_val = ent_find.get()
        replace_val = ent_replace.get()
        whole = var_whole.get()
        ignore = var_ignore.get()
        is_math = var_math.get()

        min_v = float(ent_min.get()) if var_range.get() and ent_min.get().strip() else None
        max_v = float(ent_max.get()) if var_range.get() and ent_max.get().strip() else None

        res_text, count = replace_text(
            inp, find_val, replace_val,
            whole_word=whole, ignore_case=ignore, math_mode=is_math,
            min_val=min_v, max_val=max_v
        )

        txt_output.delete("1.0", "end")
        txt_output.insert("1.0", res_text)

        lbl_status.config(text=f"Status: Done | {count} instances replaced")

    # Bind events for auto live preview
    txt_input.bind("<KeyRelease>", update_transformation)
    ent_find.bind("<KeyRelease>", update_transformation)
    ent_replace.bind("<KeyRelease>", update_transformation)
    chk_whole.config(command=update_transformation)
    chk_ignore.config(command=update_transformation)
    chk_math.config(command=update_transformation)
    chk_range.config(command=update_transformation)
    ent_min.bind("<KeyRelease>", update_transformation)
    ent_max.bind("<KeyRelease>", update_transformation)

    # Button handlers
    def action_copy():
        out_text = txt_output.get("1.0", "end-1c")
        root.clipboard_clear()
        root.clipboard_append(out_text)
        messagebox.showinfo("Copied", "Transformed text copied to clipboard!")

    def action_load_file():
        path = filedialog.askopenfilename(title="Open Text File")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                txt_input.delete("1.0", "end")
                txt_input.insert("1.0", content)
                update_transformation()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def action_save_file():
        path = filedialog.asksaveasfilename(title="Save Output File", defaultextension=".txt")
        if path:
            try:
                out_text = txt_output.get("1.0", "end-1c")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out_text)
                messagebox.showinfo("Saved", f"File saved successfully to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def action_clear():
        txt_input.delete("1.0", "end")
        update_transformation()

    # Populate Button Bar
    btn_copy = make_btn(btn_bar, "📋 Copy Output", action_copy, ACCENT_CYAN, "#0f172a")
    btn_copy.pack(side="left", padx=(0, 6))

    btn_load = make_btn(btn_bar, "📁 Load File", action_load_file, "#3b82f6", "#ffffff")
    btn_load.pack(side="left", padx=6)

    btn_save = make_btn(btn_bar, "💾 Save Output", action_save_file, ACCENT_GREEN, "#0f172a")
    btn_save.pack(side="left", padx=6)

    btn_clear = make_btn(btn_bar, "🧹 Clear Input", action_clear, "#64748b", "#ffffff")
    btn_clear.pack(side="left", padx=6)

    btn_exit = make_btn(btn_bar, "❌ Exit", root.destroy, ACCENT_ROSE, "#ffffff")
    btn_exit.pack(side="right")

    # Set initial sample text if input text empty
    if initial_text:
        txt_input.insert("1.0", initial_text)
    else:
        sample = ("Sample Data Log:\n"
                  "Server 1: status OFFLINE, port 8080, latency 42ms, active users: 100\n"
                  "Server 2: status ONLINE, port 8081, latency 42ms, active users: 250\n"
                  "Global multiplier factor: 3.14159\n"
                  "Target id 42 in line 4242.\n"
                  "An apple and two apples.")
        txt_input.insert("1.0", sample)

    update_transformation()
    root.mainloop()


# --- CURSES TERMINAL INTERACTIVE TUI MODE ---

def launch_tui(stdscr):
    """Launches Curses-based interactive Terminal UI directly in console."""
    import curses

    curses.curs_set(1)
    curses.use_default_colors()

    # Define color pairs if supported
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, -1)     # Header/Titles
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Output text
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Highlights / Inputs
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # Commands
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN) # Status bar

    find_str = "42"
    replace_str = "99"
    input_lines = [
        "Interactive Terminal TUI Mode",
        "Type or edit text here (Press [F2], [F3], or [TAB] to switch)",
        "Example line 1: status is OFFLINE and 42 items pending.",
        "Example line 2: server 1 port 8080 latency 42ms.",
        "Example line 3: total 100 apples."
    ]

    active_field = 0  # 0: Find, 1: Replace, 2: Input Text
    whole_word = True
    ignore_case = False

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Draw Banner Header
        title = " ⚡ REPLA5ER TUI - Interactive Terminal Text & Number Replacer "
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(0, 0, title.ljust(width))
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        # Draw Inputs Panel
        stdscr.addstr(2, 2, "Find (Word/Number): ", curses.color_pair(1) | curses.A_BOLD)
        f_attr = curses.color_pair(3) | curses.A_UNDERLINE if active_field == 0 else curses.A_NORMAL
        stdscr.addstr(2, 22, find_str.ljust(15), f_attr)

        stdscr.addstr(3, 2, "Replace (Word/Math): ", curses.color_pair(2) | curses.A_BOLD)
        r_attr = curses.color_pair(3) | curses.A_UNDERLINE if active_field == 1 else curses.A_NORMAL
        stdscr.addstr(3, 22, replace_str.ljust(15), r_attr)

        w_str = "[X] Whole Words Only" if whole_word else "[ ] Whole Words Only"
        i_str = "[X] Ignore Case" if ignore_case else "[ ] Ignore Case"
        stdscr.addstr(4, 2, f"{w_str}    {i_str}", curses.color_pair(4))

        # Split Windows
        raw_text = "\n".join(input_lines)
        transformed_text, total_count = replace_text(raw_text, find_str, replace_str, whole_word=whole_word, ignore_case=ignore_case)

        box_height = max(5, (height - 9) // 2)

        # Input Box
        stdscr.addstr(6, 2, "--- INPUT TEXT (Active)" if active_field == 2 else "--- INPUT TEXT", curses.color_pair(1))
        for idx, line in enumerate(input_lines[:box_height]):
            if 7 + idx < height - 2:
                stdscr.addstr(7 + idx, 4, line[:width - 6])

        # Output Box
        out_start = 8 + min(len(input_lines), box_height)
        if out_start < height - 2:
            stdscr.addstr(out_start, 2, f"--- TRANSFORMED OUTPUT ({total_count} replacements) ---", curses.color_pair(2) | curses.A_BOLD)
            out_lines = transformed_text.splitlines()
            for idx, line in enumerate(out_lines[:box_height]):
                if out_start + 1 + idx < height - 1:
                    stdscr.addstr(out_start + 1 + idx, 4, line[:width - 6], curses.color_pair(2))

        # Footer Status Bar
        status = " [TAB]: Switch Field | [F2]: Whole Word | [F3]: Ignore Case | [ESC/q]: Quit "
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(height - 1, 0, status.ljust(width))
        stdscr.attroff(curses.color_pair(5))

        stdscr.refresh()

        # Handle Keyboard Input
        try:
            ch = stdscr.getch()
        except KeyboardInterrupt:
            break

        if ch in (27, ord('q'), ord('Q')): # ESC or q
            break
        elif ch in (9, curses.KEY_RIGHT): # TAB
            active_field = (active_field + 1) % 3
        elif ch in (curses.KEY_F2, ord('w')):
            whole_word = not whole_word
        elif ch in (curses.KEY_F3, ord('i')):
            ignore_case = not ignore_case
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if active_field == 0 and len(find_str) > 0:
                find_str = find_str[:-1]
            elif active_field == 1 and len(replace_str) > 0:
                replace_str = replace_str[:-1]
            elif active_field == 2 and input_lines:
                if input_lines[-1]:
                    input_lines[-1] = input_lines[-1][:-1]
                elif len(input_lines) > 1:
                    input_lines.pop()
        elif 32 <= ch <= 126: # Printable ascii
            char = chr(ch)
            if active_field == 0:
                find_str += char
            elif active_field == 1:
                replace_str += char
            elif active_field == 2:
                if not input_lines:
                    input_lines.append("")
                input_lines[-1] += char
        elif ch in (10, 13): # Enter
            if active_field == 2:
                input_lines.append("")
            else:
                active_field = (active_field + 1) % 3


def run_tui_wrapper():
    """Wrapper to initialize curses cleanly."""
    try:
        import curses
        curses.wrapper(launch_tui)
    except Exception as e:
        print(f"[Error launching TUI]: {e}", file=sys.stderr)
        sys.exit(1)


# --- FLASK WEB SERVER MODE & REST API ---

def launch_web(port: int = 5000, host: str = "0.0.0.0"):
    """Launches Flask Web Server & REST API Endpoint."""
    try:
        from flask import Flask, request, jsonify, render_template
    except ImportError:
        print("[Error] Flask library is required for web mode. Install via 'pip install flask'", file=sys.stderr)
        sys.exit(1)

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, template_folder=template_dir)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/replace', methods=['POST'])
    def api_replace():
        data = request.get_json(silent=True) or {}
        text = data.get('text', '')
        find_str = data.get('find', '')
        replace_str = data.get('replace', '')
        whole_word = data.get('whole_word', True)
        ignore_case = data.get('ignore_case', False)
        math_mode = data.get('math_mode', False)
        min_val = data.get('min_val', None)
        max_val = data.get('max_val', None)

        if min_val is not None:
            try: min_val = float(min_val)
            except (ValueError, TypeError): min_val = None

        if max_val is not None:
            try: max_val = float(max_val)
            except (ValueError, TypeError): max_val = None

        transformed, count = replace_text(
            text, find_str, replace_str,
            whole_word=whole_word,
            ignore_case=ignore_case,
            math_mode=math_mode,
            min_val=min_val,
            max_val=max_val
        )

        return jsonify({
            'transformed': transformed,
            'count': count,
            'status': 'success'
        })

    print(f"\n⚡ REPLA5ER Web Application Server Started!")
    print(f"👉 Web UI URL:   http://localhost:{port}")
    print(f"👉 REST API URL: http://localhost:{port}/api/replace")
    print("Press CTRL+C to stop server.\n")

    app.run(host=host, port=port, debug=False)


def daemonize(port: int = 5000):
    """Launches the Web App process completely detached in the background."""
    import subprocess
    cmd = [sys.executable, os.path.abspath(__file__), "--web", "--port", str(port)]
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_server.log")

    with open(log_file, "a") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=f, start_new_session=True)

    print(f"⚡ REPLA5ER Web App launched in background daemon mode!")
    print(f"📌 Process PID: {proc.pid}")
    print(f"👉 Web UI URL:   http://localhost:{port}")
    print(f"📝 Output Log:   {log_file}")
    print(f"💡 To stop:      kill {proc.pid}\n")


# --- MAIN ENTRY POINT ---

def main():
    parser = argparse.ArgumentParser(description="⚡ REPLA5ER - Interactive Terminal, GUI & Web Text/Number Replacer")
    parser.add_argument("old", nargs="?", default=None, help="Word or number to find (e.g. OFFLINE or 42)")
    parser.add_argument("new", nargs="?", default=None, help="Word, number or math formula (e.g. ONLINE, 99 or +10)")
    parser.add_argument("-w", "--word", action="store_true", default=True,
                        help="Match whole words/numbers only (default: True)")
    parser.add_argument("--partial", action="store_false", dest="word",
                        help="Allow partial word/number matches (e.g. apple inside apples or 42 inside 142)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Enable case-insensitive text matching")
    parser.add_argument("-m", "--math", action="store_true",
                        help="Enable math formula mode across all numbers")
    parser.add_argument("--gui", action="store_true",
                        help="Launch Graphical Dark Terminal GUI window")
    parser.add_argument("--tui", action="store_true",
                        help="Launch interactive Curses Terminal UI")
    parser.add_argument("--web", action="store_true",
                        help="Launch Cyberpunk Dark Terminal Web Application Server")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port number for Web Application Server (default: 5000)")
    parser.add_argument("-d", "--daemon", action="store_true",
                        help="Run Web Application server in background as a daemon process")

    args = parser.parse_args()

    # Explicit mode selection
    if args.daemon:
        daemonize(port=args.port)
        return

    if args.web:
        launch_web(port=args.port)
        return

    if args.gui:
        launch_gui()
        return

    if args.tui:
        run_tui_wrapper()
        return

    # If stdin is connected to a pipe / file stream OR positional args provided
    if not sys.stdin.isatty() or (args.old is not None and args.new is not None):
        if args.old is None or args.new is None:
            if not args.math:
                print("Error: Both <old> and <new> arguments are required for CLI stream mode.", file=sys.stderr)
                parser.print_help()
                sys.exit(1)

        # Process piped input line-by-line
        try:
            for line in sys.stdin:
                transformed, _ = replace_text(
                    line,
                    args.old or "",
                    args.new or "",
                    whole_word=args.word,
                    ignore_case=args.ignore_case,
                    math_mode=args.math
                )
                sys.stdout.write(transformed)
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n[Interrupted]", file=sys.stderr)
            sys.exit(0)
        return

    # Default interactive launcher if executed without arguments in TTY
    print("⚡ REPLA5ER - No CLI arguments provided.")
    print("Opening Graphical Dark Terminal GUI... (Use --web for Web App, --tui for terminal mode, or --help)")
    launch_gui()


if __name__ == "__main__":
    main()