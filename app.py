#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silence.eco — Dealer Finder  |  Production v1.0
Architecture: fetch → parse → validate → enrich → export
"""

# ── Auto-install dependencies ─────────────────────────────────────────────────
import subprocess, sys, os

def _bootstrap():
    pkgs = {"bs4":"beautifulsoup4","selenium":"selenium",
            "webdriver_manager":"webdriver-manager","requests":"requests"}
    missing = []
    for mod, pkg in pkgs.items():
        try: __import__(mod)
        except ImportError: missing.append(pkg)
    if missing:
        try:
            import tkinter as tk
            r = tk.Tk(); r.withdraw()
            from tkinter import messagebox
            messagebox.showinfo("Silence Dealer Finder",
                f"Installation des composants requis…\n({', '.join(missing)})\n\nL'app redémarre dans 30 secondes.")
            r.destroy()
        except: pass
        subprocess.check_call([sys.executable,"-m","pip","install","--quiet"]+missing)
        os.execv(sys.executable,[sys.executable]+sys.argv)
_bootstrap()

# ── Imports ───────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading, json, re, time, csv, random, unicodedata
import urllib.request, urllib.parse, urllib.error, http.cookiejar
from datetime import datetime

# ── Keys (built-in) ───────────────────────────────────────────────────────────
HUNTER_KEY = "6f720d52e7ff130ef0717a890cd35abcac84c6fd"

# ── Brand ─────────────────────────────────────────────────────────────────────
C = dict(
    red="#D01A20", red_d="#A01015", red_lt="#FAE8E8",
    dark="#1C1C1E", dark2="#2C2C2E", dark3="#3A3A3C",
    gray="#F2F2F7", white="#FFFFFF", muted="#8E8E93",
    border="#E5E5EA", green="#34C759", amber="#FF9500",
    blue="#007AFF",
)

# ── i18n ──────────────────────────────────────────────────────────────────────
STRINGS = {
"FR": dict(
    title="Silence.eco — Dealer Finder",
    tab_ex="Extraction", tab_re="Résultats", tab_se="Paramètres",
    url_lbl="URL du réseau concessionnaires", btn_go="Extraire",
    btn_run="En cours…", btn_again="Relancer",
    opt1="Enrichir les emails", opt2="Dédupliquer", opt3="Exclure domaines constructeur",
    desc="Analyse · Extrait · Valide · Enrichit",
    log_hdr="Journal en direct",
    c_num="#", c_name="Concessionnaire", c_addr="Adresse",
    c_phone="Téléphone", c_email="Email", c_role="Rôle", c_src="Source",
    s_page="Page", s_web="Web", s_hunter="Hunter.io",
    st1="Concessionnaires", st2="Emails validés", st3="Via web", st4="Adresses",
    btn_copy="Copier les emails", btn_csv="Exporter CSV",
    no_res="Lancez une extraction pour voir les résultats",
    p_delay="Délai entre requêtes (s)", p_timeout="Timeout (s)",
    p_retries="Tentatives", p_excl="Domaines à exclure",
    p_excl_hint="Un domaine par ligne",
    p_no_email="Inclure sans email dans CSV",
    p_open="Ouvrir CSV après export",
    btn_save="Enregistrer", btn_reset="Réinitialiser",
    saved="Paramètres enregistrés.", reset="Paramètres réinitialisés.",
    err_url="URL invalide — doit commencer par http",
    exp_ok="CSV sauvegardé :", exp_rows=" lignes",
    ready="Prêt", last="Run : ", copied=" emails copiés",
    no_copy="Aucun email.",
),
"ES": dict(
    title="Silence.eco — Dealer Finder",
    tab_ex="Extracción", tab_re="Resultados", tab_se="Ajustes",
    url_lbl="URL de la red de concesionarios", btn_go="Extraer",
    btn_run="En proceso…", btn_again="Reiniciar",
    opt1="Enriquecer emails", opt2="Eliminar duplicados", opt3="Excluir dominios fabricante",
    desc="Analiza · Extrae · Valida · Enriquece",
    log_hdr="Registro en vivo",
    c_num="#", c_name="Concesionario", c_addr="Dirección",
    c_phone="Teléfono", c_email="Email", c_role="Rol", c_src="Fuente",
    s_page="Página", s_web="Web", s_hunter="Hunter.io",
    st1="Concesionarios", st2="Emails validados", st3="Vía web", st4="Direcciones",
    btn_copy="Copiar emails", btn_csv="Exportar CSV",
    no_res="Lance una extracción para ver los resultados",
    p_delay="Retraso entre solicitudes (s)", p_timeout="Tiempo de espera (s)",
    p_retries="Intentos", p_excl="Dominios a excluir",
    p_excl_hint="Un dominio por línea",
    p_no_email="Incluir sin email en CSV",
    p_open="Abrir CSV tras exportar",
    btn_save="Guardar", btn_reset="Restablecer",
    saved="Ajustes guardados.", reset="Ajustes restablecidos.",
    err_url="URL inválida — debe empezar por http",
    exp_ok="CSV guardado:", exp_rows=" filas",
    ready="Listo", last="Run: ", copied=" emails copiados",
    no_copy="Sin emails.",
),
"EN": dict(
    title="Silence.eco — Dealer Finder",
    tab_ex="Extraction", tab_re="Results", tab_se="Settings",
    url_lbl="Dealer network page URL", btn_go="Extract",
    btn_run="Running…", btn_again="Run Again",
    opt1="Enrich emails", opt2="Deduplicate", opt3="Exclude manufacturer domains",
    desc="Analyse · Extract · Validate · Enrich",
    log_hdr="Live log",
    c_num="#", c_name="Dealer", c_addr="Address",
    c_phone="Phone", c_email="Email", c_role="Role", c_src="Source",
    s_page="Page", s_web="Web", s_hunter="Hunter.io",
    st1="Dealers", st2="Validated emails", st3="Via web", st4="Addresses",
    btn_copy="Copy emails", btn_csv="Export CSV",
    no_res="Run an extraction to see results",
    p_delay="Delay between requests (s)", p_timeout="Timeout (s)",
    p_retries="Retries", p_excl="Domains to exclude",
    p_excl_hint="One domain per line",
    p_no_email="Include no-email rows in CSV",
    p_open="Open CSV after export",
    btn_save="Save", btn_reset="Reset",
    saved="Settings saved.", reset="Settings reset.",
    err_url="Invalid URL — must start with http",
    exp_ok="CSV saved:", exp_rows=" rows",
    ready="Ready", last="Run: ", copied=" emails copied",
    no_copy="No emails.",
),
}

EXCL_DEFAULT = ["silence.eco","aixam.com","microcar.fr","ligier.fr","chatenet.com",
                "casalini.it","bellier.fr","grecav.com","renault.fr","peugeot.fr",
                "citroen.fr","toyota.fr","volkswagen.fr","ford.fr","opel.fr"]

SKIP_DOMAINS = ["duckduckgo.com","google.","bing.","facebook.","instagram.",
                "twitter.","linkedin.","youtube.","pagesjaunes.","societe.com",
                "verif.com","pappers.","wix.","squarespace.","shopify.",
                "wordpress.","example.com","test.com","w3.org","schema.org",
                "cloudflare.","sentry.","microsoft.","apple.","amazon.",
                "leboncoin.","lacentrale.","largus.","caradisiac.",
                # Insurance / finance (never a dealer email)
                "sollyazar.","allianz.","axa.","maif.","macif.","matmut.",
                "groupama.","covea.","generali.","mma.","aviva.","april.",
                "credit-agricole.","bnpparibas.","lcl.","caisse-epargne.",
                "sg.","boursorama.",
                # Job boards / directories
                "indeed.","linkedin.","monster.","cadremploi.","pole-emploi.",
                "annuaire.","pagesblanches.",]

FREE_MAIL  = ["gmail.","orange.","hotmail.","yahoo.","outlook.","sfr.",
              "wanadoo.","free.","laposte.","bbox.","live.","icloud.","msn."]

EMAIL_RE   = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE   = re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
ADDR_RE    = re.compile(r"\d{1,4}[\s,]+[^\d\n]{5,60}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,35}",re.I)

ROLE_MAP = [
    (["direction","directeur","directrice","pdg","ceo","dg","gerant","patron"],"Direction"),
    (["commercial","vente","ventes","sales","vendeur"],"Commercial"),
    (["marketing","communication","promo","digital"],"Marketing"),
    (["comptabilite","comptable","compta","facturation","finance"],"Comptabilité"),
    (["contact","info","information","accueil","reception","bonjour","hello"],"Contact"),
    (["apv","atelier","technique","sav","service","reparation"],"Après-vente"),
    (["rh","hr","recrutement","emploi"],"RH"),
    (["secretariat","admin","administration","assistante"],"Administration"),
    (["pieces","parts","magasin","boutique"],"Pièces / Boutique"),
]

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

# ═════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

def norm(s):
    """Normalize: lowercase, remove accents, keep alphanum only."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)

