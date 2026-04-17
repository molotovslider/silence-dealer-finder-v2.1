#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silence.eco — Dealer Finder v11 — Production"""
import tkinter as tk
import json, re, time, os, csv, random, threading, urllib.request, urllib.parse, urllib.error
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ── Clés API intégrées ────────────────────────────────────────────────────────
HUNTER_KEY = "6f720d52e7ff130ef0717a890cd35abcac84c6fd"
CLAUDE_KEY  = ""  # optionnel

# ── Couleurs Silence ──────────────────────────────────────────────────────────
RED="#D01A20"; RED_D="#A01015"; RED_LT="#FAE8E8"; DARK="#1C1C1E"
GRAY="#F2F2F2"; WHITE="#FFFFFF"; MUTED="#8A8A8E"; BORDER="#E0E0E0"
GREEN="#15803d"; GREEN_LT="#F0FFF4"; AMBER="#b45309"; AMBER_LT="#FFFBF0"

# ── Traductions ───────────────────────────────────────────────────────────────
T = {
"FR": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extraction  ", tab2="  Résultats  ", tab3="  Paramètres  ",
    url_label="URL de la page réseau concessionnaires :",
    btn_go="  Extraire  ", btn_run="  En cours…  ", btn_again="  Relancer  ",
    opt1="Recherche emails (web + Hunter.io)", opt2="Dédupliquer", opt3="Exclure emails constructeur",
    info="Analyse la page → extrait tous les concessionnaires → trouve leur site web\n→ scrape les emails → interroge Hunter.io pour enrichir les contacts.",
    log_lbl="Journal :",
    col_num="#", col_name="Nom", col_addr="Adresse", col_phone="Téléphone",
    col_email="Email", col_src="Source", col_role="Rôle / Personne",
    src_page="Page", src_web="Site web", src_hunter="Hunter.io",
    stat1="Concessionnaires", stat2="Emails trouvés", stat3="Via Hunter/web", stat4="Adresses",
    btn_copy="Copier les emails", btn_csv="Exporter CSV",
    no_results="Aucun résultat — lancez une extraction",
    # Paramètres
    p_search="Recherche & Extraction",
    p_delay="Délai entre requêtes (secondes)",
    p_delay_desc="Augmentez si le site bloque les requêtes (recommandé : 1-3s)",
    p_timeout="Timeout connexion (secondes)",
    p_timeout_desc="Temps maximum d'attente par page (recommandé : 15-25s)",
    p_retries="Tentatives en cas d'échec",
    p_retries_desc="Nombre de réessais si une page ne répond pas (recommandé : 2-4)",
    p_filter="Filtres emails",
    p_excl="Domaines à exclure (constructeurs)",
    p_excl_desc="Un domaine par ligne — ces emails seront ignorés automatiquement",
    p_also_excl="Exclure aussi les emails génériques (info@, contact@…)",
    p_export="Export",
    p_include_no_email="Inclure les concessionnaires sans email dans le CSV",
    p_open_csv="Ouvrir le CSV après export",
    btn_save="  Enregistrer  ", btn_reset="Réinitialiser",
    info_saved="Paramètres enregistrés !",
    info_reset="Paramètres réinitialisés.",
    err_url="URL invalide (doit commencer par http)",
    export_ok="CSV sauvegardé sur le Bureau :",
    ready="Prêt", last="Dernier run : ",
    copied="emails copiés !", no_copy="Aucun email.",
),
"ES": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extracción  ", tab2="  Resultados  ", tab3="  Ajustes  ",
    url_label="URL de la página red de concesionarios:",
    btn_go="  Extraer  ", btn_run="  En proceso…  ", btn_again="  Reiniciar  ",
    opt1="Buscar emails (web + Hunter.io)", opt2="Eliminar duplicados", opt3="Excluir emails fabricante",
    info="Analiza la página → extrae concesionarios → encuentra su web\n→ extrae emails → consulta Hunter.io para enriquecer contactos.",
    log_lbl="Registro:",
    col_num="#", col_name="Nombre", col_addr="Dirección", col_phone="Teléfono",
    col_email="Email", col_src="Fuente", col_role="Rol / Persona",
    src_page="Página", src_web="Sitio web", src_hunter="Hunter.io",
    stat1="Concesionarios", stat2="Emails encontrados", stat3="Vía Hunter/web", stat4="Direcciones",
    btn_copy="Copiar emails", btn_csv="Exportar CSV",
    no_results="Sin resultados — lance una extracción",
    p_search="Búsqueda y Extracción",
    p_delay="Retraso entre solicitudes (segundos)",
    p_delay_desc="Auméntelo si el sitio bloquea las solicitudes (recomendado: 1-3s)",
    p_timeout="Tiempo de espera (segundos)",
    p_timeout_desc="Tiempo máximo de espera por página (recomendado: 15-25s)",
    p_retries="Intentos en caso de fallo",
    p_retries_desc="Número de reintentos si una página no responde (recomendado: 2-4)",
    p_filter="Filtros de email",
    p_excl="Dominios a excluir (fabricantes)",
    p_excl_desc="Un dominio por línea — estos emails se ignorarán automáticamente",
    p_also_excl="Excluir también emails genéricos (info@, contact@…)",
    p_export="Exportación",
    p_include_no_email="Incluir concesionarios sin email en el CSV",
    p_open_csv="Abrir el CSV tras exportar",
    btn_save="  Guardar  ", btn_reset="Restablecer",
    info_saved="¡Ajustes guardados!", info_reset="Ajustes restablecidos.",
    err_url="URL inválida (debe empezar por http)",
    export_ok="CSV guardado en el Escritorio:",
    ready="Listo", last="Última extracción: ",
    copied="emails copiados!", no_copy="Sin emails.",
),
"EN": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extraction  ", tab2="  Results  ", tab3="  Settings  ",
    url_label="Dealer network page URL:",
    btn_go="  Extract  ", btn_run="  Running…  ", btn_again="  Run Again  ",
    opt1="Find emails (web + Hunter.io)", opt2="Deduplicate", opt3="Exclude manufacturer emails",
    info="Scans the page → extracts all dealers → finds their website\n→ scrapes emails → queries Hunter.io to enrich contacts.",
    log_lbl="Log:",
    col_num="#", col_name="Name", col_addr="Address", col_phone="Phone",
    col_email="Email", col_src="Source", col_role="Role / Person",
    src_page="Page", src_web="Website", src_hunter="Hunter.io",
    stat1="Dealers", stat2="Emails found", stat3="Via Hunter/web", stat4="Addresses",
    btn_copy="Copy emails", btn_csv="Export CSV",
    no_results="No results — run an extraction first",
    p_search="Search & Extraction",
    p_delay="Delay between requests (seconds)",
    p_delay_desc="Increase if the site blocks requests (recommended: 1-3s)",
    p_timeout="Connection timeout (seconds)",
    p_timeout_desc="Maximum wait time per page (recommended: 15-25s)",
    p_retries="Retries on failure",
    p_retries_desc="Number of retries if a page does not respond (recommended: 2-4)",
    p_filter="Email filters",
    p_excl="Domains to exclude (manufacturers)",
    p_excl_desc="One domain per line — these emails will be ignored automatically",
    p_also_excl="Also exclude generic emails (info@, contact@…)",
    p_export="Export",
    p_include_no_email="Include dealers without email in the CSV",
    p_open_csv="Open CSV after export",
    btn_save="  Save  ", btn_reset="Reset",
    info_saved="Settings saved!", info_reset="Settings reset.",
    err_url="Invalid URL (must start with http)",
    export_ok="CSV saved to Desktop:",
    ready="Ready", last="Last run: ",
    copied="emails copied!", no_copy="No emails.",
),
}

