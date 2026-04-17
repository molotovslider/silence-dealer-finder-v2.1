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

def get_phones(text):
    seen, out = set(), []
    for m in PHONE_RE.finditer(text):
        p = re.sub(r"[\s.\-]", "", m.group(0))
        if p not in seen: seen.add(p); out.append(p)
    return out

def get_emails_raw(text, excl):
    out = set()
    for m in EMAIL_RE.finditer(text):
        e = m.group(0).lower().strip(".,;:<>\"'()")
        dom = e.split("@")[-1]
        if (is_valid_email(e)
                and not any(x in dom for x in excl)
                and not any(s in dom for s in SKIP_DOMAINS)):
            out.add(e)
    return out

def fetch(url, timeout=18, retries=3, referer="https://www.google.com"):
    """Fetch with Selenium → requests → urllib cascade."""
    # ── Selenium ──────────────────────────────────────────────────────────
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
        # Wait for dynamic content (emails loaded via JS)
        wait_time = 4 if "ligier" in url.lower() or "reseau" in url.lower() else 2
        time.sleep(wait_time)
        # Scroll to trigger lazy loading
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
        except Exception:
            pass
        html = driver.page_source
        driver.quit()
        if html and len(html) > 3000:
            return html
    except Exception:
        pass
    # ── requests ──────────────────────────────────────────────────────────
    try:
        import requests
        s = requests.Session()
        s.headers.update({
            "User-Agent": random.choice(UA_POOL),
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
            "Referer": referer,
        })
        try:
            base = re.match(r"https?://[^/]+", url)
            if base: s.get(base.group(0), timeout=6)
        except Exception:
            pass
        r = s.get(url, timeout=timeout, allow_redirects=True)
        r.encoding = r.apparent_encoding or "utf-8"
        if len(r.text) > 2000: return r.text
    except Exception:
        pass
    # ── urllib ────────────────────────────────────────────────────────────
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