def guess_role(email):
    local = norm(email.split("@")[0])
    for kws, lbl in ROLE_MAP:
        if any(k in local for k in kws): return lbl
    return "Équipe"

def is_valid_email(e):
    """Basic structural validation."""
    if not e or len(e) < 6 or "@" not in e: return False
    local, dom = e.split("@")[0].lower(), e.split("@")[-1].lower()
    if re.search(r"\.(png|jpg|gif|css|js|svg|ico|woff|pdf)$", dom): return False
    if "." not in dom: return False
    return True

def email_belongs_to_dealer(email, dealer_name, dealer_addr=""):
    """
    Strict validation: is this email actually from this dealer?

    Returns (bool, confidence 0-1, explanation)

    Rules (in priority order):
    1. Domain contains dealer name keyword → HIGH confidence
    2. Local part contains dealer name keyword → HIGH confidence
    3. It's a generic professional prefix on a business domain → MEDIUM
    4. Free provider (gmail etc) needs strong name match → STRICT
    5. Fuzzy similarity score → only if >= 0.65
    """
    if not is_valid_email(email): return False, 0.0, "email malformé"

    local  = norm(email.split("@")[0])
    dom    = norm(email.split("@")[-1].split(".")[0])
    is_free = any(p in email.split("@")[-1] for p in FREE_MAIL)

    # Name keywords (words > 2 chars, normalized)
    name_kws = [norm(w) for w in re.split(r"[\s\-\'&/,.()]", dealer_name) if len(w) > 2]
    # City from address
    city_kws = []
    if dealer_addr:
        m = re.search(r"\d{5}\s+(.+)", dealer_addr)
        if m:
            city_kws = [norm(w) for w in m.group(1).split() if len(w) > 3]

    # ── Rule 1: domain matches dealer name ───────────────────────────────
    for kw in name_kws:
        if len(kw) >= 4:
            if kw in dom or dom in kw:
                return True, 0.95, f"domaine '{dom}' correspond à '{kw}'"

    # ── Rule 2: local part contains dealer name keyword ───────────────────
    for kw in name_kws:
        if len(kw) >= 4 and kw in local:
            return True, 0.90, f"préfixe contient '{kw}'"

    # ── Rule 3: dealer name keyword in full email ─────────────────────────
    full = norm(email)
    for kw in name_kws:
        if len(kw) >= 5 and kw in full:
            return True, 0.85, f"email contient '{kw}'"

    # ── Rule 4: city in domain ────────────────────────────────────────────
    for kw in city_kws:
        if len(kw) >= 4 and kw in dom:
            return True, 0.70, f"ville '{kw}' dans domaine"

    # ── Rule 5: professional generic on business domain ───────────────────
    PRO_PREFIXES = ["contact","info","accueil","commercial","vente","direction",
                    "secretariat","apv","sav","service","garage","auto","moto",
                    "vsp","reception","marketing","admin","manager","concess"]
    if not is_free:
        for pfx in PRO_PREFIXES:
            if pfx in local:
                # Only valid if domain looks like a business (has >4 chars before TLD)
                dom_full = email.split("@")[-1].lower()
                dom_name_part = dom_full.split(".")[0]
                if len(dom_name_part) >= 4:
                    return True, 0.72, f"préfixe pro '{pfx}' sur domaine métier"

    # ── Rule 6: initials match ────────────────────────────────────────────
    if name_kws:
        initials = "".join(w[0] for w in name_kws if w)
        abbrev   = "".join(w[:4] for w in name_kws[:3] if w)
        if len(initials) >= 3 and initials in local:
            return True, 0.78, f"initiales '{initials}' dans préfixe"
        if len(abbrev) >= 5 and abbrev in local:
            return True, 0.75, f"abréviation '{abbrev}' dans préfixe"

    # ── Rule 7: local part contains significant part of dealer name ─────
    # e.g. "nautimarine@gmail.com" → local="nautimarine" → matches "NAUTIMARINE"
    # e.g. "rhonalpauto@orange.fr" → local="rhonalpauto" → matches "RHONALP AUTO"
    name_joined = "".join(name_kws)
    if name_joined and len(name_joined) >= 4:
        # Check if local is basically the dealer name concatenated
        # e.g. local="rhonalpauto", name_kws=["rhonalp","auto"] → "rhonalp" in "rhonalpauto"
        for kw in name_kws:
            if len(kw) >= 3 and kw in local:
                return True, 0.85, f"nom '{kw}' dans préfixe email"

        # Fuzzy ratio — same threshold for all providers
        # (free providers already filtered by rule 2 above if name matches)
        common = sum(1 for c in local if c in name_joined)
        score  = common / max(len(local), len(name_joined))
        # For free providers: need 65% (not 72%) — catches "rhonalpauto@gmail"
        # For business domains: need 50%
        threshold = 0.65 if is_free else 0.50
        if score >= threshold:
            return True, round(score, 2), f"similarité {score:.0%}"

    return False, 0.0, "aucun lien avec le concessionnaire"


# ═════════════════════════════════════════════════════════════════════════════
# NETWORK
# ═════════════════════════════════════════════════════════════════════════════