# ── Constantes ────────────────────────────────────────────────────────────────
EXCL_DEFAULT = [
    "silence.eco","aixam.com","microcar.fr","ligier.fr","chatenet.com",
    "casalini.it","bellier.fr","grecav.com","renault.fr","peugeot.fr",
    "citroen.fr","toyota.fr","volkswagen.fr","ford.fr","opel.fr",
]
PLATFORM_SKIP = [
    "duckduckgo.com","google.","facebook.","instagram.","twitter.","linkedin.",
    "youtube.","yelp.","tripadvisor.","pagesjaunes.","societe.com","verif.com",
    "pappers.fr","wix.","squarespace.","shopify.","wordpress.","example.com",
    "test.com","noreply.","sentry.","w3.org","schema.org","cloudflare.",
    "microsoft.","apple.","amazon.","leboncoin.","lacentrale.","largus.",
]
GENERIC_PREFIXES = ["info","contact","noreply","no-reply","admin","webmaster",
                    "postmaster","support","hello","bonjour","mailer"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
ADDR_RE  = re.compile(
    r"\d{1,4}[\s,]+[^\d\n]{5,60}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,35}", re.I)

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

ROLE_MAP = [
    (["direction","directeur","directrice","pdg","ceo","dg","gerant","patron","president"], "Direction"),
    (["commercial","vente","ventes","sales","vendeur","vendeuse","dealer"],                 "Commercial"),
    (["marketing","communication","comm","media","promo","digital","pub"],                  "Marketing"),
    (["comptabilite","comptable","compta","facturation","finance","gestion"],               "Comptabilité"),
    (["contact","info","information","hello","bonjour","accueil","reception","bienvenue"],  "Contact général"),
    (["apv","atelier","technique","sav","service","reparation","garage","meca"],            "Après-vente"),
    (["rh","hr","recrutement","emploi","jobs","carriere"],                                  "RH"),
    (["secretariat","admin","administration","assistante","assistant","bureau"],            "Administration"),
    (["pieces","parts","magasin","boutique","accessoires"],                                  "Pièces / Boutique"),
]

def guess_role(email):
    local = re.sub(r"[.\-_0-9]", "", email.split("@")[0].lower())
    for kws, lbl in ROLE_MAP:
        if any(k in local for k in kws): return lbl
    return "Équipe"

# ── Fetch robuste ─────────────────────────────────────────────────────────────
def fetch(url, timeout=18, retries=3, ref="https://www.google.com"):
    """
    Fetch with 4 strategies — guaranteed to work on all sites.
    """
    html = None

    # ── Strategy 1: Selenium (vrai Chrome installé sur le PC) ────────────
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import subprocess, shutil

        # Find chrome/chromedriver
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome", "/usr/bin/chromium-browser",
        ]
        chrome_ok = any(os.path.exists(p) for p in chrome_paths)

        # Auto-download chromedriver if needed
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            opts = Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument(f"--user-agent={random.choice(UA_POOL)}")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opts)
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            time.sleep(2)
            html = driver.page_source
            driver.quit()
            if html and len(html) > 5000:
                return html
        except Exception:
            pass

        if chrome_ok:
            opts = Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument(f"--user-agent={random.choice(UA_POOL)}")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            driver = webdriver.Chrome(options=opts)
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            time.sleep(2)  # let JS execute
            html = driver.page_source
            driver.quit()
            if html and len(html) > 5000:
                return html
    except Exception:
        pass

    # ── Strategy 2: requests with session + cookies ───────────────────────
    try:
        import requests
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(UA_POOL),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": ref,
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
        })
        # First visit homepage to get cookies
        base = re.match(r"https?://[^/]+", url)
        if base:
            try: session.get(base.group(0), timeout=8)
            except: pass
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.encoding = resp.apparent_encoding or "utf-8"
        if len(resp.text) > 5000:
            return resp.text
        html = resp.text
    except Exception:
        pass

    # ── Strategy 3: urllib with full cookie jar ───────────────────────────
    for attempt in range(retries):
        try:
            import http.cookiejar
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [
                ("User-Agent", random.choice(UA_POOL)),
                ("Accept", "text/html,application/xhtml+xml,*/*;q=0.9"),
                ("Accept-Language", "fr-FR,fr;q=0.9,en;q=0.7"),
                ("Accept-Encoding", "gzip, deflate"),
                ("Connection", "keep-alive"),
                ("Referer", ref),
                ("Upgrade-Insecure-Requests", "1"),
            ]
            with opener.open(url, timeout=timeout) as r:
                raw = r.read()
                enc = r.headers.get_content_charset("utf-8") or "utf-8"
                text = raw.decode(enc, errors="replace")
                if len(text) > 3000:
                    return text
                html = text
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):
                time.sleep(2 ** attempt + random.uniform(1, 3))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))

    # ── Strategy 4: return whatever we got, even if small ─────────────────
    if html:
        return html
    raise Exception(f"Impossible de charger la page: {url}")


def is_real(e, filter_generic=False):
    if not e or len(e) < 7 or "@" not in e: return False
    local, dom = e.split("@")[0].lower(), e.split("@")[-1].lower()
    if any(p in dom for p in PLATFORM_SKIP): return False
    if re.search(r"\.(png|jpg|gif|css|js|svg|ico|woff|ttf|pdf)$", dom): return False
    if "." not in dom or len(dom.split(".")[0]) < 2: return False
    if filter_generic and local in GENERIC_PREFIXES: return False
    return True

def get_emails(text, excl, filter_generic=False):
    out = set()
    for m in EMAIL_RE.finditer(text):
        e = m.group(0).lower().strip(".,;:<>\"'()")
        dom = e.split("@")[-1]
        if not any(x in dom for x in excl) and is_real(e, filter_generic):
            out.add(e)
    return out

def get_phones(text):
    seen, out = set(), []
    for m in PHONE_RE.finditer(text):
        p = re.sub(r"[\s.\-]", "", m.group(0))
        if p not in seen: seen.add(p); out.append(p)
    return out

# ── Hunter.io ─────────────────────────────────────────────────────────────────
def hunter_search(domain, excl, log, timeout=15):
    if not HUNTER_KEY or not domain: return {}
    try:
        url = (f"https://api.hunter.io/v2/domain-search"
               f"?domain={urllib.parse.quote(domain)}&api_key={HUNTER_KEY}&limit=100")
        data = json.loads(fetch(url, timeout=timeout))
        results = {}
        for item in data.get("data", {}).get("emails", []):
            e = item.get("value", "").lower()
            if not e or not is_real(e) or any(x in e.split("@")[-1] for x in excl): continue
            fn = (item.get("first_name") or "").strip()
            ln = (item.get("last_name") or "").strip()
            pos = (item.get("position") or "").strip()
            dept = (item.get("department") or "").strip()
            person = f"{fn} {ln}".strip()
            parts = [p for p in [person, pos, dept] if p]
            results[e] = " — ".join(parts) if parts else guess_role(e)
        log(f"  ✅ Hunter.io ({domain}): {len(results)} email(s)")
        return results
    except Exception as err:
        log(f"  Hunter: {str(err)[:60]}")
        return {}