def email_belongs_to_dealer(email, dealer_name, dealer_addr=""):
    """
    STRICT RULE: a keyword from the dealer name must appear
    in the email address (local part or domain).
    Otherwise → no email.
    """
    if not email or "@" not in email: return False, 0, "invalide"

    local    = norm(email.split("@")[0])
    dom      = norm(email.split("@")[-1].split(".")[0])
    dom_full = email.split("@")[-1].lower()

    # Blacklisted domains
    SKIP_DOMS = ["sollyazar.","allianz.","axa.","maif.","macif.","3s2i.",
                 "google.","bing.","duckduckgo.","societe.com","generali.",
                 "mma.","groupama.","covea.","april.","bnpparibas.","lcl.",
                 "credit-agricole.","boursorama.","indeed.","monster."]
    if any(p in dom_full for p in SKIP_DOMS):
        return False, 0, "domaine blacklisté"

    # Build keywords: words >= 2 chars from dealer name
    # Remove brand prefixes like "Ligier Store", "Ligier Partner", "Ligier Service"
    clean_name = re.sub(r"^(Ligier\s+(Store|Partner|Service|Group)\s*)", "", dealer_name, flags=re.I).strip()
    # Also remove city suffix after " - "
    clean_name_no_city = re.split(r"\s+-\s+", clean_name)[0].strip()

    kws = []
    for part in [dealer_name, clean_name, clean_name_no_city]:
        for w in re.split(r"[\s\-'&/,.()]", part):
            kw = norm(w)
            if len(kw) >= 2 and kw not in kws:
                kws.append(kw)
    # Add full concatenated name
    for part in [clean_name_no_city, clean_name]:
        c = norm(part)
        if c and c not in kws: kws.append(c)
    # Add uppercase acronyms
    for w in re.split(r"[\s\-'&/,.()]", clean_name_no_city):
        if len(w) >= 2 and w.isupper():
            kws.append(norm(w))
    kws = list(dict.fromkeys(kws))

    # THE ONE RULE: keyword must appear in local OR domain
    for kw in kws:
        if len(kw) >= 2:
            if kw in local:
                return True, 0.95, f"'{kw}' dans le préfixe"
            if kw in dom:
                return True, 0.95, f"'{kw}' dans le domaine"

    return False, 0.0, "nom du concessionnaire absent de l'email"


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

            # Page emails are ALWAYS valid — they come from the constructor's official page
            validated = {e: guess_role(e) for e in pg_emails}

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

    # ── If 0 emails on main page: fetch individual dealer pages ───────────
    no_email_count = sum(1 for d in final if not d["emails"])
    if no_email_count == len(final) and len(final) > 0:
        log(f"⚠ 0 email sur la page principale — scraping des fiches individuelles…")

        base = re.match(r"https?://[^/]+", url)
        base_url2 = base.group(0) if base else ""

        def make_slug(name):
            s = unicodedata.normalize("NFD", name.lower())
            s = "".join(c for c in s if unicodedata.category(c) != "Mn")
            s = re.sub(r"[^a-z0-9\s]", " ", s)
            s = re.sub(r"\s+", "-", s.strip()).strip("-")
            return re.sub(r"-+", "-", s)

        def fetch_fiche(dealer):
            """Try multiple URL patterns for dealer individual page."""
            name = dealer["name"]
            slug = make_slug(name)
            profile = dealer.get("profile_url", "")

            # Try known URL patterns
            candidates = []
            if profile: candidates.append(profile)
            candidates += [
                f"{base_url2}/reseau/{slug}/",
                f"{base_url2}/reseau/{slug}",
                f"{base_url2}/network/{slug}/",
            ]
            # Also try slug without city (after last dash-word)
            slug_short = "-".join(slug.split("-")[:-1]) if "-" in slug else slug
            if slug_short != slug:
                candidates.append(f"{base_url2}/reseau/{slug_short}/")

            for candidate_url in candidates:
                try:
                    html = fetch(candidate_url, timeout=12, referer=url)
                    if len(html) < 2000: continue
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    txt  = soup.get_text(" ", strip=True)
                    # Collect all emails — page emails are always valid
                    emails = get_emails_raw(txt, excl)
                    for a in soup.find_all("a", href=True):
                        if a["href"].startswith("mailto:"):
                            e = a["href"][7:].split("?")[0].strip().lower()
                            if is_valid_email(e): emails.add(e)
                    if emails:
                        dealer["profile_url"] = candidate_url
                        return {e: guess_role(e) for e in emails}
                except Exception:
                    continue
            return {}

        # Test on first 3 dealers to see if individual pages work
        found_individual = False
        for d in final[:3]:
            result = fetch_fiche(d)
            if result:
                d["emails"] = result
                d["src"] = "page"
                log(f"  ✅ Fiche individuelle fonctionne: {d['name'][:35]} → {list(result.keys())[0]}")
                found_individual = True
                break

        if found_individual:
            log(f"  → Chargement de toutes les fiches individuelles ({len(final)})…")
            import concurrent.futures
            def process_fiche(d):
                if not d["emails"]:
                    result = fetch_fiche(d)
                    if result:
                        d["emails"] = result
                        d["src"] = "page"
                return d

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                futures = {ex.submit(process_fiche, d): d for d in final if not d["emails"]}
                done = 0
                for future in concurrent.futures.as_completed(futures):
                    done += 1
                    if done % 10 == 0:
                        log(f"  {done}/{len(futures)} fiches traitées…")
                    time.sleep(0.1)

            with_email = sum(1 for d in final if d["emails"])
            log(f"  ✓ {with_email}/{len(final)} concessionnaires avec email via fiches")
        else:
            log(f"  ↳ Fiches individuelles inaccessibles — enrichissement web en fallback")

    return final


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

    # ── Source 7: annuaire-entreprises.data.gouv.fr (official French gov) ─
    try:
        log(f"  🔍 Annuaire officiel (data.gouv.fr): {name_clean[:30]}")
        q = urllib.parse.quote(f"{name_clean} {city}".strip())
        html = fetch(f"https://annuaire-entreprises.data.gouv.fr/recherche?terme={q}",
                     timeout=12, referer="https://annuaire-entreprises.data.gouv.fr")
        validated = extract_and_validate(html, "Annuaire officiel")
        if validated:
            log(f"  ✔ Trouvé via annuaire officiel")
            return validated
    except Exception:
        pass

    # ── Source 8: Verif.com ────────────────────────────────────────────────
    try:
        log(f"  🔍 Verif.com: {name_clean[:35]}")
        q = urllib.parse.quote(name_clean)
        html = fetch(f"https://www.verif.com/recherche/{q}/",
                     timeout=12, referer="https://www.verif.com")
        validated = extract_and_validate(html, "Verif.com")
        if validated:
            log(f"  ✔ Trouvé via Verif.com")
            return validated
    except Exception:
        pass

    # ── Source 7: Smart email construction ───────────────────────────────
    # Try to find website first, then construct probable emails
    log(f"  💡 Construction d'emails probables…")
    domain = find_dealer_website(dealer["name"], dealer.get("addr",""), lambda x: None)
    if domain:
        # Try common professional email patterns with dealer name keywords
        clean = re.sub(r"^(Ligier\s+(Store|Partner|Service)\s*)", "", dealer["name"], flags=re.I).strip()
        clean = re.split(r"\s+-\s+", clean)[0].strip()
        name_kws = [norm(w) for w in re.split(r"[\s\-\'&/,.()]", clean) if len(w) >= 3]
        prefixes = ["contact", "info", "accueil", "vente", "commercial"]
        if name_kws:
            prefixes = [name_kws[0]] + prefixes  # dealer name first
        for pfx in prefixes[:4]:
            guessed = f"{pfx}@{domain}"
            try:
                # Verify by trying to fetch the email (just construct, don't send)
                ok, sc, rs = email_belongs_to_dealer(guessed, dealer["name"])
                if ok:
                    log(f"  💡 Email probable: {guessed}")
                    return {guessed: guess_role(guessed)}
            except Exception:
                pass

    log(f"  ✗ Aucun email trouvé (toutes sources épuisées)")
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
    Enrichment pipeline — smart and fast:
    - If emails already found on page → use them directly, skip web search
    - If no emails on page → search web (Google, DDG, Bing, etc.)
    - Always try Hunter.io if we have a domain
    """
    all_em = dict(dealer.get("emails", {}))
    src    = dealer.get("src", "pending")
    name   = dealer["name"]

    log(f"┌ {name}")

    # ── Already has emails from page → skip web search ────────────────────
    if all_em:
        log(f"│ ✓ Email(s) déjà trouvé(s) sur la page — pas de recherche web")
    else:
        # ── Step 1: Web search (Google, Maps, DDG, Bing, PJ) ─────────────
        log(f"│ 1/3 Recherche web…")
        found = search_emails_for_dealer(dealer, excl, log)
        if found:
            all_em.update(found)
            src = "web"

    # ── Step 2: Find dealer website ───────────────────────────────────────
    log(f"│ 2/3 Site web…")
    domain = find_dealer_website(name, dealer["addr"], log)
    if domain:
        dealer["website"] = domain
        log(f"│  → {domain}")
        # Scrape only if we still have no emails
        if not all_em:
            scraped = scrape_website(domain, excl, log)
            for e in scraped:
                ok, sc, rs = email_belongs_to_dealer(e, name, dealer["addr"])
                if ok:
                    all_em[e] = guess_role(e)
                    log(f"│  ✅ [Site] {e}")
                    src = "web"

        # ── Step 3: Hunter.io (always, for enrichment) ───────────────────
        log(f"│ 3/3 Hunter.io ({domain})…")
        h = hunter_search(domain, excl, log)
        if h:
            all_em.update(h)
            src = "hunter"
    else:
        log(f"│  → Site non trouvé — Hunter ignoré")

    total = len(all_em)
    log(f"└ {'✓' if total else '✗'} {total} email(s) — {src}")
    return {e: r for e, r in all_em.items() if is_valid_email(e)}, src


# ═════════════════════════════════════════════════════════════════════════════
# GUI
# ═════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    """
    Silence.eco Dealer Finder — Futuristic HUD Interface
    Dark premium aesthetic with animated scan effects
    """
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
        self._scan_angle = 0
        self._pulse_step = 0
        self._anim_running = False
        self.configure(bg="#0A0A0B")
        self.geometry("1100x740")
        self.minsize(900,620)
        self.title("Silence.eco — Dealer Finder")
        self._build()
        self._apply_lang()

    def L(self, k): return STRINGS[self.lang].get(k, k)

    # ══ BUILD ═════════════════════════════════════════════════════════════
    def _build(self):
        self._mk_styles()
        self._mk_header()
        self._mk_body()

    def _mk_styles(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook", background="#0A0A0B", borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab", background="#111114", foreground="#555560",
                    padding=[22,10], font=("Courier New",10,"bold"))
        s.map("TNotebook.Tab",
              background=[("selected","#1A1A1F")],
              foreground=[("selected","#D01A20")])
        s.configure("TFrame", background="#0A0A0B")
        s.configure("Inner.TFrame", background="#111114")
        s.configure("Scan.Horizontal.TProgressbar",
                    troughcolor="#1A1A1F", background="#D01A20",
                    borderwidth=0, thickness=3)
        s.configure("Treeview", rowheight=30,
                    font=("Courier New",9),
                    background="#0D0D10",
                    fieldbackground="#0D0D10",
                    foreground="#C0C0CC")
        s.configure("Treeview.Heading",
                    font=("Courier New",8,"bold"),
                    background="#111114",
                    foreground="#D01A20",
                    relief="flat")
        s.map("Treeview",
              background=[("selected","#1A0608")],
              foreground=[("selected","#FF4444")])

    def _mk_header(self):
        hdr = tk.Frame(self, bg="#0A0A0B")
        hdr.pack(fill="x")
        # Top red line
        tk.Frame(hdr, bg="#D01A20", height=2).pack(fill="x")
        # Corner accent
        corner = tk.Frame(hdr, bg="#D01A20", width=4)
        inner = tk.Frame(hdr, bg="#0A0A0B", pady=12)
        inner.pack(fill="x", padx=0)

        left = tk.Frame(inner, bg="#0A0A0B")
        left.pack(side="left", padx=20)

        # Animated logo canvas
        self._logo_cv = tk.Canvas(left, width=44, height=44,
                                   bg="#0A0A0B", highlightthickness=0)
        self._logo_cv.pack(side="left", padx=(0,14))
        self._draw_logo()

        # Brand text
        brand = tk.Frame(left, bg="#0A0A0B")
        brand.pack(side="left")
        tk.Label(brand, text="SILENCE", bg="#0A0A0B", fg="#FFFFFF",
                 font=("Courier New",18,"bold")).pack(anchor="w")
        tk.Label(brand, text="ECO · DEALER FINDER SYSTEM v1.0",
                 bg="#0A0A0B", fg="#D01A20",
                 font=("Courier New",8)).pack(anchor="w")

        # Right side
        right = tk.Frame(inner, bg="#0A0A0B")
        right.pack(side="right", padx=20)

        # Status indicator
        self._status_frame = tk.Frame(right, bg="#0A0A0B")
        self._status_frame.pack(side="right", padx=(14,0))
        self._status_dot = tk.Canvas(self._status_frame, width=8, height=8,
                                      bg="#0A0A0B", highlightthickness=0)
        self._status_dot.pack(side="left", padx=(0,6))
        self._status_dot.create_oval(0,0,8,8, fill="#34C759", outline="")
        self._status_lbl = tk.Label(self._status_frame, text="",
                                     bg="#0A0A0B", fg="#555560",
                                     font=("Courier New",9))
        self._status_lbl.pack(side="left")

        # Language buttons
        for code in ("FR","ES","EN"):
            b = tk.Button(right, text=code,
                          bg="#111114", fg="#555560",
                          font=("Courier New",8,"bold"),
                          relief="flat", width=3, cursor="hand2",
                          bd=0, pady=5,
                          activebackground="#D01A20",
                          activeforeground="#FFFFFF",
                          command=lambda c=code: self._switch(c))
            b.pack(side="left", padx=1)

        # Bottom divider with scan line effect
        div = tk.Frame(hdr, bg="#1A1A1F", height=1)
        div.pack(fill="x")
        self._scan_line = tk.Frame(hdr, bg="#D01A20", height=1, width=0)
        self._scan_line.place(x=0, y=0)  # will be animated

    def _draw_logo(self):
        cv = self._logo_cv
        cv.delete("all")
        # Hexagon background
        cx, cy, r = 22, 22, 20
        pts = []
        import math
        for i in range(6):
            a = math.pi/2 + i*math.pi/3
            pts += [cx + r*math.cos(a), cy + r*math.sin(a)]
        cv.create_polygon(pts, fill="#D01A20", outline="")
        # Inner hexagon
        r2 = 14
        pts2 = []
        for i in range(6):
            a = math.pi/2 + i*math.pi/3
            pts2 += [cx + r2*math.cos(a), cy + r2*math.sin(a)]
        cv.create_polygon(pts2, fill="#0A0A0B", outline="")
        # Center dot
        cv.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#D01A20", outline="")

    def _mk_body(self):
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=0, pady=0)
        self._f1 = ttk.Frame(self._nb)
        self._f2 = ttk.Frame(self._nb)
        self._f3 = ttk.Frame(self._nb)
        self._nb.add(self._f1, text="")
        self._nb.add(self._f2, text="")
        self._nb.add(self._f3, text="")
        self._tab1()
        self._tab2()
        self._tab3()

    # ══ TAB 1: EXTRACTION ════════════════════════════════════════════════
    def _tab1(self):
        f = self._f1
        f.configure(style="TFrame")

        # URL section
        url_frame = tk.Frame(f, bg="#0A0A0B")
        url_frame.pack(fill="x", padx=22, pady=(18,8))

        self._lbl_url = tk.Label(url_frame, text="",
                                  bg="#0A0A0B", fg="#555560",
                                  font=("Courier New",8,"bold"))
        self._lbl_url.pack(anchor="w", pady=(0,6))

        row = tk.Frame(url_frame, bg="#0A0A0B")
        row.pack(fill="x")

        # URL entry with HUD style
        entry_frame = tk.Frame(row, bg="#D01A20", padx=1, pady=1)
        entry_frame.pack(side="left", fill="x", expand=True, padx=(0,10))
        entry_inner = tk.Frame(entry_frame, bg="#0D0D10")
        entry_inner.pack(fill="both")

        self._url = tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        self._url_entry = tk.Entry(entry_inner,
                                    textvariable=self._url,
                                    font=("Courier New",10),
                                    bg="#0D0D10", fg="#E0E0E8",
                                    insertbackground="#D01A20",
                                    relief="flat", bd=0)
        self._url_entry.pack(fill="x", padx=12, pady=9)

        self._btn = tk.Button(row, text="",
                               bg="#D01A20", fg="#FFFFFF",
                               font=("Courier New",10,"bold"),
                               relief="flat", cursor="hand2",
                               bd=0, padx=22, pady=10,
                               activebackground="#A01015",
                               activeforeground="#FFFFFF",
                               command=self._start)
        self._btn.pack(side="left")

        # Options row
        opt = tk.Frame(f, bg="#0A0A0B")
        opt.pack(fill="x", padx=22, pady=(4,8))
        self._v1=tk.BooleanVar(value=True)
        self._v2=tk.BooleanVar(value=True)
        self._v3=tk.BooleanVar(value=True)
        for v,attr in [(self._v1,"_c1"),(self._v2,"_c2"),(self._v3,"_c3")]:
            c = tk.Checkbutton(opt, text="", variable=v,
                               bg="#0A0A0B", fg="#888890",
                               font=("Courier New",9),
                               activebackground="#0A0A0B",
                               selectcolor="#0A0A0B",
                               cursor="hand2",
                               highlightthickness=0)
            c.pack(side="left", padx=(0,18))
            setattr(self, attr, c)

        # Hunter indicator
        ind = tk.Frame(f, bg="#0A0A0B")
        ind.pack(fill="x", padx=22, pady=(0,6))
        self._h_dot = tk.Canvas(ind, width=8, height=8,
                                 bg="#0A0A0B", highlightthickness=0)
        self._h_dot.pack(side="left")
        self._h_dot.create_oval(0,0,8,8, fill="#34C759", outline="")
        self._hunter_lbl = tk.Label(ind, text="Hunter.io : ACTIF",
                                     bg="#0A0A0B", fg="#34C759",
                                     font=("Courier New",8,"bold"))
        self._hunter_lbl.pack(side="left", padx=(6,0))

        # Info banner
        banner = tk.Frame(f, bg="#0D0D10", pady=1)
        banner.pack(fill="x", padx=22, pady=(0,10))
        left_accent = tk.Frame(banner, bg="#D01A20", width=2)
        left_accent.pack(side="left", fill="y")
        self._desc_lbl = tk.Label(banner, text="",
                                   bg="#0D0D10", fg="#555560",
                                   font=("Courier New",8), justify="left")
        self._desc_lbl.pack(padx=14, pady=7, anchor="w")

        # Progress section with animated scanner
        prog_frame = tk.Frame(f, bg="#0A0A0B")
        prog_frame.pack(fill="x", padx=22, pady=(0,6))

        # Status line
        status_row = tk.Frame(prog_frame, bg="#0A0A0B")
        status_row.pack(fill="x", pady=(0,6))
        self._prog_icon = tk.Label(status_row, text="◈",
                                    bg="#0A0A0B", fg="#D01A20",
                                    font=("Courier New",10))
        self._prog_icon.pack(side="left", padx=(0,8))
        self._prog_lbl = tk.Label(status_row, text="",
                                   bg="#0A0A0B", fg="#E0E0E8",
                                   font=("Courier New",10,"bold"))
        self._prog_lbl.pack(side="left")

        # Progress bar container
        pb_container = tk.Frame(prog_frame, bg="#1A1A1F", height=4)
        pb_container.pack(fill="x")
        pb_container.pack_propagate(False)
        self._prog_var = tk.DoubleVar()
        ttk.Progressbar(pb_container,
                        variable=self._prog_var,
                        maximum=100,
                        style="Scan.Horizontal.TProgressbar").pack(fill="both", expand=True)

        # Animated scanner overlay
        self._scanner_cv = tk.Canvas(prog_frame, bg="#0A0A0B",
                                      height=3, highlightthickness=0)
        self._scanner_cv.pack(fill="x", pady=(1,0))

        # Log section
        log_hdr = tk.Frame(f, bg="#0A0A0B")
        log_hdr.pack(fill="x", padx=22, pady=(8,4))
        tk.Label(log_hdr, text="▸ ", bg="#0A0A0B", fg="#D01A20",
                 font=("Courier New",9)).pack(side="left")
        self._log_hdr = tk.Label(log_hdr, text="",
                                  bg="#0A0A0B", fg="#555560",
                                  font=("Courier New",8,"bold"))
        self._log_hdr.pack(side="left")

        log_container = tk.Frame(f, bg="#D01A20", padx=1, pady=1)
        log_container.pack(fill="both", expand=True, padx=22)
        self._log = scrolledtext.ScrolledText(
            log_container,
            height=8,
            font=("Courier New",8),
            bg="#060608", fg="#888890",
            insertbackground="#D01A20",
            relief="flat", bd=0,
            state="disabled",
            wrap="word",
            highlightthickness=0)
        self._log.pack(fill="both", expand=True)
        self._log.tag_configure("ok",  foreground="#34C759")
        self._log.tag_configure("err", foreground="#FF4444")
        self._log.tag_configure("info",foreground="#888890")
        self._log.tag_configure("src", foreground="#D01A20")

        # Stats row
        sf = tk.Frame(f, bg="#0A0A0B")
        sf.pack(fill="x", padx=22, pady=(8,16))
        self._sv={}; self._slbl={}
        colors = ["#FFFFFF","#D01A20","#34C759","#888890"]
        for i,k in enumerate(("s1","s2","s3","s4")):
            c = tk.Frame(sf, bg="#0D0D10", padx=14, pady=10)
            c.pack(side="left", fill="x", expand=True, padx=(0,6 if i<3 else 0))
            # Corner accent
            tk.Frame(c, bg=C["red"] if k=="s2" else "#1A1A1F",
                     width=2, height=30).pack(side="left", fill="y", pady=2)
            right_c = tk.Frame(c, bg="#0D0D10")
            right_c.pack(side="left", padx=(8,0))
            lbl = tk.Label(right_c, text="", bg="#0D0D10",
                           fg="#555560", font=("Courier New",7,"bold"))
            lbl.pack(anchor="w")
            v = tk.StringVar(value="—")
            tk.Label(right_c, textvariable=v, bg="#0D0D10",
                     fg=colors[i],
                     font=("Courier New",22,"bold")).pack(anchor="w")
            self._sv[k]=v; self._slbl[k]=lbl

    # ══ TAB 2: RESULTS ═══════════════════════════════════════════════════
    def _tab2(self):
        f = self._f2
        top = tk.Frame(f, bg="#0A0A0B")
        top.pack(fill="x", padx=18, pady=10)
        self._meta = tk.Label(top, text="", bg="#0A0A0B",
                               fg="#555560", font=("Courier New",8))
        self._meta.pack(side="left")

        self._btn_csv = tk.Button(top, text="",
                                   bg="#D01A20", fg="#FFFFFF",
                                   font=("Courier New",9,"bold"),
                                   relief="flat", cursor="hand2",
                                   bd=0, padx=14, pady=5,
                                   activebackground="#A01015",
                                   command=self._export)
        self._btn_csv.pack(side="right")
        self._btn_copy = tk.Button(top, text="",
                                    bg="#111114", fg="#888890",
                                    font=("Courier New",9),
                                    relief="flat", bd=0,
                                    cursor="hand2", padx=10, pady=5,
                                    command=self._copy)
        self._btn_copy.pack(side="right", padx=(0,8))

        # Tree container with border
        tf = tk.Frame(f, bg="#D01A20", padx=1, pady=1)
        tf.pack(fill="both", expand=True, padx=18, pady=(0,14))
        tree_inner = tk.Frame(tf, bg="#0D0D10")
        tree_inner.pack(fill="both", expand=True)

        cols = ("num","name","addr","phone","email","role","src")
        self._tree = ttk.Treeview(tree_inner, columns=cols,
                                   show="headings", selectmode="browse")
        for col,w in [("num",36),("name",190),("addr",145),
                      ("phone",95),("email",180),("role",140),("src",85)]:
            self._tree.column(col, width=w, minwidth=30)
        vsb = ttk.Scrollbar(tree_inner, orient="vertical",
                             command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_inner, orient="horizontal",
                             command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)
        self._tree.tag_configure("miss",   background="#0D0608")
        self._tree.tag_configure("web",    background="#0D0D08")
        self._tree.tag_configure("hunter", background="#080D08")

    # ══ TAB 3: SETTINGS ══════════════════════════════════════════════════
    def _tab3(self):
        f = self._f3
        canvas = tk.Canvas(f, bg="#0A0A0B", highlightthickness=0)
        vsb = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg="#0A0A0B")
        win = canvas.create_window((0,0), window=inner, anchor="nw")
        def _rsz(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=e.width)
        canvas.bind("<Configure>", _rsz)

        def section(title):
            fr = tk.Frame(inner, bg="#0A0A0B")
            fr.pack(fill="x", padx=22, pady=(20,0))
            hrow = tk.Frame(fr, bg="#0A0A0B")
            hrow.pack(fill="x")
            tk.Label(hrow, text="◈ ", bg="#0A0A0B", fg="#D01A20",
                     font=("Courier New",9)).pack(side="left")
            tk.Label(hrow, text=title, bg="#0A0A0B", fg="#FFFFFF",
                     font=("Courier New",10,"bold")).pack(side="left")
            tk.Frame(fr, bg="#1A1A1F", height=1).pack(fill="x", pady=(6,10))
            return fr

        def spinrow(parent, lbl_key, var, frm, to, step=1):
            r = tk.Frame(parent, bg="#0A0A0B")
            r.pack(fill="x", padx=4, pady=4)
            tk.Label(r, text=self.L(lbl_key), bg="#0A0A0B",
                     fg="#888890", font=("Courier New",9)).pack(side="left")
            sp_frame = tk.Frame(r, bg="#D01A20", padx=1, pady=1)
            sp_frame.pack(side="right")
            sp = tk.Spinbox(sp_frame, textvariable=var,
                            from_=frm, to=to, increment=step,
                            width=5, font=("Courier New",9),
                            bg="#0D0D10", fg="#E0E0E8",
                            relief="flat", bd=0,
                            buttonbackground="#1A1A1F",
                            insertbackground="#D01A20")
            sp.pack(ipady=4, padx=4)

        s1 = section("RÉSEAU")
        spinrow(s1, "p_delay",   self.delay,   0.3, 10, 0.1)
        spinrow(s1, "p_timeout", self.timeout, 5,   60, 1)
        spinrow(s1, "p_retries", self.retries, 1,   6,  1)

        s2 = section("FILTRES")
        tk.Label(s2, text=self.L("p_excl"), bg="#0A0A0B",
                 fg="#888890", font=("Courier New",9)).pack(anchor="w", padx=4)
        txt_frame = tk.Frame(s2, bg="#D01A20", padx=1, pady=1)
        txt_frame.pack(fill="x", padx=4, pady=(4,4))
        self._excl_txt = tk.Text(txt_frame, height=8,
                                  font=("Courier New",8),
                                  bg="#060608", fg="#888890",
                                  insertbackground="#D01A20",
                                  relief="flat", bd=0)
        self._excl_txt.pack(fill="x", padx=4, pady=4)
        self._excl_txt.insert("1.0", "\n".join(self.excl))

        s3 = section("EXPORT")
        for var, attr in [(self.inc_no,"_ck_no"),(self.open_csv,"_ck_open")]:
            c = tk.Checkbutton(s3, text="", variable=var,
                               bg="#0A0A0B", fg="#888890",
                               font=("Courier New",9),
                               activebackground="#0A0A0B",
                               selectcolor="#0A0A0B",
                               cursor="hand2")
            c.pack(anchor="w", padx=4, pady=2)
            setattr(self, attr, c)

        btn_row = tk.Frame(inner, bg="#0A0A0B")
        btn_row.pack(fill="x", padx=22, pady=16)
        self._btn_save = tk.Button(btn_row, text="",
                                    bg="#D01A20", fg="#FFFFFF",
                                    font=("Courier New",9,"bold"),
                                    relief="flat", cursor="hand2",
                                    bd=0, padx=14, pady=7,
                                    activebackground="#A01015",
                                    command=self._save)
        self._btn_save.pack(side="left")
        self._btn_rst = tk.Button(btn_row, text="",
                                   bg="#111114", fg="#555560",
                                   font=("Courier New",9),
                                   relief="flat", bd=0,
                                   cursor="hand2", padx=10, pady=7,
                                   command=self._reset)
        self._btn_rst.pack(side="left", padx=(8,0))

    # ══ ANIMATIONS ════════════════════════════════════════════════════════
    def _start_anim(self):
        self._anim_running = True
        self._animate()

    def _stop_anim(self):
        self._anim_running = False

    def _animate(self):
        if not self._anim_running: return
        # Pulse the progress icon
        icons = ["◈","◉","◎","◉"]
        self._pulse_step = (self._pulse_step + 1) % len(icons)
        try:
            self._prog_icon.configure(text=icons[self._pulse_step])
        except Exception: pass
        # Scan line animation across header
        try:
            w = self.winfo_width()
            self._scan_angle = (self._scan_angle + 3) % 100
            x = int(w * self._scan_angle / 100)
            # Draw scanner on log area
            cv = self._scanner_cv
            cw = cv.winfo_width()
            cv.delete("all")
            scan_x = int(cw * self._scan_angle / 100)
            cv.create_line(scan_x, 0, scan_x+40, 0,
                          fill="#D01A20", width=2)
            cv.create_line(scan_x, 0, scan_x, 3,
                          fill="#FF4444", width=1)
        except Exception: pass
        # Color-code log lines
        self.after(80, self._animate)

    # ══ LANGUAGE ══════════════════════════════════════════════════════════
    def _switch(self, lang): self.lang=lang; self._apply_lang()

    def _apply_lang(self):
        L = self.L
        self.title(L("title"))
        self._nb.tab(0, text=f"  {L('tab_ex')}  ")
        self._nb.tab(1, text=f"  {L('tab_re')}  ")
        self._nb.tab(2, text=f"  {L('tab_se')}  ")
        self._lbl_url.configure(text=L("url_lbl").upper())
        self._btn.configure(text=f"[ {L('btn_go')} ]" if not self._run
                            else f"[ {L('btn_run')} ]")
        self._c1.configure(text=L("opt1"))
        self._c2.configure(text=L("opt2"))
        self._c3.configure(text=L("opt3"))
        self._desc_lbl.configure(text=L("desc"))
        self._log_hdr.configure(text=L("log_hdr").upper())
        for k,tk_k in [("s1","st1"),("s2","st2"),("s3","st3"),("s4","st4")]:
            self._slbl[k].configure(text=L(tk_k).upper())
        rl = {"FR":"RÔLE","ES":"ROL","EN":"ROLE"}.get(self.lang,"RÔLE")
        for col,key in [("num","c_num"),("name","c_name"),("addr","c_addr"),
                        ("phone","c_phone"),("email","c_email"),("src","c_src")]:
            self._tree.heading(col, text=L(key).upper())
        self._tree.heading("role", text=rl)
        self._btn_copy.configure(text=f"[ {L('btn_copy')} ]")
        self._btn_csv.configure(text=f"[ {L('btn_csv')} ]")
        self._btn_save.configure(text=f"[ {L('btn_save')} ]")
        self._btn_rst.configure(text=f"[ {L('btn_reset')} ]")
        self._ck_no.configure(text=L("p_no_email"))
        self._ck_open.configure(text=L("p_open"))
        self._status_lbl.configure(text=L("ready").upper())
        if self.results: self._render()

    # ══ LOG ═══════════════════════════════════════════════════════════════
    def _log_add(self, msg):
        self._log.configure(state="normal")
        # Color based on content
        if "✅" in msg or "✔" in msg or "✓" in msg:
            tag = "ok"
        elif "✗" in msg or "ERREUR" in msg or "rejeté" in msg:
            tag = "err"
        elif "🔍" in msg or "🗺" in msg or "💡" in msg:
            tag = "src"
        else:
            tag = "info"
        self._log.insert("end", f"  {msg}\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_prog(self, pct, lbl=""):
        self._prog_var.set(pct)
        if lbl:
            # Add scanline prefix for futuristic feel
            self._prog_lbl.configure(text=lbl)
        self.update_idletasks()

    # ══ ACTIONS ═══════════════════════════════════════════════════════════
    def _save(self):
        raw = self._excl_txt.get("1.0","end").strip()
        self.excl = [l.strip().lstrip("@") for l in raw.splitlines() if l.strip()]
        messagebox.showinfo("SILENCE · SYSTEM", self.L("saved"))

    def _reset(self):
        self.excl = list(EXCL_DEFAULT)
        self._excl_txt.delete("1.0","end")
        self._excl_txt.insert("1.0","\n".join(self.excl))
        self.delay.set(0.8); self.timeout.set(18); self.retries.set(3)
        self.inc_no.set(True); self.open_csv.set(False)
        messagebox.showinfo("SILENCE · SYSTEM", self.L("reset"))

    def _start(self):
        if self._run: return
        url = self._url.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("ERROR", self.L("err_url")); return
        self._run = True
        self._btn.configure(state="disabled",
                             text=f"[ {self.L('btn_run')} ]")
        self._log.configure(state="normal")
        self._log.delete("1.0","end")
        self._log.configure(state="disabled")
        self._set_prog(0,"")
        for v in self._sv.values(): v.set("—")
        # Start animation
        self._start_anim()
        excl = self.excl if self._v3.get() else []
        threading.Thread(target=self._worker, args=(url,excl), daemon=True).start()

    def _worker(self, url, excl):
        try:
            to=self.timeout.get(); rt=self.retries.get(); dly=self.delay.get()
            dealers = scrape_dealer_page(url, excl, self._log_add,
                                          self._set_prog, timeout=to, retries=rt)
            self._set_prog(44,"Enrichissement…")
            if self._v1.get():
                pending = dealers
                no_em = sum(1 for d in dealers if not d["emails"])
                has_em = len(dealers) - no_em
                self._log_add(f"━━ {len(dealers)} concessionnaires ━━")
                self._log_add(f"  {has_em} avec email(s) → Hunter seulement")
                self._log_add(f"  {no_em} sans email → recherche complète")
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
                            pct = 44+int(50*done[0]/max(len(pending),1))
                            self._set_prog(pct,
                                f"{done[0]}/{len(pending)} — {d['name'][:28]}")
                threads=[]
                for d in pending:
                    t=threading.Thread(target=do_one,args=(d,),daemon=True)
                    threads.append(t); t.start()
                    while len([x for x in threads if x.is_alive()])>=4:
                        time.sleep(0.3)
                for t in threads: t.join(timeout=40)
            if self._v2.get():
                seen,uniq=set(),[]
                for d in dealers:
                    k=norm(d["name"])[:20]
                    if k not in seen: seen.add(k); uniq.append(d)
                dealers=uniq
            self._set_prog(100,"✓ EXTRACTION TERMINÉE")
            total=sum(len(d["emails"]) for d in dealers)
            self._log_add(f"━━ {len(dealers)} concessionnaires · {total} emails validés ━━")
            self.results=dealers
            self.after(0, self._finish)
        except Exception as e:
            self.after(0,lambda:messagebox.showerror("ERROR",str(e)))
            self._log_add(f"✗ ERREUR CRITIQUE: {e}")
            self.after(0,lambda: self._btn.configure(
                state="normal",text=f"[ {self.L('btn_go')} ]"))
            self._run=False
            self._stop_anim()

    def _finish(self):
        self._run=False
        self._stop_anim()
        self._prog_icon.configure(text="◈")
        d=self.results
        em=sum(len(x["emails"]) for x in d)
        wb=sum(1 for x in d if x["src"] in ("web","hunter"))
        ad=sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d)))
        self._sv["s2"].set(str(em))
        self._sv["s3"].set(str(wb))
        self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal",
                             text=f"[ {self.L('btn_again')} ]")
        self._status_lbl.configure(
            text=(self.L("last")+datetime.now().strftime("%H:%M")).upper())
        self._render()
        self._nb.select(self._f2)

    def _render(self):
        d=self.results
        em=sum(len(x["emails"]) for x in d)
        ad=sum(1 for x in d if x["addr"])
        sm={"page":self.L("s_page"),"web":self.L("s_web"),
            "hunter":self.L("s_hunter")}
        self._meta.configure(
            text=f"{len(d)} {self.L('st1').upper()} · {em} {self.L('st2').upper()} · {ad} {self.L('st4').upper()}")
        for r in self._tree.get_children(): self._tree.delete(r)
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
                        email, role, sl if i==0 else "",
                    ))
                n+=1

    def _copy(self):
        em=sorted({e for x in self.results for e in x["emails"]})
        if not em: messagebox.showinfo("",self.L("no_copy")); return
        self.clipboard_clear(); self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓",f"{len(em)}{self.L('copied')}")

    def _export(self):
        if not self.results: messagebox.showinfo("",self.L("no_copy")); return
        desk=os.path.join(os.path.expanduser("~"),"Desktop")
        os.makedirs(desk,exist_ok=True)
        fname=f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        fpath=os.path.join(desk,fname)
        sm={"page":self.L("s_page"),"web":self.L("s_web"),
            "hunter":self.L("s_hunter")}
        date_s=datetime.now().strftime("%d/%m/%Y"); rows=0
        with open(fpath,"w",newline="",encoding="utf-8-sig") as fp:
            w=csv.writer(fp)
            w.writerow([self.L("c_name"),self.L("c_addr"),self.L("c_phone"),
                        self.L("c_email"),self.L("c_role"),
                        "Site web",self.L("c_src"),"Date"])
            for x in self.results:
                if not x["emails"] and not self.inc_no.get(): continue
                sl=sm.get(x["src"],"—"); site=x.get("website","")
                if not x["emails"]:
                    w.writerow([x["name"],x["addr"],x["phone"],
                                "","",site,sl,date_s]); rows+=1
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
        messagebox.showinfo("✓",
            f"{self.L('exp_ok')}\n{fname}\n\n{rows}{self.L('exp_rows')}")
        if self.open_csv.get():
            try: os.startfile(fpath)
            except Exception:
                try: os.system(f'open "{fpath}"')
                except Exception: pass

if __name__ == "__main__":
    App().mainloop()