def fetch(url, timeout=18, retries=3, referer="https://www.google.com"):
    """Fetch with Selenium (real Chrome) → requests → urllib cascade."""

    # ── Selenium: real Chrome, impossible to block ────────────────────────
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument(f"--user-agent={random.choice(UA_POOL)}")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        driver = None
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        except Exception:
            driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(1.5)
        html = driver.page_source
        driver.quit()
        if html and len(html) > 3000:
            return html
    except Exception:
        pass

    # ── requests with session ─────────────────────────────────────────────
    try:
        import requests
        s = requests.Session()
        s.headers.update({
            "User-Agent": random.choice(UA_POOL),
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
            "Referer": referer,
        })
        try: s.get(re.match(r"https?://[^/]+", url).group(0), timeout=6)
        except: pass
        r = s.get(url, timeout=timeout, allow_redirects=True)
        r.encoding = r.apparent_encoding or "utf-8"
        if len(r.text) > 2000: return r.text
    except Exception:
        pass

    # ── urllib fallback ───────────────────────────────────────────────────
    last = None
    for attempt in range(retries):
        try:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [
                ("User-Agent", random.choice(UA_POOL)),
                ("Accept", "text/html,*/*;q=0.9"),
                ("Accept-Language", "fr-FR,fr;q=0.9"),
                ("Referer", referer),
            ]
            with opener.open(url, timeout=timeout) as r:
                raw = r.read()
                enc = r.headers.get_content_charset("utf-8") or "utf-8"
                return raw.decode(enc, errors="replace")
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last or Exception(f"Impossible de charger: {url}")


def get_emails_raw(text, excl):
    """Extract all structurally valid emails, excluding known constructors."""
    out = set()
    for m in EMAIL_RE.finditer(text):
        e = m.group(0).lower().strip(".,;:<>\"'()")
        dom = e.split("@")[-1]
        if (is_valid_email(e)
                and not any(x in dom for x in excl)
                and not any(s in dom for s in SKIP_DOMAINS)):
            out.add(e)
    return out


def get_phones(text):
    seen, out = set(), []
    for m in PHONE_RE.finditer(text):
        p = re.sub(r"[\s.\-]", "", m.group(0))
        if p not in seen: seen.add(p); out.append(p)
    return out


# ═════════════════════════════════════════════════════════════════════════════
# SCRAPE DEALER PAGE
# ═════════════════════════════════════════════════════════════════════════════

def scrape_dealer_page(url, excl, log, prog, timeout=18, retries=3):
    prog(5, "Chargement de la page…")
    log(f"GET {url}")
    html = fetch(url, timeout=timeout, retries=retries)
    log(f"Page reçue — {len(html)//1024} Ko")
    prog(18, "Extraction des concessionnaires…")

    dealers = []
    base_url = (re.match(r"https?://[^/]+", url) or type("x",[],{"group":lambda s,i:""})()).group(0)
    path_dir = re.sub(r"/[^/]*$", "/", urllib.parse.urlparse(url).path)

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script","style","nav","footer","head","header","aside"]): t.decompose()

        seen = set()

        # ── Method A: h2/h3 headings = dealer names ───────────────────────
        for htag in soup.find_all(["h2","h3","h4"]):
            a = htag.find("a") or htag
            name = a.get_text(strip=True)
            if not name or len(name) < 3 or len(name) > 100: continue
            SKIP_START = ("tél","tel","fax","email","adresse","voir","notre","les ",
                          "le ","la ","pour ","avec ","sans ","tous","département",
                          "région","accueil","bienvenue","cliquez","réseau","network",
                          "voiture sans permis","scooter","moto électrique")
            if any(name.lower().startswith(s) for s in SKIP_START): continue
            if re.match(r"^\d", name): continue

            # Filter department/region names: "Ain (01)", "Aisne (02)", "Nord", etc.
            # Pattern: short word + optional (XX) = French department
            if re.match(r"^[A-ZÀ-Ÿa-zà-ÿ\s\-]+\s*\(\d{2,3}\)\s*$", name): continue
            if re.match(r"^[A-ZÀ-Ÿa-zà-ÿ\s\-]+\s*\d{2,3}\s*$", name.strip()) and len(name.split()) <= 3: continue
            # Single generic word = region/category, not a dealer
            REGIONS = {"ain","aisne","allier","alpes","ardèche","ardennes","ariège",
                       "aube","aude","aveyron","bouches","calvados","cantal","charente",
                       "cher","corrèze","corse","côte","creuse","dordogne","doubs",
                       "drôme","eure","finistère","gard","gers","gironde","hérault",
                       "ille","indre","isère","jura","landes","loir","loire","loiret",
                       "lot","lozère","maine","manche","marne","mayenne","meurthe",
                       "meuse","morbihan","moselle","nièvre","nord","oise","orne",
                       "pas","puy","pyrénées","bas-rhin","haut-rhin","rhône","haute-saône",
                       "saône","sarthe","savoie","paris","seine","deux-sèvres","somme",
                       "tarn","var","vaucluse","vendée","vienne","vosges","yonne",
                       "territoire","essonne","hauts","val","france","espagne","spain"}
            name_lower = name.lower().strip()
            # Remove department number if present
            name_no_num = re.sub(r"\s*\(\d+\)\s*$","",name_lower).strip()
            if name_no_num in REGIONS: continue
            # Also skip if it looks like "Region (01)" pattern used by Aixam
            if re.search(r"\(\d{2,3}\)", name): continue

            key = norm(name)[:22]
            if not key or key in seen: continue
            seen.add(key)

            # Collect sibling content after heading
            parts, node = [], htag.next_sibling
            for _ in range(50):
                if node is None: break
                if hasattr(node,"name") and node.name in ["h2","h3","h4"]: break
                parts.append(str(node)); node = node.next_sibling
            bsoup = BeautifulSoup("".join(parts), "html.parser")
            btxt  = bsoup.get_text(" ", strip=True)
            ptxt  = htag.parent.get_text(" ", strip=True) if htag.parent else ""

            # Address
            addr = ""
            am = ADDR_RE.search(btxt) or ADDR_RE.search(ptxt)
            if am: addr = am.group(0).strip()[:120]
            if not addr:
                for tag in bsoup.find_all(["p","address","div","span"]):
                    t2 = tag.get_text(" ", strip=True)
                    if re.search(r"\d{5}", t2) and len(t2) < 200:
                        addr = t2[:120]; break

            phones = get_phones(btxt + " " + ptxt)
            phone  = phones[0] if phones else ""

            # Emails on page for this block (already validated by proximity)
            pg_emails = get_emails_raw(btxt + " " + ptxt, excl)
            for atag in bsoup.find_all("a", href=True):
                h2 = atag["href"]
                if h2.startswith("mailto:"):
                    e = h2[7:].split("?")[0].strip().lower()
                    if is_valid_email(e) and not any(x in e.split("@")[-1] for x in excl):
                        pg_emails.add(e)

            # Validate page emails against dealer
            validated = {}
            for e in pg_emails:
                ok, score, reason = email_belongs_to_dealer(e, name, addr)
                if ok: validated[e] = guess_role(e)

            # Profile URL
            profile = ""
            a_tag = htag.find("a")
            if a_tag and a_tag.get("href"):
                href = a_tag["href"]
                if href.startswith("/"): href = base_url + href
                profile = href
            if not profile and htag.parent:
                for a2 in htag.parent.find_all("a", href=True):
                    href = a2["href"]
                    if href.startswith("/"): href = base_url + href
                    if (base_url in href and path_dir in href
                            and href.rstrip("/") != url.rstrip("/")):
                        profile = href; break

            dealers.append({
                "name": name[:80], "addr": addr, "phone": phone,
                "website": "", "profile_url": profile,
                "emails": validated,
                "src": "page" if validated else "pending",
            })

        log(f"Méthode h3: {len(dealers)} concessionnaires")

        # ── Method B: CSS selectors ───────────────────────────────────────
        if len(dealers) < 5:
            log("Tentative sélecteurs CSS…")
            best, best_n = [], 0
            for sel in ["[class*='dealer']","[class*='concess']","[class*='revendeur']",
                        "[class*='reseau']","[class*='network']","[class*='store']",
                        "[class*='location']","article","[class*='card']","[class*='item']"]:
                found = soup.select(sel)
                valid = [b for b in found if (PHONE_RE.search(b.get_text())
                         or EMAIL_RE.search(b.get_text())
                         or len(b.get_text(strip=True)) > 40)]
                if len(valid) > best_n: best_n = len(valid); best = valid
            log(f"CSS: {best_n} blocs")
            for blk in best:
                txt = blk.get_text(" ", strip=True)
                if len(txt) < 15: continue
                name = ""
                for tag in blk.find_all(["h2","h3","h4","h5","strong","b"]):
                    v = tag.get_text(strip=True)
                    if 3 < len(v) < 90 and not PHONE_RE.match(v): name = v; break
                if not name: continue
                key = norm(name)[:22]
                if not key or key in seen: continue
                seen.add(key)
                am = ADDR_RE.search(txt); addr = am.group(0)[:120] if am else ""
                phones = get_phones(txt); phone = phones[0] if phones else ""
                pg_emails = get_emails_raw(txt, excl)
                for a2 in blk.find_all("a", href=True):
                    h2 = a2["href"]
                    if h2.startswith("mailto:"):
                        e = h2[7:].split("?")[0].strip().lower()
                        if is_valid_email(e): pg_emails.add(e)
                validated = {}
                for e in pg_emails:
                    ok, sc, rs = email_belongs_to_dealer(e, name, addr)
                    if ok: validated[e] = guess_role(e)
                dealers.append({"name":name[:80],"addr":addr,"phone":phone,
                    "website":"","profile_url":"","emails":validated,
                    "src":"page" if validated else "pending"})

        # ── Method C: phone-block fallback ────────────────────────────────
        if len(dealers) < 5:
            log("Fallback blocs téléphone…")
            for blk in soup.find_all(["div","li","article","p","section"]):
                if not PHONE_RE.search(blk.get_text()): continue
                txt = blk.get_text(" ", strip=True)
                if len(txt) < 20 or len(txt) > 800: continue
                name = ""
                for tag in blk.find_all(["strong","b","span"]):
                    v = tag.get_text(strip=True)
                    if 3 < len(v) < 90 and not PHONE_RE.match(v): name = v; break
                if not name: continue
                key = norm(name)[:22]
                if not key or key in seen: continue
                seen.add(key)
                phones = get_phones(txt); phone = phones[0] if phones else ""
                am = ADDR_RE.search(txt); addr = am.group(0)[:120] if am else ""
                dealers.append({"name":name[:80],"addr":addr,"phone":phone,
                    "website":"","profile_url":"","emails":{},"src":"pending"})

    except ImportError:
        log("Mode regex (bs4 non installé)")
        clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        names = re.findall(r"<h3[^>]*>(?:<a[^>]*>)?([^<]{3,80})(?:</a>)?</h3>", html, re.I)
        seen = set()
        for name in names:
            name = name.strip()
            key = norm(name)[:22]
            if not key or key in seen or len(name) < 3: continue
            seen.add(key)
            idx = clean.find(name[:15])
            ctx = clean[max(0,idx-30):idx+400] if idx >= 0 else ""
            phones = get_phones(ctx); phone = phones[0] if phones else ""
            am = ADDR_RE.search(ctx); addr = am.group(0)[:120] if am else ""
            dealers.append({"name":name[:80],"addr":addr,"phone":phone,
                "website":"","profile_url":"","emails":{},"src":"pending"})

    # Dedup
    final, seen2 = [], set()
    for d in dealers:
        k = norm(d["name"])[:20]
        if k and k not in seen2: seen2.add(k); final.append(d)

    log(f"✓ {len(final)} concessionnaires uniques")
    return final