# ── Trouver le vrai site du concessionnaire ───────────────────────────────────
def find_dealer_domain(name, addr, log, delay=0.5):
    city = ""
    if addr:
        m = re.search(r"\d{5}\s+(\S+)", addr)
        if m: city = m.group(1)
    queries = [
        f'"{name}" site officiel concessionnaire',
        f'{name} {city} site web' if city else f'{name} concessionnaire site',
    ]
    for q in queries:
        try:
            log(f"  🌐 Recherche site: {q[:55]}")
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
            html = fetch(url, timeout=15, ref="https://duckduckgo.com")
            for href in re.findall(r'href="(https?://[^"&]{8,})"', html):
                dom = re.sub(r"https?://(?:www\.)?", "", href).split("/")[0].lower().strip()
                if not dom or "." not in dom or len(dom) < 5: continue
                if any(c in dom for c in EXCL_DEFAULT): continue
                if any(p in dom for p in PLATFORM_SKIP): continue
                log(f"  Site: {dom}")
                return dom
            time.sleep(delay * 0.5)
        except Exception as e:
            pass  # silent fail, move to next
    return ""

def scrape_domain_emails(domain, excl, log, timeout=12):
    found = set()
    pages = [
        f"https://{domain}", f"https://www.{domain}",
        f"https://{domain}/contact", f"https://www.{domain}/contact",
        f"https://{domain}/nous-contacter", f"https://{domain}/contacto",
        f"https://{domain}/contact-us",
    ]
    base = domain.replace("www.", "")
    for page in pages:
        try:
            html = fetch(page, timeout=timeout, ref=f"https://{domain}")
            same = {e for e in get_emails(html, excl) if base in e}
            if same:
                found.update(same)
                log(f"  Scrape {page}: {len(same)} email(s)")
            if len(found) >= 10: break
            time.sleep(random.uniform(0.4, 1.0))
        except Exception:
            continue
    return found

# ── Enrichissement complet ────────────────────────────────────────────────────
def google_search_emails(name, addr, excl, log):
    """
    Search emails — stops immediately when first email found.
    Scans full page HTML (Google shows emails directly in results).
    Sources in order: Google → Google Maps → DuckDuckGo → Bing → Pages Jaunes → Societe.com
    """
    city = ""
    if addr:
        m = re.search(r"\d{5}\s+(\S+)", addr)
        if m: city = m.group(1)
    n = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", name).strip()

    def scan_full_page(html, source):
        """Scan the entire page — Google puts emails anywhere in the HTML."""
        # Full raw text scan
        full_text = re.sub(r"<[^>]+>", " ", html)
        full_text = re.sub(r"\s+", " ", full_text)
        emails = get_emails(full_text, excl)
        # Also scan raw HTML for mailto: links
        for m2 in re.finditer(r"mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})", html):
            e = m2.group(1).lower()
            if is_real(e) and not any(x in e.split("@")[-1] for x in excl):
                emails.add(e)
        if emails:
            for e in sorted(emails)[:5]:
                log(f"  ✅ [{source}] {e}")
        return emails

    # ── 1. Google Search ──────────────────────────────────────────────────
    for q in [f'"{n}" email', f'"{n}" {city} email' if city else None,
              f'{n} concessionnaire email contact']:
        if not q: continue
        try:
            log(f"  🔍 Google: {q[:55]}")
            url = "https://www.google.com/search?q=" + urllib.parse.quote(q) + "&hl=fr&num=10"
            html = fetch(url, timeout=12, ref="https://www.google.com")
            emails = scan_full_page(html, "Google")
            if emails:
                log(f"  ✔ Trouvé via Google — recherche arrêtée")
                return emails
            time.sleep(random.uniform(1.0, 1.8))
        except Exception as e:
            log(f"  ↳ Google bloqué ({str(e)[:30]}) — source suivante")
            break

    # ── 2. Google Maps ────────────────────────────────────────────────────
    try:
        log(f"  🗺️  Google Maps: {n[:40]}")
        url = "https://www.google.com/maps/search/" + urllib.parse.quote(f"{n} {city}".strip()) + "?hl=fr"
        html = fetch(url, timeout=12, ref="https://www.google.com/maps")
        emails = scan_full_page(html, "Google Maps")
        if emails:
            log(f"  ✔ Trouvé via Google Maps — recherche arrêtée")
            return emails
        # Extract website from Maps result and scrape it
        url_pattern = re.compile(r'https?://[^\s<>"]{8,60}')
        for m2 in url_pattern.finditer(html):
            href = m2.group(0)
            dom = re.sub(r"https?://(?:www\.)?", "", href).split("/")[0].lower()
            if dom and "." in dom and not any(p in dom for p in PLATFORM_SKIP) and dom not in excl:
                log(f"  🗺️  Site Maps→scraping: {dom}")
                scraped = scrape_domain_emails(dom, excl, log)
                if scraped:
                    for e in sorted(scraped)[:3]: log(f"  ✅ [Maps→Site] {e}")
                    log(f"  ✔ Trouvé via Maps+Site — recherche arrêtée")
                    return scraped
                break
    except Exception as e:
        log(f"  ↳ Google Maps: {str(e)[:35]}")

    # ── 3. DuckDuckGo ─────────────────────────────────────────────────────
    for q in [f'"{n}" email', f'{n} {city} contact' if city else None]:
        if not q: continue
        try:
            log(f"  🔍 DuckDuckGo: {q[:50]}")
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
            html = fetch(url, timeout=12, ref="https://duckduckgo.com")
            emails = scan_full_page(html, "DuckDuckGo")
            if emails:
                log(f"  ✔ Trouvé via DuckDuckGo — recherche arrêtée")
                return emails
            time.sleep(random.uniform(0.6, 1.2))
        except Exception:
            break

    # ── 4. Bing ───────────────────────────────────────────────────────────
    try:
        log(f"  🔍 Bing: {n[:40]}")
        q = urllib.parse.quote(f'"{n}" email contact')
        html = fetch(f"https://www.bing.com/search?q={q}&setlang=fr",
                     timeout=12, ref="https://www.bing.com")
        emails = scan_full_page(html, "Bing")
        if emails:
            log(f"  ✔ Trouvé via Bing — recherche arrêtée")
            return emails
    except Exception:
        pass

    # ── 5. Pages Jaunes ───────────────────────────────────────────────────
    try:
        log(f"  🔍 Pages Jaunes: {n[:35]}")
        q = urllib.parse.quote(f"{n} {city}".strip())
        html = fetch(f"https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui={q}",
                     timeout=12, ref="https://www.pagesjaunes.fr")
        emails = scan_full_page(html, "Pages Jaunes")
        if emails:
            log(f"  ✔ Trouvé via Pages Jaunes — recherche arrêtée")
            return emails
    except Exception:
        pass

    # ── 6. Societe.com ────────────────────────────────────────────────────
    try:
        log(f"  🔍 Societe.com: {n[:35]}")
        q = urllib.parse.quote(n)
        html = fetch(f"https://www.societe.com/cgi-bin/search?champs={q}",
                     timeout=12, ref="https://www.societe.com")
        emails = scan_full_page(html, "Societe.com")
        if emails:
            log(f"  ✔ Trouvé via Societe.com — recherche arrêtée")
            return emails
    except Exception:
        pass

    log(f"  ✗ Aucun email trouvé (6 sources épuisées)")
    return set()


