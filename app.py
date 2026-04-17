#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Silence.eco — Dealer Finder v11 FIX (stable)"""

import tkinter as tk
import json, re, time, os, csv, random, threading, urllib.request, urllib.parse, urllib.error
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ─────────────────────────────────────────────
# API
# ─────────────────────────────────────────────
HUNTER_KEY = "6f720d52e7ff130ef0717a890cd35abcac84c6fd"

# ─────────────────────────────────────────────
# SAFE BS4 IMPORT
# ─────────────────────────────────────────────
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

# ─────────────────────────────────────────────
# REGEX
# ─────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# ─────────────────────────────────────────────
# FETCH SAFE
# ─────────────────────────────────────────────
def fetch(url, timeout=15, retries=2):
    last = ""
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,*/*",
                "Accept-Language": "fr-FR,fr;q=0.9"
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                enc = r.headers.get_content_charset() or "utf-8"
                return raw.decode(enc, errors="ignore")
        except Exception as e:
            last = str(e)
            time.sleep(1)
    return ""

# ─────────────────────────────────────────────
# CLEAN
# ─────────────────────────────────────────────
def clean(txt):
    return re.sub(r"\s+", " ", txt)

# ─────────────────────────────────────────────
# EMAIL / PHONE
# ─────────────────────────────────────────────
def get_emails(txt):
    return set(m.group(0).lower() for m in EMAIL_RE.finditer(txt))

def get_phones(txt):
    return list(set(m.group(0) for m in PHONE_RE.finditer(txt)))

# ─────────────────────────────────────────────
# SCRAPER CORE (FIXED)
# ─────────────────────────────────────────────
def scrape_page(url, log):

    log(f"GET {url}")

    html = fetch(url)

    if not html:
        log("❌ HTML vide → blocage ou JS")
        return []

    log(f"HTML reçu: {len(html)//1024} KB")

    if len(html) < 8000:
        log("⚠️ HTML suspect (JS ou contenu incomplet)")

    if BeautifulSoup is None:
        log("❌ BS4 absent → fallback regex")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # cleanup
    for t in soup(["script", "style", "nav", "footer", "header"]):
        t.decompose()

    text = clean(soup.get_text(" ", strip=True))

    dealers = []
    seen = set()

    htags = soup.find_all(["h2", "h3", "h4"])
    log(f"H tags détectés: {len(htags)}")

    for h in htags:

        name = h.get_text(strip=True)

        if not name or len(name) < 3 or len(name) > 80:
            continue

        key = re.sub(r"[^a-z0-9]", "", name.lower())[:20]
        if key in seen:
            continue
        seen.add(key)

        ctx = text[:1500]

        dealers.append({
            "name": name,
            "addr": "",
            "phone": get_phones(ctx)[0] if get_phones(ctx) else "",
            "emails": list(get_emails(ctx)),
            "website": "",
            "src": "page"
        })

    if not dealers:
        log("❌ Aucun dealer détecté → structure HTML incompatible")

    log(f"Concessionnaires trouvés: {len(dealers)}")
    return dealers

# ─────────────────────────────────────────────
# GUI (UNCHANGED)
# ─────────────────────────────────────────────
class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Dealer Finder FIX")
        self.geometry("900x600")

        self.url = tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")

        tk.Entry(self, textvariable=self.url).pack(fill="x", padx=10, pady=5)
        tk.Button(self, text="RUN", command=self.run).pack()

        self.logbox = scrolledtext.ScrolledText(self)
        self.logbox.pack(fill="both", expand=True)

    def logf(self, msg):
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")
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