# ═════════════════════════════════════════════════════════════════════════════
# EMAIL ENRICHMENT
# ═════════════════════════════════════════════════════════════════════════════

def search_emails_for_dealer(dealer, excl, log):
    """
    Search emails for one dealer using multiple sources.
    STOPS as soon as validated emails are found.
    Each email is strictly validated against the dealer name.
    """
    name = dealer["name"]
    addr = dealer["addr"]
    name_clean = re.sub(r"[^\w\s]", " ", name).strip()

    city = ""
    if addr:
        m = re.search(r"\d{5}\s+(\S+)", addr)
        if m: city = m.group(1)

    def extract_and_validate(html, source):
        """Extract emails from HTML, validate each against dealer, return validated set."""
        text  = re.sub(r"<[^>]+>", " ", html)
        text  = re.sub(r"\s+", " ", text)

        # Strategy: look near dealer name FIRST (most accurate)
        name_pos = text.lower().find(name_clean.lower()[:12])
        if name_pos >= 0:
            window = text[max(0, name_pos-50):name_pos+400]
            raw = get_emails_raw(window, excl)
        else:
            raw = set()

        # Also check mailto links in the full HTML near dealer name
        html_pos = html.lower().find(name_clean.lower()[:12])
        if html_pos >= 0:
            win_html = html[max(0, html_pos-100):html_pos+600]
            for m2 in re.finditer(r"mailto:([^\s\"'<>?]+)", win_html):
                e = m2.group(1).strip().lower()
                if is_valid_email(e): raw.add(e)

        # If nothing near name, scan full page
        if not raw:
            raw = get_emails_raw(text, excl)

        validated = {}
        for e in raw:
            ok, score, reason = email_belongs_to_dealer(e, name, addr)
            if ok:
                validated[e] = guess_role(e)
                log(f"  ✅ [{source}] {e}  ({reason})")
            else:
                log(f"  ✗  [{source}] rejeté: {e}  ({reason})")
        return validated

    # ── Source 1: Google via Selenium ─────────────────────────────────────
    google_queries = [
        f'"{name_clean}" email',
        f'"{name_clean}" {city} email' if city else None,
        f'{name_clean} concessionnaire contact email',
    ]
    for q in [x for x in google_queries if x]:
        try:
            log(f"  🔍 Google: {q[:60]}")
            url = "https://www.google.com/search?q=" + urllib.parse.quote(q) + "&hl=fr&num=10"
            html = fetch(url, timeout=12, referer="https://www.google.com")
            validated = extract_and_validate(html, "Google")
            if validated:
                log(f"  ✔ Trouvé via Google — on passe au suivant")
                return validated
            time.sleep(random.uniform(0.8, 1.5))
        except Exception as e:
            log(f"  ↳ Google: {str(e)[:40]}")
            break

    # ── Source 2: Google Maps via Selenium ────────────────────────────────
    try:
        log(f"  🗺️  Google Maps: {name_clean[:40]}")
        q = urllib.parse.quote(f"{name_clean} {city} concessionnaire".strip())
        html = fetch(f"https://www.google.com/maps/search/{q}?hl=fr",
                     timeout=12, referer="https://www.google.com/maps")
        validated = extract_and_validate(html, "Maps")
        if validated:
            log(f"  ✔ Trouvé via Google Maps")
            return validated
    except Exception:
        pass

    # ── Source 3: DuckDuckGo ──────────────────────────────────────────────
    for q in [f'"{name_clean}" email', f'{name_clean} {city} contact' if city else None]:
        if not q: continue
        try:
            log(f"  🔍 DuckDuckGo: {q[:55]}")
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
            html = fetch(url, timeout=12, referer="https://duckduckgo.com")
            validated = extract_and_validate(html, "DDG")
            if validated:
                log(f"  ✔ Trouvé via DuckDuckGo")
                return validated
            time.sleep(random.uniform(0.5, 1.0))
        except Exception:
            break

    # ── Source 4: Bing ────────────────────────────────────────────────────
    try:
        log(f"  🔍 Bing: {name_clean[:40]}")
        q = urllib.parse.quote(f'"{name_clean}" email contact')
        html = fetch(f"https://www.bing.com/search?q={q}&setlang=fr",
                     timeout=12, referer="https://www.bing.com")
        validated = extract_and_validate(html, "Bing")
        if validated:
            log(f"  ✔ Trouvé via Bing")
            return validated
    except Exception:
        pass

    # ── Source 5: Pages Jaunes ────────────────────────────────────────────
    try:
        log(f"  🔍 Pages Jaunes: {name_clean[:35]}")
        q = urllib.parse.quote(f"{name_clean} {city}".strip())
        html = fetch(f"https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui={q}",
                     timeout=12, referer="https://www.pagesjaunes.fr")
        validated = extract_and_validate(html, "PJ")
        if validated:
            log(f"  ✔ Trouvé via Pages Jaunes")
            return validated
    except Exception:
        pass

    # ── Source 6: Societe.com ─────────────────────────────────────────────
    try:
        log(f"  🔍 Societe.com: {name_clean[:35]}")
        q = urllib.parse.quote(name_clean)
        html = fetch(f"https://www.societe.com/cgi-bin/search?champs={q}",
                     timeout=12, referer="https://www.societe.com")
        validated = extract_and_validate(html, "Societe")
        if validated:
            log(f"  ✔ Trouvé via Societe.com")
            return validated
    except Exception:
        pass

    log(f"  ✗ Aucun email validé (6 sources épuisées)")
    return {}


