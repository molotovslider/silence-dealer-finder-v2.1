#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Silence.eco — Dealer Finder v12 (stable + debug)
"""

import tkinter as tk
import json, re, time, os, csv, random, threading, urllib.request, urllib.parse, urllib.error
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ── API ─────────────────────────────────────────────
HUNTER_KEY = "6f720d52e7ff130ef0717a890cd35abcac84c6fd"

# ── Regex ────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")

# ── UA ───────────────────────────────────────────────
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# ── FETCH SAFE ───────────────────────────────────────
def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,*/*",
            "Accept-Language": "fr-FR,fr;q=0.9"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = r.headers.get_content_charset() or "utf-8"
            html = raw.decode(enc, errors="ignore")

            return html

    except Exception as e:
        return ""

# ── CLEAN TEXT ───────────────────────────────────────
def clean(html):
    return re.sub(r"\s+", " ", html)

# ── EMAIL / PHONE ────────────────────────────────────
def get_emails(txt):
    return set(m.group(0).lower() for m in EMAIL_RE.finditer(txt))

def get_phones(txt):
    return list(set(m.group(0) for m in PHONE_RE.finditer(txt)))

# ── SCRAPER SIMPLE MAIS FIABLE ───────────────────────
def scrape_page(url, log):
    log(f"GET {url}")
    html = fetch(url)

    if not html:
        log("❌ HTML vide (bloqué ou JS)")
        return []

    log(f"HTML reçu: {len(html)//1024} KB")

    txt = clean(html)

    # extraction ultra simple fallback
    names = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", html, re.I)

    dealers = []
    seen = set()

    for n in names:
        n = re.sub("<.*?>", "", n).strip()
        if len(n) < 3 or len(n) > 80:
            continue

        key = re.sub(r"[^a-z0-9]", "", n.lower())[:20]
        if key in seen:
            continue
        seen.add(key)

        ctx = txt[:2000]  # simplifié (pas context compliqué)

        dealers.append({
            "name": n,
            "addr": "",
            "phone": get_phones(ctx)[0] if get_phones(ctx) else "",
            "emails": list(get_emails(ctx)),
            "website": "",
            "src": "page"
        })

    log(f"Concessionnaires trouvés: {len(dealers)}")
    return dealers

# ── GUI MINIMAL DEBUG ────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dealer Finder FIX")
        self.geometry("900x600")

        self.url = tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")

        tk.Entry(self, textvariable=self.url).pack(fill="x")
        tk.Button(self, text="RUN", command=self.run).pack()

        self.log = scrolledtext.ScrolledText(self)
        self.log.pack(fill="both", expand=True)

    def logf(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        print(msg)

    def run(self):
        def task():
            dealers = scrape_page(self.url.get(), self.logf)

            self.logf("──── RESULT ────")
            for d in dealers:
                self.logf(str(d))

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
