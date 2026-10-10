# ⚡ REPLA5ER

> **The Ultimate Web Text & Number Transformation Engine for Vercel**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Vercel-black.svg)]()
[![Web API](https://img.shields.io/badge/REST%20API-Flask%20Online-38bdf8.svg)]()

**REPLA5ER** is a web-based text and number replacer designed for Vercel deployment. It provides a full-stack REST API web server built with Flask and Python serverless functions, alongside a beautiful cyberpunk UI.

---

## 🌟 Key Features

- 🔤 **Smart Word Replacement**: Replace text and words with whole-word boundary matching (`\bword\b`) or partial substring matching (`--partial`).
- 🔠 **Case-Insensitive Matching**: Match and replace words regardless of capitalization (e.g. `OFFLINE`, `offline`, `Offline`).
- 🔢 **Intelligent Number Engine**: Safely replaces whole numbers without corrupting decimals or larger digits (e.g. replaces `42` without touching `142` or `42.5`).
- 🧮 **Math Formula Modifier Mode**: Apply arithmetic calculations (`+10`, `-5`, `*2`, `/2`) directly to target numbers or across all numeric values in a text stream.
- 🎯 **Numeric Range Filtering**: Target only numbers within a specific minimum and maximum threshold (`min_val` to `max_val`).
- 🌐 **Web App & REST API Server**: Modern glassmorphism web interface backed by a JSON REST API, running on Vercel Python Serverless functions.

---

## 🚀 Quick Start & Deployment

### Run Locally
To run the server locally, install dependencies and execute `replacer.py`:

```bash
git clone https://github.com/Hauntdog/Repla5er.git
cd Repla5er
pip install -r requirements.txt
python replacer.py
```
Access the Web UI in your browser at `http://localhost:5000`.

### Deploy to Vercel
This repository is pre-configured for Vercel. 
Simply push to GitHub and import your repository in the Vercel dashboard. Vercel will automatically detect `vercel.json` and the `api/index.py` Serverless function to deploy the Flask app.

---

## 🌐 REST API Usage

### Endpoint: `POST /api/replace`

Send JSON payloads to `/api/replace`:

```bash
curl -X POST https://your-vercel-domain.vercel.app/api/replace \
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

## 📁 Repository Structure

```
Repla5er/
├── api/
│   └── index.py         # Vercel Serverless Function entry point
├── templates/
│   └── index.html       # Web App frontend template (HTML5/CSS3/JS)
├── replacer.py          # Main executable engine & Flask app logic
├── requirements.txt     # Python dependencies (Flask)
├── vercel.json          # Vercel deployment configuration
└── README.md            # Project documentation
```

---

## 📄 License

Distributed under the **MIT License**. Free for open-source and commercial use.

---

<p align="center">
  <b>⚡ Crafted for speed, precision, and flexibility.</b>
</p>