def enrich_dealer(dealer, excl, log, delay=0.8, timeout=15):
    """
    Enrichment pipeline:
    1. Direct Google search "name email" → fastest
    2. Find dealer website → scrape emails
    3. Hunter.io on domain → professional contacts with names
    """
    all_em = dict(dealer.get("emails", {}))
    src    = dealer.get("src", "pending")
    name   = dealer["name"]

    log(f"┌─ {name[:50]}")

    # ── Étape 1 : Recherche directe Google ───────────────────────────────
    log(f"│  Étape 1/3 — Recherche Google directe")
    direct = google_search_emails(name, dealer["addr"], excl, log)
    if direct:
        for e in direct:
            if e not in all_em: all_em[e] = guess_role(e)
        src = "web"
        log(f"│  → {len(direct)} email(s) trouvé(s) via Google")
    else:
        log(f"│  → Aucun email trouvé via Google")

    # ── Étape 2 : Site web du concessionnaire ────────────────────────────
    log(f"│  Étape 2/3 — Recherche du site web")
    domain = find_dealer_domain(name, dealer["addr"], log, delay)
    if domain:
        dealer["website"] = domain
        log(f"│  → Site trouvé: {domain}")
        log(f"│  Scraping du site web…")
        scraped = scrape_domain_emails(domain, excl, log, timeout)
        if scraped:
            for e in scraped:
                if e not in all_em: all_em[e] = guess_role(e)
            if src == "pending": src = "web"
            log(f"│  → {len(scraped)} email(s) depuis le site")
        else:
            log(f"│  → Aucun email sur le site")

        # ── Étape 3 : Hunter.io ──────────────────────────────────────────
        log(f"│  Étape 3/3 — Hunter.io ({domain})")
        h = hunter_search(domain, excl, log, timeout)
        if h:
            all_em.update(h)
            src = "hunter"
            log(f"│  → {len(h)} contact(s) Hunter.io")
        else:
            log(f"│  → Aucun résultat Hunter.io")
    else:
        log(f"│  → Site web non trouvé")
        log(f"│  Étape 3/3 — Hunter.io ignoré (pas de domaine)")

    total = len([e for e in all_em if is_real(e)])
    log(f"└─ Total: {total} email(s) — Source: {src}")

    return {e: r for e, r in all_em.items() if is_real(e)}, src


def scrape_page(url, excl, log, prog, timeout=18, retries=3):
    prog(5, "Chargement de la page…")
    log(f"GET {url}")
    html = fetch(url, timeout=timeout, retries=retries)
    log(f"Page reçue — {len(html)//1024} Ko")
    prog(18, "Analyse HTML…")
    dealers = []
    PHONE_RE2 = re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
    ADDR_RE2  = re.compile(r"\d{1,4}[\s,]+[^\d\n]{5,60}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,35}", re.I)

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script","style","nav","footer","head","header","aside"]): t.decompose()
        clean_text = soup.get_text(" ", strip=True)

        base_url = (re.match(r"https?://[^/]+", url) or type("x",[],{"group":lambda s,i:""})()).group(0)
        parsed   = urllib.parse.urlparse(url)
        path_dir = re.sub(r"/[^/]*$", "/", parsed.path)

        seen = set()

        # ── Méthode 1 : h3 comme noms (Aixam, la plupart des sites réseaux) ──
        for h3 in soup.find_all(["h3","h4"]):
            a_tag = h3.find("a")
            name  = (a_tag or h3).get_text(strip=True)
            if not name or len(name) < 3 or len(name) > 100: continue
            skip_words = ("tél","tel","fax","email","adresse","voir","cliquer",
                          "notre","les ","le ","la ","pour ","avec ","sans ",
                          "tous","département","région","accueil","bienvenue")
            if any(name.lower().startswith(w) for w in skip_words): continue
            if re.match(r"^\d", name): continue

            key = re.sub(r"[^a-z0-9]", "", name.lower())[:22]
            if not key or key in seen: continue
            seen.add(key)

            # Contenu après le h3 jusqu'au prochain h3/h4
            block_parts = []
            node = h3.next_sibling
            for _ in range(50):
                if node is None: break
                if hasattr(node,"name") and node.name in ["h3","h4","h2","h1"]: break
                block_parts.append(str(node))
                node = node.next_sibling
            block_html = "".join(block_parts)
            b = BeautifulSoup(block_html, "html.parser")
            btxt = b.get_text(" ", strip=True)

            # Aussi regarder le parent direct du h3
            parent_txt = h3.parent.get_text(" ", strip=True) if h3.parent else ""

            # Adresse
            addr = ""
            for src_txt in [btxt, parent_txt]:
                am = ADDR_RE2.search(src_txt)
                if am: addr = am.group(0).strip()[:120]; break
            if not addr:
                # Chercher un code postal 5 chiffres dans le bloc
                for tag in b.find_all(["p","address","div","span"]):
                    t2 = tag.get_text(" ", strip=True)
                    if re.search(r"\d{5}", t2) and 5 < len(t2) < 200:
                        addr = t2[:120]; break

            # Téléphone
            phones = get_phones(btxt + " " + parent_txt)
            phone  = phones[0] if phones else ""

            # Emails visibles dans le bloc
            pg = get_emails(btxt + " " + parent_txt, excl)
            for a in b.find_all("a", href=True):
                h2 = a["href"]
                if h2.startswith("mailto:"):
                    e = h2[7:].split("?")[0].strip().lower()
                    if is_real(e) and not any(x in e.split("@")[-1] for x in excl):
                        pg.add(e)

            # Lien fiche du concessionnaire
            profile = ""
            if a_tag and a_tag.get("href"):
                href = a_tag["href"]
                if href.startswith("/"): href = base_url + href
                profile = href
            if not profile and h3.parent:
                for a in h3.parent.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/"): href = base_url + href
                    if base_url in href and path_dir in href and href.rstrip("/") != url.rstrip("/"):
                        profile = href; break

            dealers.append({
                "name": name[:80], "addr": addr, "phone": phone,
                "website": "", "profile_url": profile,
                "emails": {e: guess_role(e) for e in pg},
                "src": "page" if pg else "pending",
            })

        log(f"Méthode h3/h4: {len(dealers)} concessionnaires")

        # ── Méthode 2 : sélecteurs CSS (autres sites) ──────────────────────
        if len(dealers) < 5:
            log("Tentative sélecteurs CSS…")
            best_blocks, best_n = [], 0
            for sel in [
                "[class*='dealer']","[class*='concess']","[class*='revendeur']",
                "[class*='reseau']","[class*='network']","[class*='store']",
                "[class*='location']","[class*='retailer']","[class*='point-de-vente']",
                "[class*='distributor']","[class*='agent']",
                "article","[class*='card']","[class*='item']",
            ]:
                found = soup.select(sel)
                valid = [b for b in found
                         if PHONE_RE2.search(b.get_text())
                         or EMAIL_RE.search(b.get_text())
                         or (len(b.get_text(strip=True)) > 40 and len(b.get_text(strip=True)) < 800)]
                if len(valid) > best_n:
                    best_n = len(valid); best_blocks = valid
            log(f"Meilleur CSS: {best_n} blocs")

            for blk in best_blocks:
                txt = blk.get_text(" ", strip=True)
                if len(txt) < 15: continue
                name = ""
                for tag in blk.find_all(["h2","h3","h4","h5","strong","b"]):
                    v = tag.get_text(strip=True)
                    if 3 < len(v) < 90 and not PHONE_RE2.match(v) and not v.replace(" ","").isdigit():
                        name = v; break
                if not name: continue
                key = re.sub(r"[^a-z0-9]", "", name.lower())[:22]
                if not key or key in seen: continue
                seen.add(key)
                am = ADDR_RE2.search(txt); addr = am.group(0).strip()[:120] if am else ""
                phones = get_phones(txt); phone = phones[0] if phones else ""
                pg = get_emails(txt, excl)
                for a in blk.find_all("a", href=True):
                    h2 = a["href"]
                    if h2.startswith("mailto:"):
                        e = h2[7:].split("?")[0].strip().lower()
                        if is_real(e) and not any(x in e.split("@")[-1] for x in excl): pg.add(e)
                dealers.append({
                    "name": name[:80], "addr": addr, "phone": phone,
                    "website": "", "profile_url": "",
                    "emails": {e: guess_role(e) for e in pg},
                    "src": "page" if pg else "pending",
                })

        # ── Méthode 3 : fallback blocs avec téléphone ──────────────────────
        if len(dealers) < 5:
            log("Fallback blocs téléphone…")
            for blk in soup.find_all(["div","li","article","p","section"]):
                if not PHONE_RE2.search(blk.get_text()): continue
                txt = blk.get_text(" ", strip=True)
                if len(txt) < 20 or len(txt) > 1000: continue
                name = ""
                for tag in blk.find_all(["strong","b","span","h5","h4","h3"]):
                    v = tag.get_text(strip=True)
                    if 3 < len(v) < 90 and not PHONE_RE2.match(v): name = v; break
                if not name: continue
                key = re.sub(r"[^a-z0-9]", "", name.lower())[:22]
                if not key or key in seen: continue
                seen.add(key)
                phones = get_phones(txt); phone = phones[0] if phones else ""
                am = ADDR_RE2.search(txt); addr = am.group(0)[:120] if am else ""
                pg = get_emails(txt, excl)
                dealers.append({
                    "name": name[:80], "addr": addr, "phone": phone,
                    "website": "", "profile_url": "",
                    "emails": {e: guess_role(e) for e in pg},
                    "src": "page" if pg else "pending",
                })

    except ImportError:
        # ── Sans BeautifulSoup : regex sur le HTML brut ────────────────────
        log("Mode regex (bs4 non installé)…")
        # Extraire noms depuis les h3 avec liens
        names = re.findall(r"<h3[^>]*>\s*(?:<a[^>]*>)?([^<]{3,80})(?:</a>)?\s*</h3>", html, re.I)
        clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        seen = set()
        for name in names:
            name = name.strip()
            if not name or len(name) < 3: continue
            key = re.sub(r"[^a-z0-9]", "", name.lower())[:22]
            if key in seen: continue
            seen.add(key)
            idx = clean.find(name[:20])
            ctx = clean[max(0,idx-30):idx+350] if idx >= 0 else ""
            phones = get_phones(ctx); phone = phones[0] if phones else ""
            am = ADDR_RE2.search(ctx); addr = am.group(0)[:120] if am else ""
            em_l = list(get_emails(ctx, excl))
            dealers.append({
                "name": name[:80], "addr": addr, "phone": phone,
                "website": "", "profile_url": "",
                "emails": {e: guess_role(e) for e in em_l},
                "src": "page" if em_l else "pending",
            })
        # Fallback téléphones si pas de h3
        if not dealers:
            seen2 = set()
            for m in PHONE_RE.finditer(clean):
                ph = re.sub(r"[\s.\-]","",m.group(0))
                idx = m.start()
                ctx = clean[max(0,idx-200):idx+200]
                nm  = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿa-zà-ÿ\-]+){1,4})", ctx)
                name = nm.group(1) if nm else f"Concessionnaire {len(dealers)+1}"
                key = re.sub(r"[^a-z0-9]","",name.lower())[:20]
                if key in seen2: continue
                seen2.add(key)
                em_l = list(get_emails(ctx, excl))
                dealers.append({
                    "name": name[:80], "addr": "", "phone": ph,
                    "website": "", "profile_url": "",
                    "emails": {e: guess_role(e) for e in em_l},
                    "src": "page" if em_l else "pending",
                })

    # ── Déduplication finale ───────────────────────────────────────────────
    final, seen3 = [], set()
    for d in dealers:
        k = re.sub(r"[^a-z0-9]", "", d["name"].lower())[:20]
        if k and k not in seen3:
            seen3.add(k); final.append(d)

    log(f"✓ {len(final)} concessionnaires uniques extraits")
    return final