def find_dealer_website(name, addr, log):
    """Find dealer's own website domain."""
    city = ""
    if addr:
        m = re.search(r"\d{5}\s+(\S+)", addr)
        if m: city = m.group(1)
    n = re.sub(r"[^\w\s]", " ", name).strip()

    for q in [f'"{n}" site officiel', f'{n} {city} site web' if city else None]:
        if not q: continue
        try:
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
            html = fetch(url, timeout=12, referer="https://duckduckgo.com")
            for href in re.findall(r'href="(https?://[^"&]{8,})"', html):
                dom = re.sub(r"https?://(?:www\.)?","",href).split("/")[0].lower().strip()
                if not dom or "." not in dom or len(dom) < 5: continue
                if any(c in dom for c in EXCL_DEFAULT): continue
                if any(p in dom for p in SKIP_DOMAINS): continue
                return dom
            time.sleep(random.uniform(0.5, 1.0))
        except Exception:
            pass
    return ""


def hunter_search(domain, excl, log):
    """Query Hunter.io for all emails on a domain."""
    if not HUNTER_KEY or not domain: return {}
    try:
        url = (f"https://api.hunter.io/v2/domain-search"
               f"?domain={urllib.parse.quote(domain)}&api_key={HUNTER_KEY}&limit=100")
        data = json.loads(fetch(url, timeout=15))
        results = {}
        for item in data.get("data", {}).get("emails", []):
            e = item.get("value","").lower()
            if not e or not is_valid_email(e): continue
            if any(x in e.split("@")[-1] for x in excl): continue
            fn  = (item.get("first_name") or "").strip()
            ln  = (item.get("last_name")  or "").strip()
            pos = (item.get("position")   or "").strip()
            person = f"{fn} {ln}".strip()
            parts = [p for p in [person, pos] if p]
            results[e] = " — ".join(parts) if parts else guess_role(e)
        if results: log(f"  ✅ [Hunter.io] {len(results)} contact(s) sur {domain}")
        return results
    except Exception as e:
        log(f"  ↳ Hunter: {str(e)[:40]}")
        return {}


def scrape_website(domain, excl, log):
    """Scrape dealer's own website for emails."""
    found = set()
    base = domain.replace("www.", "")
    for page in [f"https://{domain}", f"https://www.{domain}",
                 f"https://{domain}/contact", f"https://{domain}/nous-contacter"]:
        try:
            html = fetch(page, timeout=10, referer=f"https://{domain}")
            for e in get_emails_raw(html, excl):
                if base in e: found.add(e)
            if len(found) >= 8: break
            time.sleep(random.uniform(0.3, 0.8))
        except Exception:
            continue
    return found


def enrich_dealer(dealer, excl, log, delay=0.8, timeout=15):
    """
    Full enrichment pipeline for one dealer.
    Priority: web search → website scrape → Hunter.io
    All emails strictly validated against dealer name.
    """
    all_em = dict(dealer.get("emails", {}))
    src    = dealer.get("src", "pending")
    name   = dealer["name"]

    log(f"┌ {name}")

    # ── Step 1: Web search (Google, Maps, DDG, Bing, PJ, Societe) ─────────
    log(f"│ 1/3 Recherche web…")
    found = search_emails_for_dealer(dealer, excl, log)
    if found:
        all_em.update(found)
        src = "web"

    # ── Step 2: Dealer website ────────────────────────────────────────────
    log(f"│ 2/3 Recherche du site web…")
    domain = find_dealer_website(name, dealer["addr"], log)
    if domain:
        dealer["website"] = domain
        log(f"│  → Site: {domain}")
        scraped = scrape_website(domain, excl, log)
        for e in scraped:
            if e not in all_em:
                ok, sc, rs = email_belongs_to_dealer(e, name, dealer["addr"])
                if ok:
                    all_em[e] = guess_role(e)
                    log(f"│  ✅ [Site] {e}")
        if scraped and src == "pending": src = "web"

        # ── Step 3: Hunter.io ────────────────────────────────────────────
        log(f"│ 3/3 Hunter.io…")
        h = hunter_search(domain, excl, log)
        # Hunter emails are domain-validated (same domain = same business)
        all_em.update(h)
        if h: src = "hunter"
    else:
        log(f"│  → Site non trouvé — Hunter ignoré")

    total = len(all_em)
    icon  = "✓" if total > 0 else "✗"
    log(f"└ {icon} {total} email(s) — {src}")

    return {e: r for e, r in all_em.items() if is_valid_email(e)}, src


