#!/usr/bin/env python3
"""
⚡ REPLA5ER - Web Text & Number Replacer Engine
"""

import sys
import re
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

# --- FLASK WEB SERVER MODE & REST API ---

def create_app():
    """Creates and configures the Flask Web Server & REST API Endpoint."""
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
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"⚡ REPLA5ER Web Application Server Started on port {port}!")
    app.run(host="0.0.0.0", port=port, debug=False)