# ══════════════════════════════════════════════════════════════════════════════
#  GUI
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang     = "FR"
        self.results  = []
        self._running = False
        # Paramètres (avec valeurs par défaut)
        self.excl          = list(EXCL_DEFAULT)
        self.delay         = tk.DoubleVar(value=1.2)
        self.timeout_v     = tk.IntVar(value=18)
        self.retries_v     = tk.IntVar(value=3)
        self.filter_generic= tk.BooleanVar(value=False)
        self.include_no_em = tk.BooleanVar(value=True)
        self.open_csv      = tk.BooleanVar(value=False)

        self.configure(bg=DARK)
        self.geometry("1060x710")
        self.minsize(860, 600)
        self._build()
        self._apply_lang()

    def L(self, k): return T[self.lang].get(k, k)

    # ── HEADER ────────────────────────────────────────────────────────────────
    def _build(self):
        hdr = tk.Frame(self, bg=DARK, pady=10); hdr.pack(fill="x")
        left = tk.Frame(hdr, bg=DARK); left.pack(side="left", padx=20)
        c = tk.Canvas(left, width=34, height=34, bg=DARK, highlightthickness=0)
        c.pack(side="left")
        c.create_rectangle(0,0,34,34, fill=RED, outline="")
        c.create_polygon([17,4,28,10,28,24,17,30,6,24,6,10], outline=WHITE, fill="", width=2)
        c.create_oval(12,12,22,22, fill=WHITE, outline="")
        tk.Label(left, text="  SILENCE", bg=DARK, fg=WHITE,
                 font=("Helvetica",16,"bold")).pack(side="left")
        tk.Label(left, text=" ECO · DEALER FINDER", bg=DARK, fg=RED,
                 font=("Helvetica",9)).pack(side="left")
        right = tk.Frame(hdr, bg=DARK); right.pack(side="right", padx=20)
        self._lbl_status = tk.Label(right, text="", bg=DARK, fg=MUTED,
                                     font=("Helvetica",10))
        self._lbl_status.pack(side="left", padx=(0,16))
        for code in ("FR","ES","EN"):
            tk.Button(right, text=code, bg="#2C2C2E", fg=WHITE,
                      font=("Helvetica",9,"bold"), relief="flat", width=3,
                      cursor="hand2", bd=0, pady=4,
                      command=lambda c=code: self._switch(c)).pack(side="left", padx=2)
        self._mk_nb()

    # ── NOTEBOOK ──────────────────────────────────────────────────────────────
    def _mk_nb(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook", background=DARK, borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab", background="#2C2C2E", foreground=MUTED,
                    padding=[16,9], font=("Helvetica",11))
        s.map("TNotebook.Tab", background=[("selected",WHITE)], foreground=[("selected",RED)])
        s.configure("TFrame", background=WHITE)
        s.configure("Red.Horizontal.TProgressbar", troughcolor=BORDER, background=RED, thickness=5)
        s.configure("Treeview", rowheight=26, font=("Helvetica",10),
                    background=WHITE, fieldbackground=WHITE, foreground=DARK)
        s.configure("Treeview.Heading", font=("Helvetica",9,"bold"),
                    background=GRAY, foreground=MUTED)
        s.map("Treeview", background=[("selected",RED_LT)], foreground=[("selected",DARK)])
        self._nb = ttk.Notebook(self); self._nb.pack(fill="both", expand=True)
        self._f1=ttk.Frame(self._nb); self._f2=ttk.Frame(self._nb); self._f3=ttk.Frame(self._nb)
        self._nb.add(self._f1, text=""); self._nb.add(self._f2, text=""); self._nb.add(self._f3, text="")
        self._build_t1(); self._build_t2(); self._build_t3()

    # ── TAB 1 : EXTRACTION ────────────────────────────────────────────────────
    def _build_t1(self):
        f=self._f1; P=dict(padx=22,pady=5)
        self._lbl_url=tk.Label(f,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9,"bold"))
        self._lbl_url.pack(anchor="w",padx=22,pady=(14,3))
        row=tk.Frame(f,bg=WHITE); row.pack(fill="x",**P)
        self._url_var=tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        tk.Entry(row,textvariable=self._url_var,font=("Helvetica",11),bg=GRAY,relief="flat",bd=0,
                 highlightthickness=1,highlightbackground=BORDER,
                 highlightcolor=RED).pack(side="left",fill="x",expand=True,ipady=8,padx=(0,8))
        self._btn=tk.Button(row,text="",bg=RED,fg=WHITE,font=("Helvetica",11,"bold"),
                             relief="flat",cursor="hand2",bd=0,padx=16,pady=8,command=self._start)
        self._btn.pack(side="left")

        opt=tk.Frame(f,bg=WHITE); opt.pack(fill="x",**P)
        self._v1=tk.BooleanVar(value=True); self._v2=tk.BooleanVar(value=True); self._v3=tk.BooleanVar(value=True)
        self._chk1=tk.Checkbutton(opt,text="",variable=self._v1,bg=WHITE,fg=DARK,
                                   font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk2=tk.Checkbutton(opt,text="",variable=self._v2,bg=WHITE,fg=DARK,
                                   font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk3=tk.Checkbutton(opt,text="",variable=self._v3,bg=WHITE,fg=DARK,
                                   font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk1.pack(side="left",padx=(0,14)); self._chk2.pack(side="left",padx=(0,14)); self._chk3.pack(side="left")

        # Indicateurs Hunter
        ai_row=tk.Frame(f,bg=WHITE); ai_row.pack(fill="x",padx=22,pady=(0,3))
        self._hunter_ind=tk.Label(ai_row,text="⬤ Hunter.io : actif",bg=WHITE,fg=GREEN,font=("Helvetica",9))
        self._hunter_ind.pack(side="left")

        banner=tk.Frame(f,bg=RED_LT); banner.pack(fill="x",padx=22,pady=(0,6))
        tk.Frame(banner,bg=RED,width=3).pack(side="left",fill="y")
        self._banner_lbl=tk.Label(banner,text="",bg=RED_LT,fg="#7a0a0a",font=("Helvetica",9),justify="left")
        self._banner_lbl.pack(padx=10,pady=8,anchor="w")

        pf=tk.Frame(f,bg=WHITE); pf.pack(fill="x",**P)
        self._prog_lbl=tk.Label(pf,text="",bg=WHITE,fg=DARK,font=("Helvetica",10,"bold"))
        self._prog_lbl.pack(anchor="w")
        self._prog_var=tk.DoubleVar()
        ttk.Progressbar(pf,variable=self._prog_var,maximum=100,
                        style="Red.Horizontal.TProgressbar").pack(fill="x",pady=(4,0))

        lf=tk.Frame(f,bg=WHITE); lf.pack(fill="both",expand=True,**P)
        self._log_lbl=tk.Label(lf,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9,"bold"))
        self._log_lbl.pack(anchor="w")
        self._log=scrolledtext.ScrolledText(lf,height=7,font=("Courier",9),bg=GRAY,fg=DARK,
                                             relief="flat",bd=0,state="disabled",wrap="word",highlightthickness=0)
        self._log.pack(fill="both",expand=True,pady=(3,0))

        sf=tk.Frame(f,bg=WHITE); sf.pack(fill="x",padx=22,pady=(4,14))
        self._sv={}; self._slbl={}
        for k in ("s1","s2","s3","s4"):
            c=tk.Frame(sf,bg=GRAY,padx=14,pady=8); c.pack(side="left",fill="x",expand=True,padx=(0,8))
            lbl=tk.Label(c,text="",bg=GRAY,fg=MUTED,font=("Helvetica",9)); lbl.pack(anchor="w")
            v=tk.StringVar(value="—"); col=RED if k=="s2" else DARK
            tk.Label(c,textvariable=v,bg=GRAY,fg=col,font=("Helvetica",22,"bold")).pack(anchor="w")
            self._sv[k]=v; self._slbl[k]=lbl

    # ── TAB 2 : RÉSULTATS ────────────────────────────────────────────────────
    def _build_t2(self):
        f=self._f2
        top=tk.Frame(f,bg=WHITE); top.pack(fill="x",padx=16,pady=10)
        self._meta_lbl=tk.Label(top,text="",bg=WHITE,fg=MUTED,font=("Helvetica",10)); self._meta_lbl.pack(side="left")
        self._btn_csv=tk.Button(top,text="",bg=RED,fg=WHITE,font=("Helvetica",10,"bold"),
                                 relief="flat",cursor="hand2",bd=0,padx=12,pady=5,command=self._export_csv)
        self._btn_csv.pack(side="right")
        self._btn_copy=tk.Button(top,text="",bg=WHITE,fg=DARK,font=("Helvetica",10),relief="flat",
                                  bd=1,cursor="hand2",padx=10,pady=5,highlightbackground=BORDER,
                                  command=self._copy_emails)
        self._btn_copy.pack(side="right",padx=(0,8))

        tf=tk.Frame(f,bg=WHITE); tf.pack(fill="both",expand=True,padx=16,pady=(0,14))
        self._tree=ttk.Treeview(tf,columns=("num","name","addr","phone","email","role","src"),
                                 show="headings",selectmode="browse")
        for col,w in [("num",36),("name",195),("addr",155),("phone",100),("email",185),("role",150),("src",90)]:
            self._tree.column(col,width=w,minwidth=30)
        vsb=ttk.Scrollbar(tf,orient="vertical",command=self._tree.yview)
        hsb=ttk.Scrollbar(tf,orient="horizontal",command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.pack(side="right",fill="y"); hsb.pack(side="bottom",fill="x"); self._tree.pack(fill="both",expand=True)
        self._tree.tag_configure("miss",   background="#FFF5F5")
        self._tree.tag_configure("web",    background=AMBER_LT)
        self._tree.tag_configure("hunter", background=GREEN_LT)

    # ── TAB 3 : PARAMÈTRES ───────────────────────────────────────────────────
    def _build_t3(self):
        f=self._f3

        # Canvas + scrollbar pour tout le contenu
        canvas=tk.Canvas(f,bg=WHITE,highlightthickness=0)
        vsb=ttk.Scrollbar(f,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); canvas.pack(fill="both",expand=True)
        inner=tk.Frame(canvas,bg=WHITE)
        win=canvas.create_window((0,0),window=inner,anchor="nw")
        def _resize(e): canvas.configure(scrollregion=canvas.bbox("all")); canvas.itemconfig(win,width=e.width)
        canvas.bind("<Configure>",_resize)

        def section(parent, title):
            fr=tk.Frame(parent,bg=WHITE); fr.pack(fill="x",padx=22,pady=(14,0))
            tk.Label(fr,text=title,bg=WHITE,fg=DARK,font=("Helvetica",11,"bold")).pack(anchor="w")
            tk.Frame(fr,bg=BORDER,height=1).pack(fill="x",pady=(4,8))
            return fr

        def row_spinbox(parent, lbl, desc, var, from_, to_, step=0.5):
            r=tk.Frame(parent,bg=WHITE); r.pack(fill="x",padx=4,pady=3)
            left=tk.Frame(r,bg=WHITE); left.pack(side="left",fill="x",expand=True)
            tk.Label(left,text=lbl,bg=WHITE,fg=DARK,font=("Helvetica",10)).pack(anchor="w")
            tk.Label(left,text=desc,bg=WHITE,fg=MUTED,font=("Helvetica",8)).pack(anchor="w")
            sp=tk.Spinbox(r,textvariable=var,from_=from_,to=to_,increment=step,
                          width=6,font=("Helvetica",10),bg=GRAY,relief="flat",bd=0,
                          highlightthickness=1,highlightbackground=BORDER)
            sp.pack(side="right",padx=(8,0),ipady=4)

        def row_check(parent, lbl, var):
            tk.Checkbutton(parent,text=lbl,variable=var,bg=WHITE,fg=DARK,
                           font=("Helvetica",10),activebackground=WHITE,
                           selectcolor=WHITE,cursor="hand2").pack(anchor="w",padx=4,pady=2)

        # ── Section 1 : Recherche ─────────────────────────────────────────
        s1=section(inner,self.L("p_search") if hasattr(self,"lang") else "Recherche")
        row_spinbox(s1,self.L("p_delay"),self.L("p_delay_desc"),self.delay,0.5,10.0,0.5)
        row_spinbox(s1,self.L("p_timeout"),self.L("p_timeout_desc"),self.timeout_v,5,60,1)
        row_spinbox(s1,self.L("p_retries"),self.L("p_retries_desc"),self.retries_v,1,6,1)
        self._s1_frame=s1

        # ── Section 2 : Filtres ───────────────────────────────────────────
        s2=section(inner,self.L("p_filter") if hasattr(self,"lang") else "Filtres")
        self._chk_generic=tk.Checkbutton(s2,text=self.L("p_also_excl"),variable=self.filter_generic,
                                          bg=WHITE,fg=DARK,font=("Helvetica",10),
                                          activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk_generic.pack(anchor="w",padx=4,pady=(0,6))
        tk.Label(s2,text=self.L("p_excl"),bg=WHITE,fg=DARK,font=("Helvetica",10)).pack(anchor="w",padx=4)
        tk.Label(s2,text=self.L("p_excl_desc"),bg=WHITE,fg=MUTED,font=("Helvetica",8)).pack(anchor="w",padx=4,pady=(0,4))
        self._excl_txt=tk.Text(s2,height=7,font=("Courier",9),bg=GRAY,fg=DARK,relief="flat",bd=0,
                                highlightthickness=1,highlightbackground=BORDER,highlightcolor=RED)
        self._excl_txt.pack(fill="x",padx=4,pady=(0,4))
        self._excl_txt.insert("1.0","\n".join(self.excl))
        self._s2_frame=s2

        # ── Section 3 : Export ────────────────────────────────────────────
        s3=section(inner,self.L("p_export") if hasattr(self,"lang") else "Export")
        self._chk_no_em=tk.Checkbutton(s3,text=self.L("p_include_no_email"),variable=self.include_no_em,
                                        bg=WHITE,fg=DARK,font=("Helvetica",10),
                                        activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk_no_em.pack(anchor="w",padx=4,pady=2)
        self._chk_open=tk.Checkbutton(s3,text=self.L("p_open_csv"),variable=self.open_csv,
                                       bg=WHITE,fg=DARK,font=("Helvetica",10),
                                       activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk_open.pack(anchor="w",padx=4,pady=2)
        self._s3_frame=s3

        # ── Boutons ───────────────────────────────────────────────────────
        btn_row=tk.Frame(inner,bg=WHITE); btn_row.pack(fill="x",padx=22,pady=12)
        self._btn_save=tk.Button(btn_row,text="",bg=RED,fg=WHITE,font=("Helvetica",10,"bold"),
                                  relief="flat",cursor="hand2",bd=0,padx=14,pady=7,command=self._save)
        self._btn_save.pack(side="left")
        self._btn_reset=tk.Button(btn_row,text="",bg=WHITE,fg=MUTED,font=("Helvetica",10),
                                   relief="flat",bd=1,cursor="hand2",padx=10,pady=7,
                                   highlightbackground=BORDER,command=self._reset_settings)
        self._btn_reset.pack(side="left",padx=(8,0))

        self._info2_lbl=tk.Label(inner,text="",bg=RED_LT,fg="#7a0a0a",
                                  font=("Helvetica",9),padx=12,pady=10)
        self._info2_lbl.pack(fill="x",padx=22,pady=(0,16))

    # ── LANGUE ────────────────────────────────────────────────────────────────
    def _switch(self, lang): self.lang=lang; self._apply_lang()

    def _apply_lang(self):
        L=self.L; self.title(L("title"))
        self._nb.tab(0,text=L("tab1")); self._nb.tab(1,text=L("tab2")); self._nb.tab(2,text=L("tab3"))
        self._lbl_url.configure(text=L("url_label"))
        self._btn.configure(text=L("btn_go") if not self._running else L("btn_run"))
        self._chk1.configure(text=L("opt1")); self._chk2.configure(text=L("opt2")); self._chk3.configure(text=L("opt3"))
        self._banner_lbl.configure(text=L("info")); self._log_lbl.configure(text=L("log_lbl"))
        for k,tk_key in [("s1","stat1"),("s2","stat2"),("s3","stat3"),("s4","stat4")]:
            self._slbl[k].configure(text=L(tk_key))
        rl={"FR":"Rôle","ES":"Rol","EN":"Role"}.get(self.lang,"Rôle")
        for col,key in [("num","col_num"),("name","col_name"),("addr","col_addr"),
                        ("phone","col_phone"),("email","col_email"),("src","col_src")]:
            self._tree.heading(col,text=L(key))
        self._tree.heading("role",text=rl)
        self._btn_copy.configure(text=L("btn_copy")); self._btn_csv.configure(text=L("btn_csv"))
        self._btn_save.configure(text=L("btn_save")); self._btn_reset.configure(text=L("btn_reset"))
        self._info2_lbl.configure(text=L("info2") if "info2" in T[self.lang] else "Données traitées localement.")
        self._lbl_status.configure(text=L("ready"))
        # Update settings labels
        self._chk_generic.configure(text=L("p_also_excl"))
        self._chk_no_em.configure(text=L("p_include_no_email"))
        self._chk_open.configure(text=L("p_open_csv"))
        if self.results: self._refresh()

    # ── LOGIQUE ───────────────────────────────────────────────────────────────
    def _log_add(self, msg):
        self._log.configure(state="normal")
        self._log.insert("end", f"▸ {msg}\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_prog(self, pct, lbl=""):
        self._prog_var.set(pct)
        if lbl: self._prog_lbl.configure(text=lbl)
        self.update_idletasks()

    def _save(self):
        raw=self._excl_txt.get("1.0","end").strip()
        self.excl=[l.strip().lstrip("@") for l in raw.splitlines() if l.strip()]
        messagebox.showinfo("✓", self.L("info_saved"))

    def _reset_settings(self):
        self.excl=list(EXCL_DEFAULT)
        self._excl_txt.delete("1.0","end"); self._excl_txt.insert("1.0","\n".join(self.excl))
        self.delay.set(1.2); self.timeout_v.set(18); self.retries_v.set(3)
        self.filter_generic.set(False); self.include_no_em.set(True); self.open_csv.set(False)
        messagebox.showinfo("✓", self.L("info_reset"))

    def _start(self):
        if self._running: return
        url=self._url_var.get().strip()
        if not url.startswith("http"): messagebox.showerror("",self.L("err_url")); return
        self._running=True
        self._btn.configure(state="disabled",text=self.L("btn_run"))
        self._log.configure(state="normal"); self._log.delete("1.0","end"); self._log.configure(state="disabled")
        self._set_prog(0,"")
        for v in self._sv.values(): v.set("—")
        excl=self.excl if self._v3.get() else []
        threading.Thread(target=self._run,args=(url,excl),daemon=True).start()

    def _run(self, url, excl):
        try:
            to=self.timeout_v.get(); rt=self.retries_v.get(); dly=self.delay.get()
            fg=self.filter_generic.get()

            dealers=scrape_page(url,excl,self._log_add,self._set_prog,timeout=to,retries=rt)
            self._set_prog(45,"Enrichissement emails…")

            if self._v1.get():
                pending=[d for d in dealers if not d["emails"]]
                self._log_add(f"━━━ Enrichissement de {len(pending)} concessionnaires ━━━")
                self._log_add(f"Pipeline: Google → Site web → Hunter.io")
                self._log_add(f"4 concessionnaires traités en parallèle")
                self._log_add(f"─────────────────────────────────────────")
                done_count = [0]
                lock = threading.Lock()

                def enrich_one(d):
                    try:
                        ne,src=enrich_dealer(d,excl,self._log_add,delay=dly,timeout=to)
                        if ne:
                            if fg: ne={e:r for e,r in ne.items() if e.split("@")[0].lower() not in GENERIC_PREFIXES}
                            d["emails"]=ne; d["src"]=src
                    except Exception as e:
                        self._log_add(f"  Erreur {d['name'][:30]}: {e}")
                    finally:
                        with lock:
                            done_count[0] += 1
                            pct = 45 + int(48 * done_count[0] / max(len(pending), 1))
                            self._set_prog(pct, f"Enrichissement {done_count[0]}/{len(pending)} — {d['name'][:25]}")

                # Run 4 dealers in parallel
                MAX_WORKERS = 4
                threads = []
                for d in pending:
                    t = threading.Thread(target=enrich_one, args=(d,), daemon=True)
                    threads.append(t)
                    t.start()
                    # Limit concurrency to MAX_WORKERS
                    running = [t for t in threads if t.is_alive()]
                    while len(running) >= MAX_WORKERS:
                        time.sleep(0.3)
                        running = [t for t in threads if t.is_alive()]

                # Wait for all to finish
                for t in threads:
                    t.join(timeout=30)

            if self._v2.get():
                seen,uniq=set(),[]
                for d in dealers:
                    k=re.sub(r"[^a-z0-9]","",d["name"].lower())[:20]
                    if k not in seen: seen.add(k); uniq.append(d)
                dealers=uniq

            self._set_prog(100,"Terminé !")
            total=sum(len(d["emails"]) for d in dealers)
            self._log_add(f"─── {len(dealers)} concessionnaires · {total} emails au total")
            self.results=dealers
            self.after(0,self._finish)
        except Exception as e:
            self.after(0,lambda:messagebox.showerror("Erreur",str(e)))
            self._log_add(f"ERREUR: {e}")
            self.after(0,lambda:self._btn.configure(state="normal",text=self.L("btn_go")))
            self._running=False

    def _finish(self):
        self._running=False; d=self.results
        em=sum(len(x["emails"]) for x in d)
        wb=sum(1 for x in d if x["src"] in ("web","hunter"))
        ad=sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d))); self._sv["s2"].set(str(em))
        self._sv["s3"].set(str(wb)); self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal",text=self.L("btn_again"))
        self._lbl_status.configure(text=self.L("last")+datetime.now().strftime("%H:%M"))
        self._refresh(); self._nb.select(self._f2)

    def _refresh(self):
        d=self.results
        em=sum(len(x["emails"]) for x in d); ad=sum(1 for x in d if x["addr"])
        self._meta_lbl.configure(
            text=f"{len(d)} {self.L('stat1')} · {em} {self.L('stat2')} · {ad} {self.L('stat4')}")
        for row in self._tree.get_children(): self._tree.delete(row)
        sm={"page":self.L("src_page"),"web":self.L("src_web"),"hunter":self.L("src_hunter")}
        n=1
        for x in d:
            sl=sm.get(x["src"],"—")
            if not x["emails"]:
                self._tree.insert("","end",tags=("miss",),
                    values=(n,x["name"],x["addr"],x["phone"],"—","—",sl)); n+=1
            else:
                for i,(email,role) in enumerate(sorted(x["emails"].items())):
                    tag={"page":"","web":"web","hunter":"hunter"}.get(x["src"],"")
                    self._tree.insert("","end",tags=(tag,),values=(
                        n if i==0 else "",
                        x["name"]  if i==0 else "",
                        x["addr"]  if i==0 else "",
                        x["phone"] if i==0 else "",
                        email, role,
                        sl if i==0 else "",
                    ))
                n+=1

    def _copy_emails(self):
        em=sorted({e for x in self.results for e in x["emails"]})
        if not em: messagebox.showinfo("",self.L("no_copy")); return
        self.clipboard_clear(); self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓",f"{len(em)} {self.L('copied')}")

    def _export_csv(self):
        if not self.results: messagebox.showinfo("",self.L("no_copy")); return
        desk=os.path.join(os.path.expanduser("~"),"Desktop")
        os.makedirs(desk,exist_ok=True)
        fname=f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        fpath=os.path.join(desk,fname)
        sm={"page":self.L("src_page"),"web":self.L("src_web"),"hunter":self.L("src_hunter")}
        date_s=datetime.now().strftime("%d/%m/%Y"); rows=0
        with open(fpath,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f)
            w.writerow([self.L("col_name"),self.L("col_addr"),self.L("col_phone"),
                        self.L("col_email"),self.L("col_role"),"Site web",self.L("col_src"),"Date"])
            for x in self.results:
                if not x["emails"] and not self.include_no_em.get(): continue
                sl=sm.get(x["src"],"—"); site=x.get("website","")
                if not x["emails"]:
                    w.writerow([x["name"],x["addr"],x["phone"],"","",site,sl,date_s]); rows+=1
                else:
                    for i,(email,role) in enumerate(sorted(x["emails"].items())):
                        w.writerow([
                            x["name"]  if i==0 else "",
                            x["addr"]  if i==0 else "",
                            x["phone"] if i==0 else "",
                            email, role,
                            site       if i==0 else "",
                            sl         if i==0 else "",
                            date_s     if i==0 else "",
                        ]); rows+=1
        messagebox.showinfo("✓",f"{self.L('export_ok')}\n{fname}\n\n{rows} lignes")
        if self.open_csv.get():
            try: os.startfile(fpath)
            except Exception:
                try: os.system(f'open "{fpath}"')
                except Exception: pass

if __name__ == "__main__":
    App().mainloop()