# ═════════════════════════════════════════════════════════════════════════════
# GUI
# ═════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang    = "FR"
        self.results = []
        self._run    = False
        self.excl    = list(EXCL_DEFAULT)
        self.delay   = tk.DoubleVar(value=0.8)
        self.timeout = tk.IntVar(value=18)
        self.retries = tk.IntVar(value=3)
        self.inc_no  = tk.BooleanVar(value=True)
        self.open_csv= tk.BooleanVar(value=False)
        self.configure(bg=C["dark"])
        self.geometry("1080x720")
        self.minsize(860, 600)
        self._build()
        self._lang()

    def L(self, k): return STRINGS[self.lang].get(k, k)

    # ── HEADER ────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["dark"], pady=0)
        hdr.pack(fill="x")

        # Red accent line
        tk.Frame(hdr, bg=C["red"], height=3).pack(fill="x")

        inner = tk.Frame(hdr, bg=C["dark"], pady=11)
        inner.pack(fill="x", padx=20)

        left = tk.Frame(inner, bg=C["dark"])
        left.pack(side="left")

        # Logo hexagon
        cv = tk.Canvas(left, width=36, height=36, bg=C["dark"], highlightthickness=0)
        cv.pack(side="left", padx=(0,10))
        cv.create_rectangle(0,0,36,36, fill=C["red"], outline="")
        cv.create_polygon([18,3,30,10,30,26,18,33,6,26,6,10], outline=C["white"], fill="", width=1.5)
        cv.create_oval(13,13,23,23, fill=C["white"], outline="")

        tk.Label(left, text="SILENCE", bg=C["dark"], fg=C["white"],
                 font=("Helvetica",17,"bold")).pack(side="left")
        tk.Label(left, text="  ECO · DEALER FINDER", bg=C["dark"], fg=C["red"],
                 font=("Helvetica",9)).pack(side="left")

        right = tk.Frame(inner, bg=C["dark"])
        right.pack(side="right")
        self._status_lbl = tk.Label(right, text="", bg=C["dark"], fg=C["muted"],
                                     font=("Helvetica",10))
        self._status_lbl.pack(side="left", padx=(0,16))
        for code in ("FR","ES","EN"):
            b = tk.Button(right, text=code, bg=C["dark2"], fg=C["white"],
                          font=("Helvetica",9,"bold"), relief="flat", width=3,
                          cursor="hand2", bd=0, pady=5, activebackground=C["red"],
                          command=lambda c=code: self._switch(c))
            b.pack(side="left", padx=1)

        self._mk_nb()

    def _mk_nb(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook", background=C["dark"], borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab", background=C["dark2"], foreground=C["muted"],
                    padding=[18,9], font=("Helvetica",11))
        s.map("TNotebook.Tab", background=[("selected",C["white"])],
              foreground=[("selected",C["red"])])
        s.configure("TFrame", background=C["white"])
        s.configure("Silence.Horizontal.TProgressbar",
                    troughcolor=C["border"], background=C["red"], thickness=4)
        s.configure("Treeview", rowheight=28, font=("Helvetica",10),
                    background=C["white"], fieldbackground=C["white"], foreground=C["dark"])
        s.configure("Treeview.Heading", font=("Helvetica",9,"bold"),
                    background=C["gray"], foreground=C["muted"])
        s.map("Treeview", background=[("selected","#FFE5E6")],
              foreground=[("selected",C["dark"])])

        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        self._f1=ttk.Frame(nb); self._f2=ttk.Frame(nb); self._f3=ttk.Frame(nb)
        nb.add(self._f1,text=""); nb.add(self._f2,text=""); nb.add(self._f3,text="")
        self._nb = nb
        self._tab1(); self._tab2(); self._tab3()

    # ── TAB 1: EXTRACTION ─────────────────────────────────────────────────
    def _tab1(self):
        f = self._f1; P = dict(padx=24, pady=5)

        # URL row
        self._lbl_url = tk.Label(f, text="", bg=C["white"], fg=C["muted"],
                                  font=("Helvetica",9,"bold"))
        self._lbl_url.pack(anchor="w", padx=24, pady=(16,3))

        row = tk.Frame(f, bg=C["white"]); row.pack(fill="x", **P)
        self._url = tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        entry = tk.Entry(row, textvariable=self._url, font=("Helvetica",11),
                 bg=C["gray"], relief="flat", bd=0,
                 highlightthickness=1.5, highlightbackground=C["border"],
                 highlightcolor=C["red"])
        entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0,10))
        self._btn = tk.Button(row, text="", bg=C["red"], fg=C["white"],
                               font=("Helvetica",11,"bold"), relief="flat",
                               cursor="hand2", bd=0, padx=20, pady=9,
                               activebackground=C["red_d"],
                               command=self._start)
        self._btn.pack(side="left")

        # Options
        opt = tk.Frame(f, bg=C["white"]); opt.pack(fill="x", **P)
        self._v1=tk.BooleanVar(value=True)
        self._v2=tk.BooleanVar(value=True)
        self._v3=tk.BooleanVar(value=True)
        self._c1=tk.Checkbutton(opt,text="",variable=self._v1,bg=C["white"],fg=C["dark"],
                                  font=("Helvetica",10),activebackground=C["white"],
                                  selectcolor=C["white"],cursor="hand2")
        self._c2=tk.Checkbutton(opt,text="",variable=self._v2,bg=C["white"],fg=C["dark"],
                                  font=("Helvetica",10),activebackground=C["white"],
                                  selectcolor=C["white"],cursor="hand2")
        self._c3=tk.Checkbutton(opt,text="",variable=self._v3,bg=C["white"],fg=C["dark"],
                                  font=("Helvetica",10),activebackground=C["white"],
                                  selectcolor=C["white"],cursor="hand2")
        self._c1.pack(side="left",padx=(0,16))
        self._c2.pack(side="left",padx=(0,16))
        self._c3.pack(side="left")

        # Status indicators
        ind = tk.Frame(f, bg=C["white"]); ind.pack(fill="x", padx=24, pady=(0,4))
        self._hunter_ind = tk.Label(ind, text="⬤ Hunter.io : actif",
                                     bg=C["white"], fg=C["green"], font=("Helvetica",9))
        self._hunter_ind.pack(side="left")

        # Banner
        banner = tk.Frame(f, bg=C["red_lt"]); banner.pack(fill="x", padx=24, pady=(0,8))
        tk.Frame(banner, bg=C["red"], width=3).pack(side="left", fill="y")
        self._desc_lbl = tk.Label(banner, text="", bg=C["red_lt"], fg="#7a0a0a",
                                   font=("Helvetica",9), justify="left")
        self._desc_lbl.pack(padx=12, pady=8, anchor="w")

        # Progress
        pf = tk.Frame(f, bg=C["white"]); pf.pack(fill="x", **P)
        self._prog_lbl = tk.Label(pf, text="", bg=C["white"], fg=C["dark"],
                                   font=("Helvetica",10,"bold"))
        self._prog_lbl.pack(anchor="w")
        self._prog_var = tk.DoubleVar()
        ttk.Progressbar(pf, variable=self._prog_var, maximum=100,
                        style="Silence.Horizontal.TProgressbar").pack(fill="x", pady=(3,0))

        # Log
        lf = tk.Frame(f, bg=C["white"]); lf.pack(fill="both", expand=True, **P)
        self._log_hdr = tk.Label(lf, text="", bg=C["white"], fg=C["muted"],
                                  font=("Helvetica",9,"bold"))
        self._log_hdr.pack(anchor="w")
        self._log = scrolledtext.ScrolledText(lf, height=7, font=("Courier New",9),
                                               bg=C["gray"], fg=C["dark"], relief="flat",
                                               bd=0, state="disabled", wrap="word",
                                               highlightthickness=0)
        self._log.pack(fill="both", expand=True, pady=(3,0))

        # Stats
        sf = tk.Frame(f, bg=C["white"]); sf.pack(fill="x", padx=24, pady=(4,16))
        self._sv={}; self._slbl={}
        for k in ("s1","s2","s3","s4"):
            c = tk.Frame(sf, bg=C["gray"], padx=16, pady=10)
            c.pack(side="left", fill="x", expand=True, padx=(0,8))
            lbl=tk.Label(c,text="",bg=C["gray"],fg=C["muted"],font=("Helvetica",9))
            lbl.pack(anchor="w")
            v=tk.StringVar(value="—"); col=C["red"] if k=="s2" else C["dark"]
            tk.Label(c,textvariable=v,bg=C["gray"],fg=col,
                     font=("Helvetica",24,"bold")).pack(anchor="w")
            self._sv[k]=v; self._slbl[k]=lbl

    # ── TAB 2: RESULTS ────────────────────────────────────────────────────
    def _tab2(self):
        f = self._f2
        top = tk.Frame(f, bg=C["white"]); top.pack(fill="x", padx=18, pady=10)
        self._meta = tk.Label(top,text="",bg=C["white"],fg=C["muted"],font=("Helvetica",10))
        self._meta.pack(side="left")
        self._btn_csv=tk.Button(top,text="",bg=C["red"],fg=C["white"],
                                 font=("Helvetica",10,"bold"),relief="flat",cursor="hand2",
                                 bd=0,padx=14,pady=5,activebackground=C["red_d"],
                                 command=self._export)
        self._btn_csv.pack(side="right")
        self._btn_copy=tk.Button(top,text="",bg=C["white"],fg=C["dark"],
                                  font=("Helvetica",10),relief="flat",bd=1,
                                  cursor="hand2",padx=10,pady=5,
                                  highlightbackground=C["border"],command=self._copy)
        self._btn_copy.pack(side="right",padx=(0,8))

        tf=tk.Frame(f,bg=C["white"]); tf.pack(fill="both",expand=True,padx=18,pady=(0,14))
        cols=("num","name","addr","phone","email","role","src")
        self._tree=ttk.Treeview(tf,columns=cols,show="headings",selectmode="browse")
        for col,w in [("num",36),("name",190),("addr",150),("phone",100),
                      ("email",185),("role",145),("src",90)]:
            self._tree.column(col,width=w,minwidth=30)
        vsb=ttk.Scrollbar(tf,orient="vertical",command=self._tree.yview)
        hsb=ttk.Scrollbar(tf,orient="horizontal",command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.pack(side="right",fill="y"); hsb.pack(side="bottom",fill="x")
        self._tree.pack(fill="both",expand=True)
        self._tree.tag_configure("miss",   background="#FFF5F5")
        self._tree.tag_configure("web",    background="#FFFBF0")
        self._tree.tag_configure("hunter", background="#F0FFF4")

    # ── TAB 3: SETTINGS ───────────────────────────────────────────────────
    def _tab3(self):
        f = self._f3
        canvas=tk.Canvas(f,bg=C["white"],highlightthickness=0)
        vsb=ttk.Scrollbar(f,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); canvas.pack(fill="both",expand=True)
        inner=tk.Frame(canvas,bg=C["white"])
        win=canvas.create_window((0,0),window=inner,anchor="nw")
        def _rsz(e): canvas.configure(scrollregion=canvas.bbox("all")); canvas.itemconfig(win,width=e.width)
        canvas.bind("<Configure>",_rsz)

        def section(title):
            fr=tk.Frame(inner,bg=C["white"]); fr.pack(fill="x",padx=24,pady=(18,0))
            tk.Label(fr,text=title,bg=C["white"],fg=C["dark"],font=("Helvetica",11,"bold")).pack(anchor="w")
            tk.Frame(fr,bg=C["border"],height=1).pack(fill="x",pady=(4,8))
            return fr

        def spinrow(parent, lbl_key, desc_key, var, frm, to, step=1):
            r=tk.Frame(parent,bg=C["white"]); r.pack(fill="x",padx=4,pady=4)
            left=tk.Frame(r,bg=C["white"]); left.pack(side="left",fill="x",expand=True)
            self._spin_labels.append(tk.Label(left,text=self.L(lbl_key),bg=C["white"],
                                               fg=C["dark"],font=("Helvetica",10)))
            self._spin_labels[-1].pack(anchor="w")
            self._spin_descs.append(tk.Label(left,text=self.L(desc_key) if desc_key else "",
                                              bg=C["white"],fg=C["muted"],font=("Helvetica",8)))
            self._spin_descs[-1].pack(anchor="w")
            sp=tk.Spinbox(r,textvariable=var,from_=frm,to=to,increment=step,
                          width=6,font=("Helvetica",10),bg=C["gray"],relief="flat",
                          bd=0,highlightthickness=1,highlightbackground=C["border"])
            sp.pack(side="right",padx=(8,0),ipady=4)

        self._spin_labels=[]; self._spin_descs=[]

        s1=section("Réseau"); spinrow(s1,"p_delay","",self.delay,0.3,10,0.1)
        spinrow(s1,"p_timeout","",self.timeout,5,60,1)
        spinrow(s1,"p_retries","",self.retries,1,6,1)

        s2=section("Filtres")
        tk.Label(s2,text=self.L("p_excl"),bg=C["white"],fg=C["dark"],
                 font=("Helvetica",10)).pack(anchor="w",padx=4)
        tk.Label(s2,text=self.L("p_excl_hint"),bg=C["white"],fg=C["muted"],
                 font=("Helvetica",8)).pack(anchor="w",padx=4,pady=(0,4))
        self._excl_txt=tk.Text(s2,height=8,font=("Courier New",9),
                                bg=C["gray"],fg=C["dark"],relief="flat",bd=0,
                                highlightthickness=1,highlightbackground=C["border"],
                                highlightcolor=C["red"])
        self._excl_txt.pack(fill="x",padx=4,pady=(0,4))
        self._excl_txt.insert("1.0","\n".join(self.excl))

        s3=section("Export")
        self._ck_no=tk.Checkbutton(s3,text=self.L("p_no_email"),variable=self.inc_no,
                                    bg=C["white"],fg=C["dark"],font=("Helvetica",10),
                                    activebackground=C["white"],selectcolor=C["white"],cursor="hand2")
        self._ck_no.pack(anchor="w",padx=4,pady=2)
        self._ck_open=tk.Checkbutton(s3,text=self.L("p_open"),variable=self.open_csv,
                                      bg=C["white"],fg=C["dark"],font=("Helvetica",10),
                                      activebackground=C["white"],selectcolor=C["white"],cursor="hand2")
        self._ck_open.pack(anchor="w",padx=4,pady=2)

        btn_row=tk.Frame(inner,bg=C["white"]); btn_row.pack(fill="x",padx=24,pady=14)
        self._btn_save=tk.Button(btn_row,text="",bg=C["red"],fg=C["white"],
                                  font=("Helvetica",10,"bold"),relief="flat",cursor="hand2",
                                  bd=0,padx=14,pady=7,activebackground=C["red_d"],
                                  command=self._save)
        self._btn_save.pack(side="left")
        self._btn_rst=tk.Button(btn_row,text="",bg=C["white"],fg=C["muted"],
                                 font=("Helvetica",10),relief="flat",bd=1,cursor="hand2",
                                 padx=10,pady=7,highlightbackground=C["border"],
                                 command=self._reset)
        self._btn_rst.pack(side="left",padx=(8,0))

    # ── LANGUAGE ──────────────────────────────────────────────────────────
    def _switch(self, lang): self.lang=lang; self._lang()

    def _lang(self):
        L=self.L; self.title(L("title"))
        self._nb.tab(0,text=L("tab_ex"))
        self._nb.tab(1,text=L("tab_re"))
        self._nb.tab(2,text=L("tab_se"))
        self._lbl_url.configure(text=L("url_lbl"))
        self._btn.configure(text=L("btn_go") if not self._run else L("btn_run"))
        self._c1.configure(text=L("opt1"))
        self._c2.configure(text=L("opt2"))
        self._c3.configure(text=L("opt3"))
        self._desc_lbl.configure(text=L("desc"))
        self._log_hdr.configure(text=L("log_hdr"))
        for k,tk_k in [("s1","st1"),("s2","st2"),("s3","st3"),("s4","st4")]:
            self._slbl[k].configure(text=L(tk_k))
        rl={"FR":"Rôle","ES":"Rol","EN":"Role"}.get(self.lang,"Rôle")
        for col,key in [("num","c_num"),("name","c_name"),("addr","c_addr"),
                        ("phone","c_phone"),("email","c_email"),("src","c_src")]:
            self._tree.heading(col,text=L(key))
        self._tree.heading("role",text=rl)
        self._btn_copy.configure(text=L("btn_copy"))
        self._btn_csv.configure(text=L("btn_csv"))
        self._btn_save.configure(text=L("btn_save"))
        self._btn_rst.configure(text=L("btn_reset"))
        self._status_lbl.configure(text=L("ready"))
        self._ck_no.configure(text=L("p_no_email"))
        self._ck_open.configure(text=L("p_open"))
        if self.results: self._render()

    # ── LOGIC ─────────────────────────────────────────────────────────────
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
        raw = self._excl_txt.get("1.0","end").strip()
        self.excl = [l.strip().lstrip("@") for l in raw.splitlines() if l.strip()]
        messagebox.showinfo("✓", self.L("saved"))

    def _reset(self):
        self.excl = list(EXCL_DEFAULT)
        self._excl_txt.delete("1.0","end"); self._excl_txt.insert("1.0","\n".join(self.excl))
        self.delay.set(0.8); self.timeout.set(18); self.retries.set(3)
        self.inc_no.set(True); self.open_csv.set(False)
        messagebox.showinfo("✓", self.L("reset"))

    def _start(self):
        if self._run: return
        url = self._url.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("", self.L("err_url")); return
        self._run = True
        self._btn.configure(state="disabled", text=self.L("btn_run"))
        self._log.configure(state="normal"); self._log.delete("1.0","end")
        self._log.configure(state="disabled")
        self._set_prog(0, "")
        for v in self._sv.values(): v.set("—")
        excl = self.excl if self._v3.get() else []
        threading.Thread(target=self._worker, args=(url,excl), daemon=True).start()

    def _worker(self, url, excl):
        try:
            to = self.timeout.get(); rt = self.retries.get(); dly = self.delay.get()

            dealers = scrape_dealer_page(url, excl, self._log_add, self._set_prog,
                                          timeout=to, retries=rt)
            self._set_prog(44, "Enrichissement emails…")

            if self._v1.get():
                pending = [d for d in dealers if not d["emails"]]
                self._log_add(f"━━━ {len(pending)} concessionnaires à enrichir ━━━")
                lock = threading.Lock()
                done = [0]

                def do_one(d):
                    try:
                        em, src = enrich_dealer(d, excl, self._log_add,
                                                 delay=dly, timeout=to)
                        if em: d["emails"]=em; d["src"]=src
                    except Exception as e:
                        self._log_add(f"  ⚠ {d['name'][:30]}: {e}")
                    finally:
                        with lock:
                            done[0] += 1
                            pct = 44 + int(50 * done[0] / max(len(pending),1))
                            self._set_prog(pct, f"{done[0]}/{len(pending)} — {d['name'][:28]}")

                # 4 parallel threads
                threads = []
                for d in pending:
                    t = threading.Thread(target=do_one, args=(d,), daemon=True)
                    threads.append(t); t.start()
                    while len([x for x in threads if x.is_alive()]) >= 4:
                        time.sleep(0.3)
                for t in threads: t.join(timeout=40)

            if self._v2.get():
                seen, uniq = set(), []
                for d in dealers:
                    k = norm(d["name"])[:20]
                    if k not in seen: seen.add(k); uniq.append(d)
                dealers = uniq

            self._set_prog(100, "Terminé !")
            total = sum(len(d["emails"]) for d in dealers)
            self._log_add(f"━━━ {len(dealers)} concessionnaires · {total} emails validés ━━━")
            self.results = dealers
            self.after(0, self._finish)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
            self._log_add(f"ERREUR: {e}")
            self.after(0, lambda: self._btn.configure(state="normal", text=self.L("btn_go")))
            self._run = False

    def _finish(self):
        self._run = False
        d = self.results
        em = sum(len(x["emails"]) for x in d)
        wb = sum(1 for x in d if x["src"] in ("web","hunter"))
        ad = sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d))); self._sv["s2"].set(str(em))
        self._sv["s3"].set(str(wb));     self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal", text=self.L("btn_again"))
        self._status_lbl.configure(text=self.L("last")+datetime.now().strftime("%H:%M"))
        self._render()
        self._nb.select(self._f2)

    def _render(self):
        d = self.results
        em=sum(len(x["emails"]) for x in d); ad=sum(1 for x in d if x["addr"])
        sm={"page":self.L("s_page"),"web":self.L("s_web"),"hunter":self.L("s_hunter")}
        self._meta.configure(
            text=f"{len(d)} {self.L('st1')} · {em} {self.L('st2')} · {ad} {self.L('st4')}")
        for r in self._tree.get_children(): self._tree.delete(r)
        n = 1
        for x in d:
            sl = sm.get(x["src"],"—")
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
                        email, role, sl if i==0 else "",
                    ))
                n += 1

    def _copy(self):
        em = sorted({e for x in self.results for e in x["emails"]})
        if not em: messagebox.showinfo("", self.L("no_copy")); return
        self.clipboard_clear(); self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓", f"{len(em)}{self.L('copied')}")

    def _export(self):
        if not self.results: messagebox.showinfo("", self.L("no_copy")); return
        desk = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desk, exist_ok=True)
        fname = f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        fpath = os.path.join(desk, fname)
        sm={"page":self.L("s_page"),"web":self.L("s_web"),"hunter":self.L("s_hunter")}
        date_s = datetime.now().strftime("%d/%m/%Y"); rows = 0
        with open(fpath,"w",newline="",encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([self.L("c_name"),self.L("c_addr"),self.L("c_phone"),
                        self.L("c_email"),self.L("c_role"),"Site web",self.L("c_src"),"Date"])
            for x in self.results:
                if not x["emails"] and not self.inc_no.get(): continue
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
        messagebox.showinfo("✓", f"{self.L('exp_ok')}\n{fname}\n\n{rows}{self.L('exp_rows')}")
        if self.open_csv.get():
            try: os.startfile(fpath)
            except Exception:
                try: os.system(f'open "{fpath}"')
                except Exception: pass


if __name__ == "__main__":
    App().mainloop()
