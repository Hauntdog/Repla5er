# ⚡ REPLA5ER

> **The Ultimate Interactive Text, Word & Number Transformation Engine for Terminal, GUI & Web**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-slate.svg)]()
[![Web API](https://img.shields.io/badge/REST%20API-Flask%20Online-38bdf8.svg)]()

**REPLA5ER** is a feature-packed, high-performance text and number replacer designed for developers, system administrators, and data analysts. Whether you need a lightning-fast UNIX stream processor, a dark cyber desktop GUI, an in-terminal Curses TUI, or a full-stack REST API web server, REPLA5ER does it all.

---

## 🌟 Key Features

- 🔤 **Smart Word Replacement**: Replace text and words with whole-word boundary matching (`\bword\b`) or partial substring matching (`--partial`).
- 🔠 **Case-Insensitive Matching (`-i`)**: Match and replace words regardless of capitalization (e.g. `OFFLINE`, `offline`, `Offline`).
- 🔢 **Intelligent Number Engine**: Safely replaces whole numbers without corrupting decimals or larger digits (e.g. replaces `42` without touching `142` or `42.5`).
- 🧮 **Math Formula Modifier Mode**: Apply arithmetic calculations (`+10`, `-5`, `*2`, `/2`) directly to target numbers or across all numeric values in a text stream.
- 🎯 **Numeric Range Filtering**: Target only numbers within a specific minimum and maximum threshold (`min_val` to `max_val`).
- 🖥️ **4 Versatile Execution Modes**:
  1. **CLI Pipe & Stream Mode**: Process stdin/stdout streams with lightning speed.
  2. **Graphical Tkinter GUI Mode (`--gui`)**: Dark Cyber slate interface with live instant preview, file load/save, and copy actions.
  3. **Curses Terminal TUI Mode (`--tui`)**: Interactive console UI running directly inside your terminal without needing a display server.
  4. **Cyberpunk Web App & REST API Server (`--web` / `-d`)**: Modern glassmorphism web interface backed by a JSON REST API.

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.8+
- Python packages (optional for Web mode): `flask`

### Installation
Clone the repository and make the script executable:

```bash
git clone https://github.com/Hauntdog/Repla5er.git
cd Repla5er
chmod +x replacer.py
```

Install Flask for Web App & REST API mode:
```bash
pip install flask
```

---

## 💡 Execution Modes & Usage Examples

### 1. 💻 CLI Pipe & Stream Mode

REPLA5ER integrates seamlessly into standard UNIX pipelines and shell scripts.

#### Replace Words
```bash
# Exact whole-word replacement
echo "Server status is OFFLINE and backup is OFFLINE." | ./replacer.py OFFLINE ONLINE
# Output: Server status is ONLINE and backup is ONLINE.

# Case-insensitive word replacement (-i)
echo "Server status is offline and backup is OFFLINE." | ./replacer.py offline ONLINE -i
# Output: Server status is ONLINE and backup is ONLINE.

# Allow partial word replacements (--partial)
echo "an apple and two apples" | ./replacer.py apple orange --partial
# Output: an orange and two oranges
```

#### Replace Numbers & Apply Math Formulas
```bash
# Target whole numbers only (-w is default)
echo "value is 42 and target is 4242" | ./replacer.py 42 99
# Output: value is 99 and target is 4242

# Math modifier on specific target number (add 10 to 42)
echo "latency is 42ms" | ./replacer.py 42 +10
# Output: latency is 52ms

# Global math mode (-m): multiply all numbers by 2
echo "port 8080 latency 42ms users 100" | ./replacer.py "" "*2" -m
# Output: port 16160 latency 84ms users 200
```

---

### 2. 🖥️ Dark Terminal GUI Mode (`--gui`)

Launch a sleek, responsive desktop GUI built with Tkinter.

```bash
./replacer.py --gui
```

- **Live Dual-Pane Editor**: Real-time transformation updates as you type.
- **Controls**: Toggles for Whole Words (`-w`), Ignore Case (`-i`), Math Mode (`-m`), and Range Filters.
- **Actions**: One-click **Copy Output**, **Load File**, **Save Output**, and **Clear Input**.

---

### 3. 📺 Curses Interactive Terminal TUI Mode (`--tui`)

Run a full keyboard-driven interactive interface directly inside your terminal session (ideal for SSH sessions).

```bash
./replacer.py --tui
```

- `[TAB]` / `[Enter]`: Switch active field (Find, Replace, Input Text)
- `[F2]`: Toggle Whole Words Mode
- `[F3]`: Toggle Ignore Case Mode
- `[ESC]` / `q`: Exit TUI

---

### 4. 🌐 Cyberpunk Web App & REST API Server Mode (`--web`)

Launch the web application on port 5000 (or custom `--port`):

```bash
# Foreground Web Server
./replacer.py --web --port 5000

# Background Daemon Mode (-d)
./replacer.py -d --port 5000
```

Access the Web UI in your browser at `http://localhost:5000`.

#### REST API Endpoint (`POST /api/replace`)

Send JSON payloads to `/api/replace`:

```bash
curl -X POST http://localhost:5000/api/replace \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Server 1 status OFFLINE, port 8080.",
    "find": "OFFLINE",
    "replace": "ONLINE",
    "whole_word": true,
    "ignore_case": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "count": 1,
  "transformed": "Server 1 status ONLINE, port 8080."
}
```

---

## ⚙️ Command-Line Reference

| Flag / Option | Description |
| :--- | :--- |
| `old` | Position 1: Word or number string to find |
| `new` | Position 2: Word, number, or math formula (`+10`, `*2`, etc.) |
| `-w`, `--word` | Match whole words/numbers only *(Default: True)* |
| `--partial` | Allow partial word or number matching |
| `-i`, `--ignore-case` | Enable case-insensitive text matching |
| `-m`, `--math` | Enable global math formula mode across all numeric values |
| `--gui` | Launch Graphical Dark Terminal GUI window |
| `--tui` | Launch interactive Curses Terminal UI |
| `--web` | Launch Web Application Server |
| `--port PORT` | Specify port for Web Application Server *(Default: 5000)* |
| `-d`, `--daemon` | Launch Web Application server in background as a daemon process |

---

## 🛠️ Systemd Background Service Setup

To run REPLA5ER as a persistent background service on Linux:

1. Copy `replacer.service` to systemd system directory:
   ```bash
   sudo cp replacer.service /etc/systemd/system/
   ```
2. Reload daemon and start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now replacer.service
   ```
3. Check status:
   ```bash
   sudo systemctl status replacer.service
   ```

---

## 📁 Repository Structure

```
Repla5er/
├── replacer.py          # Main executable engine (CLI, GUI, TUI, Web)
├── replacer.service     # Systemd service daemon unit file
├── templates/
│   └── index.html       # Web App frontend template (HTML5/CSS3/JS)
└── README.md            # Project documentation
```

---

## 📄 License

Distributed under the **MIT License**. Free for open-source and commercial use.

---

<p align="center">
  <b>⚡ Crafted for speed, precision, and flexibility.</b>
</p>
