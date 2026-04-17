#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading, re, time, os, csv, urllib.request, urllib.parse
from datetime import datetime

# ── Couleurs Silence ──────────────────────────────────────────────
RED    = "#D01A20"
RED_D  = "#A01015"
RED_LT = "#FAE8E8"
DARK   = "#1C1C1E"
GRAY   = "#F2F2F2"
WHITE  = "#FFFFFF"
MUTED  = "#8A8A8E"
BORDER = "#E0E0E0"

# ── Traductions ───────────────────────────────────────────────────
T = {
"FR": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extraction  ", tab2="  Résultats  ", tab3="  Paramètres  ",
    url_label="URL de la page réseau concessionnaires :",
    btn_go="  Extraire  ", btn_running="  En cours…  ", btn_again="  Relancer  ",
    opt1="Recherche web pour emails manquants",
    opt2="Dédupliquer les résultats",
    opt3="Exclure emails du constructeur",
    info="L'outil analyse la page, extrait nom / adresse / téléphone / email\nde chaque concessionnaire, puis complète les données manquantes\nvia une recherche web ciblée.",
    log_title="Journal :",
    col_num="#", col_name="Nom", col_addr="Adresse", col_phone="Téléphone",
    col_email="Email", col_src="Source",
    src_page="Page", src_web="Web", src_miss="—",
    stat1="Concessionnaires", stat2="Emails trouvés", stat3="Via web", stat4="Adresses",
    btn_copy="Copier les emails", btn_csv="Exporter CSV",
    no_results="Aucun résultat — lancez une extraction",
    set_title="Domaines constructeurs à exclure :",
    set_desc="(un par ligne — ces emails seront ignorés)",
    btn_save="  Enregistrer  ",
    info2="Application locale — aucune donnée envoyée à l'extérieur.",
    copied="emails copiés !",
    no_copy="Aucun email à copier.",
    saved="Paramètres enregistrés !",
    err_url="URL invalide (doit commencer par http)",
    export_ok="CSV sauvegardé sur le Bureau :",
    ready="Prêt", last="Dernier run : ",
),
"ES": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extracción  ", tab2="  Resultados  ", tab3="  Ajustes  ",
    url_label="URL de la página red de concesionarios:",
    btn_go="  Extraer  ", btn_running="  En proceso…  ", btn_again="  Reiniciar  ",
    opt1="Búsqueda web para emails faltantes",
    opt2="Eliminar duplicados",
    opt3="Excluir emails del fabricante",
    info="La herramienta analiza la página, extrae nombre / dirección / teléfono / email\nde cada concesionario, y completa los datos faltantes\nmediante búsqueda web.",
    log_title="Registro:",
    col_num="#", col_name="Nombre", col_addr="Dirección", col_phone="Teléfono",
    col_email="Email", col_src="Fuente",
    src_page="Página", src_web="Web", src_miss="—",
    stat1="Concesionarios", stat2="Emails encontrados", stat3="Vía web", stat4="Direcciones",
    btn_copy="Copiar emails", btn_csv="Exportar CSV",
    no_results="Sin resultados — lance una extracción",
    set_title="Dominios del fabricante a excluir:",
    set_desc="(uno por línea — estos emails serán ignorados)",
    btn_save="  Guardar  ",
    info2="Aplicación local — ningún dato enviado al exterior.",
    copied="emails copiados!",
    no_copy="No hay emails para copiar.",
    saved="¡Ajustes guardados!",
    err_url="URL inválida (debe comenzar por http)",
    export_ok="CSV guardado en el Escritorio:",
    ready="Listo", last="Última extracción: ",
),
"EN": dict(
    title="Silence.eco — Dealer Finder",
    tab1="  Extraction  ", tab2="  Results  ", tab3="  Settings  ",
    url_label="Dealer network page URL:",
    btn_go="  Extract  ", btn_running="  Running…  ", btn_again="  Run Again  ",
    opt1="Web search for missing emails",
    opt2="Deduplicate results",
    opt3="Exclude manufacturer emails",
    info="The tool scans the page, extracts name / address / phone / email\nfor each dealer, then fills missing data\nvia targeted web searches.",
    log_title="Log:",
    col_num="#", col_name="Name", col_addr="Address", col_phone="Phone",
    col_email="Email", col_src="Source",
    src_page="Page", src_web="Web", src_miss="—",
    stat1="Dealers", stat2="Emails found", stat3="Via web", stat4="Addresses",
    btn_copy="Copy emails", btn_csv="Export CSV",
    no_results="No results — run an extraction first",
    set_title="Manufacturer domains to exclude:",
    set_desc="(one per line — these emails will be ignored)",
    btn_save="  Save  ",
    info2="Local app — no data sent externally.",
    copied="emails copied!",
    no_copy="No emails to copy.",
    saved="Settings saved!",
    err_url="Invalid URL (must start with http)",
    export_ok="CSV saved to Desktop:",
    ready="Ready", last="Last run: ",
),
}

EXCL_DEFAULT = ["silence.eco","aixam.com","microcar.fr","ligier.fr",
                 "chatenet.com","casalini.it","bellier.fr","grecav.com"]
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
ADDR_RE  = re.compile(r"\d{1,4}[\s,]+[^\d\n]{5,50}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,30}", re.I)
HDRS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Language":"fr-FR,fr;q=0.9","Accept":"text/html,*/*;q=0.8"}

def fetch(url, timeout=14):
    r = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        enc = resp.headers.get_content_charset("utf-8") or "utf-8"
        return raw.decode(enc, errors="replace")

# ── Email validation ───────────────────────────────────────────────────────
FAKE_DOMAINS = [
    "duckduckgo.com","example.com","test.com","domain.com","email.com",
    "mail.com","noreply.com","sentry.io","w3.org","schema.org","google.com",
    "placeholder.com","cloudflare.com","jquery.com","facebook.com","twitter.com",
    "instagram.com","youtube.com","microsoft.com","apple.com","amazon.com",
    "wixpress.com","squarespace.com","wordpress.com","shopify.com",
]
ROLE_KEYWORDS = {
    "contact","info","commercial","vente","ventes","sales","marketing",
    "direction","directeur","manager","comptabilite","comptable","accounting",
    "accueil","reception","secretariat","administration","admin","rh","hr",
    "patron","gerant","pdg","ceo","apv","service","atelier","technique",
}

def is_real_email(e):
    if not e or len(e) < 7: return False
    local, dom = e.split("@")[0], e.split("@")[-1].lower()
    if any(f in dom for f in FAKE_DOMAINS): return False
    if len(dom.split(".")[0]) < 2: return False
    if re.search(r"\.(png|jpg|gif|css|js|svg|ico|woff)$", dom): return False
    return True

def guess_role(email):
    """Return a human-readable role label based on email prefix."""
    local = email.split("@")[0].lower().replace(".", "").replace("-", "").replace("_", "")
    role_map = [
        (["direction","directeur","directrice","pdg","ceo","gerant","patron","dg"], "Direction"),
        (["commercial","vente","ventes","sales","vendeur","vendeuse"],              "Commercial"),
        (["marketing","communication","comm","promo"],                              "Marketing"),
        (["comptabilite","comptable","compta","facturation","accounting"],          "Comptabilité"),
        (["contact","info","information","hello","bonjour","accueil","reception"],  "Contact général"),
        (["apv","atelier","technique","sav","service","reparation"],               "Après-vente"),
        (["rh","hr","recrutement","emploi","jobs"],                                 "RH"),
        (["secretariat","admin","administration","assistante","assistant"],         "Administration"),
    ]
    for keywords, label in role_map:
        if any(k in local for k in keywords):
            return label
    return "Équipe"

def get_emails(text, excl):
    out = set()
    for m in EMAIL_RE.finditer(text):
        e = m.group(0).lower().strip(".,;:")
        dom = e.split("@")[-1]
        if not any(x in dom for x in excl) and is_real_email(e):
            out.add(e)
    return out

def get_phones(text):
    seen, out = set(), []
    for m in PHONE_RE.finditer(text):
        p = re.sub(r"[\s\.\-]","",m.group(0))
        if p not in seen: seen.add(p); out.append(p)
    return out

# ── Multi-source web search — returns ALL emails found ─────────────────────
def web_search_all_emails(dealer_name, dealer_addr, excl, log):
    """
    Search multiple sources for ALL emails related to this dealer.
    Returns a set of validated emails.
    """
    found = set()
    city = ""
    if dealer_addr:
        m = re.search(r"\d{5}\s+([A-ZÀ-Ÿa-zà-ÿ\s\-]+)", dealer_addr)
        if m: city = m.group(1).strip().split()[0]

    queries = [
        f'"{dealer_name}" email',
        f'"{dealer_name}" {city} contact email' if city else None,
        f'"{dealer_name}" concessionnaire mail',
        f'{dealer_name} {city} site:societe.com OR site:pages-jaunes.fr' if city else None,
    ]
    queries = [q for q in queries if q]

    for q in queries:
        try:
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
            html = fetch(url, timeout=10)
            # Extract only from result snippets and links, not page UI
            clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
            clean = re.sub(r"<[^>]+>", " ", clean)
            emails = get_emails(clean, excl)
            found.update(emails)
            if found:
                break  # stop as soon as we find something
            time.sleep(0.8)
        except Exception as e:
            log(f"  search erreur ({q[:30]}): {e}")
            continue

    # Try to also fetch the dealer website if an email was found
    if found:
        try:
            domain = list(found)[0].split("@")[-1]
            site_html = fetch(f"https://{domain}", timeout=8)
            more = get_emails(site_html, excl)
            # Only keep emails from same domain
            more = {e for e in more if domain in e}
            found.update(more)
        except Exception:
            pass

    return {e for e in found if is_real_email(e)}

# ── Page scraper ────────────────────────────────────────────────────────────
def scrape(url, excl, log, send_progress):
    send_progress(5, "Chargement de la page…")
    log(f"GET {url}")
    html = fetch(url)
    log(f"Page reçue — {len(html)//1024} Ko")

    send_progress(20, "Analyse des blocs…")
    dealers = []

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script","style","nav","footer","head"]): t.decompose()

        # ── Strategy 1: try specific dealer-block selectors ──────────────
        blocks = []
        best_count = 0
        for sel in [
            "[class*='dealer']","[class*='concess']","[class*='revendeur']",
            "[class*='reseau']","[class*='network']","[class*='store']",
            "[class*='location']","[class*='point-vente']","[class*='retailer']",
            "[class*='agency']","[class*='agence']","[class*='partner']",
            "article","li.item","li.dealer","li.concessionnaire",
            ".card",".box","[class*='item']","[class*='entry']",
        ]:
            found = soup.select(sel)
            # Pick the selector that finds the MOST blocks (not just first ≥3)
            if len(found) > best_count:
                best_count = len(found)
                blocks = found
                log(f"Sélecteur '{sel}' → {len(found)} blocs")

        # ── Strategy 2: group by repeated phone pattern ───────────────────
        if best_count < 5:
            phone_blocks = [d for d in soup.find_all(["div","li","article","section"])
                            if PHONE_RE.search(d.get_text())]
            if len(phone_blocks) > best_count:
                blocks = phone_blocks
                log(f"Fallback téléphone → {len(blocks)} blocs")

        # ── Strategy 3: find the deepest list/grid containing all dealers ─
        if best_count < 5:
            for tag in soup.find_all(["ul","ol","div"]):
                children = tag.find_all(["li","div","article"], recursive=False)
                if len(children) > best_count and all(
                    PHONE_RE.search(c.get_text()) or EMAIL_RE.search(c.get_text())
                    for c in children[:3]
                ):
                    blocks = children
                    best_count = len(children)
                    log(f"Grille détectée → {len(blocks)} blocs")

        log(f"Total: {len(blocks)} blocs à analyser (sans limite)")

        # ── Parse ALL blocks — NO [:100] limit ───────────────────────────
        seen = set()
        for blk in blocks:   # <-- NO LIMIT
            txt = blk.get_text(" ", strip=True)
            if len(txt) < 10: continue

            # Extract name from heading tags first, then fallback
            name = ""
            for t in blk.find_all(["h1","h2","h3","h4","h5","strong","b","span"]):
                v = t.get_text(strip=True)
                # Must look like a business name, not a phone/address
                if 3 < len(v) < 90 and not PHONE_RE.match(v) and not v.isdigit():
                    name = v; break
            if not name:
                # Take first meaningful line
                for line in txt.split("  "):
                    line = line.strip()
                    if 3 < len(line) < 90 and not PHONE_RE.match(line):
                        name = line; break
            if not name: continue

            # Skip phone-only rows
            if re.match(r"^(t[eé]l\.?\s*:?\s*)[\d\s.\-\+]{6,}$", name.strip(), re.I): continue
            # Skip rows that are just an address number
            if re.match(r"^\d[\d\s,\-]+$", name.strip()): continue

            key = name.lower()[:30]
            if key in seen or len(name) < 3: continue
            seen.add(key)

            am = ADDR_RE.search(txt)
            addr = am.group(0).strip()[:100] if am else ""

            phones = get_phones(txt)
            phone = phones[0] if phones else ""

            # Collect ALL emails from block (visible text + mailto links)
            page_emails = get_emails(txt, excl)
            for a in blk.find_all("a", href=True):
                h = a["href"]
                if h.startswith("mailto:"):
                    e = h[7:].split("?")[0].strip().lower()
                    if is_real_email(e) and not any(x in e.split("@")[-1] for x in excl):
                        page_emails.add(e)

            emails_with_roles = {e: guess_role(e) for e in page_emails}
            src = "page" if page_emails else "pending"
            dealers.append({
                "name": name[:80], "addr": addr, "phone": phone,
                "emails": emails_with_roles,
                "src": src,
            })

    except ImportError:
        log("bs4 non disponible — mode regex")
        clean = re.sub(r"<[^>]+>"," ",html)
        clean = re.sub(r"\s+"," ",clean)
        phones = get_phones(clean)
        used = set()
        for ph in phones:  # NO LIMIT
            idx = clean.find(re.sub(r"[\s\.\-]","",ph)[:6])
            if idx < 0: continue
            ctx = clean[max(0,idx-200):idx+200]
            em_l = [e for e in get_emails(ctx,excl) if e not in used]
            for em in em_l: used.add(em)
            nm = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿa-zà-ÿ\-]+){1,4})", ctx)
            name = nm.group(1) if nm else f"Dealer {len(dealers)+1}"
            # Skip duplicates
            key = name.lower()[:25]
            if key in {d["name"].lower()[:25] for d in dealers}: continue
            dealers.append({
                "name": name[:80], "addr": "", "phone": ph,
                "emails": {em: guess_role(em) for em in em_l},
                "src": "page" if em_l else "pending",
            })

    # Final dedup by name similarity
    final, seen_keys = [], set()
    for d in dealers:
        k = re.sub(r"[^a-z0-9]", "", d["name"].lower())[:20]
        if k and k not in seen_keys:
            seen_keys.add(k)
            final.append(d)

    log(f"{len(final)} concessionnaires uniques trouvés en page")
    return final


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "FR"
        self.results = []
        self.excl = list(EXCL_DEFAULT)
        self._running = False
        self.configure(bg=DARK)
        self.geometry("980x680")
        self.minsize(800,580)
        self._build()
        self._apply_lang()

    def L(self, key):
        return T[self.lang].get(key, key)

    def _build(self):
        # ── HEADER ────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=DARK, pady=10)
        hdr.pack(fill="x", padx=0)

        left = tk.Frame(hdr, bg=DARK)
        left.pack(side="left", padx=20)

        # Logo mark
        canvas = tk.Canvas(left, width=34, height=34, bg=DARK, highlightthickness=0)
        canvas.pack(side="left")
        canvas.create_rectangle(0,0,34,34, fill=RED, outline="", tags="logo_bg")
        pts = [17,4, 28,10, 28,24, 17,30, 6,24, 6,10]
        canvas.create_polygon(pts, outline=WHITE, fill="", width=2)
        canvas.create_oval(12,12,22,22, fill=WHITE, outline="")

        tk.Label(left, text="  SILENCE", bg=DARK, fg=WHITE,
                 font=("Helvetica",16,"bold")).pack(side="left")
        tk.Label(left, text=" ECO · DEALER FINDER", bg=DARK, fg=RED,
                 font=("Helvetica",9)).pack(side="left")

        # Right side
        right = tk.Frame(hdr, bg=DARK)
        right.pack(side="right", padx=20)
        self._lbl_status = tk.Label(right, text="", bg=DARK, fg=MUTED,
                                     font=("Helvetica",10))
        self._lbl_status.pack(side="left", padx=(0,16))

        for code in ("FR","ES","EN"):
            b = tk.Button(right, text=code, bg="#2C2C2E", fg=WHITE,
                          font=("Helvetica",9,"bold"), relief="flat",
                          width=3, cursor="hand2", bd=0, pady=4,
                          command=lambda c=code: self._switch(c))
            b.pack(side="left", padx=2)

        # ── NOTEBOOK ──────────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=DARK, borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab", background="#2C2C2E", foreground=MUTED,
                        padding=[16,9], font=("Helvetica",11))
        style.map("TNotebook.Tab",
                  background=[("selected",WHITE)],
                  foreground=[("selected",RED)])
        style.configure("TFrame", background=WHITE)
        style.configure("Red.Horizontal.TProgressbar",
                        troughcolor=BORDER, background=RED, thickness=5)
        style.configure("Treeview", rowheight=26, font=("Helvetica",10),
                        background=WHITE, fieldbackground=WHITE, foreground=DARK)
        style.configure("Treeview.Heading", font=("Helvetica",9,"bold"),
                        background=GRAY, foreground=MUTED)
        style.map("Treeview", background=[("selected",RED_LT)],
                  foreground=[("selected",DARK)])

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True)

        self._f1 = ttk.Frame(self._nb)
        self._f2 = ttk.Frame(self._nb)
        self._f3 = ttk.Frame(self._nb)
        self._nb.add(self._f1, text="")
        self._nb.add(self._f2, text="")
        self._nb.add(self._f3, text="")

        self._build_tab1()
        self._build_tab2()
        self._build_tab3()

    # ── TAB 1 : EXTRACTION ────────────────────────────────────────
    def _build_tab1(self):
        f = self._f1
        P = dict(padx=22, pady=6)

        self._lbl_url = tk.Label(f, text="", bg=WHITE, fg=MUTED,
                                  font=("Helvetica",9,"bold"))
        self._lbl_url.pack(anchor="w", padx=22, pady=(16,3))

        row = tk.Frame(f, bg=WHITE)
        row.pack(fill="x", **P)
        self._url_var = tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        tk.Entry(row, textvariable=self._url_var, font=("Helvetica",11),
                 bg=GRAY, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=RED).pack(side="left", fill="x", expand=True, ipady=8, padx=(0,8))
        self._btn = tk.Button(row, text="", bg=RED, fg=WHITE,
                               font=("Helvetica",11,"bold"), relief="flat",
                               cursor="hand2", bd=0, padx=16, pady=8,
                               command=self._start)
        self._btn.pack(side="left")

        opt_frame = tk.Frame(f, bg=WHITE)
        opt_frame.pack(fill="x", **P)
        self._v1 = tk.BooleanVar(value=True)
        self._v2 = tk.BooleanVar(value=True)
        self._v3 = tk.BooleanVar(value=True)
        self._chk1 = tk.Checkbutton(opt_frame, text="", variable=self._v1,
                                     bg=WHITE, fg=DARK, font=("Helvetica",10),
                                     activebackground=WHITE, selectcolor=WHITE, cursor="hand2")
        self._chk2 = tk.Checkbutton(opt_frame, text="", variable=self._v2,
                                     bg=WHITE, fg=DARK, font=("Helvetica",10),
                                     activebackground=WHITE, selectcolor=WHITE, cursor="hand2")
        self._chk3 = tk.Checkbutton(opt_frame, text="", variable=self._v3,
                                     bg=WHITE, fg=DARK, font=("Helvetica",10),
                                     activebackground=WHITE, selectcolor=WHITE, cursor="hand2")
        self._chk1.pack(side="left", padx=(0,14))
        self._chk2.pack(side="left", padx=(0,14))
        self._chk3.pack(side="left")

        # Banner
        self._banner_frame = tk.Frame(f, bg=RED_LT)
        self._banner_frame.pack(fill="x", padx=22, pady=(4,8))
        tk.Frame(self._banner_frame, bg=RED, width=3).pack(side="left", fill="y")
        self._banner_lbl = tk.Label(self._banner_frame, text="", bg=RED_LT, fg="#7a0a0a",
                                     font=("Helvetica",9), justify="left")
        self._banner_lbl.pack(padx=10, pady=8, anchor="w")

        # Progress
        pf = tk.Frame(f, bg=WHITE)
        pf.pack(fill="x", **P)
        self._prog_lbl = tk.Label(pf, text="", bg=WHITE, fg=DARK,
                                   font=("Helvetica",10,"bold"))
        self._prog_lbl.pack(anchor="w")
        self._prog_var = tk.DoubleVar()
        ttk.Progressbar(pf, variable=self._prog_var, maximum=100,
                        style="Red.Horizontal.TProgressbar").pack(fill="x", pady=(4,0))

        # Log
        lf = tk.Frame(f, bg=WHITE)
        lf.pack(fill="both", expand=True, **P)
        self._log_lbl = tk.Label(lf, text="", bg=WHITE, fg=MUTED,
                                  font=("Helvetica",9,"bold"))
        self._log_lbl.pack(anchor="w")
        self._log = scrolledtext.ScrolledText(lf, height=6, font=("Courier",9),
                                               bg=GRAY, fg=DARK, relief="flat", bd=0,
                                               state="disabled", wrap="word",
                                               highlightthickness=0)
        self._log.pack(fill="both", expand=True, pady=(3,0))

        # Stats
        sf = tk.Frame(f, bg=WHITE)
        sf.pack(fill="x", padx=22, pady=(4,16))
        self._sv = {}
        self._slbl = {}
        for k in ("s1","s2","s3","s4"):
            c = tk.Frame(sf, bg=GRAY, padx=14, pady=10)
            c.pack(side="left", fill="x", expand=True, padx=(0,8))
            lbl = tk.Label(c, text="", bg=GRAY, fg=MUTED, font=("Helvetica",9))
            lbl.pack(anchor="w")
            v = tk.StringVar(value="—")
            col = RED if k=="s2" else DARK
            tk.Label(c, textvariable=v, bg=GRAY, fg=col,
                     font=("Helvetica",22,"bold")).pack(anchor="w")
            self._sv[k] = v
            self._slbl[k] = lbl

    # ── TAB 2 : RESULTS ───────────────────────────────────────────
    def _build_tab2(self):
        f = self._f2

        top = tk.Frame(f, bg=WHITE)
        top.pack(fill="x", padx=16, pady=10)
        self._meta_lbl = tk.Label(top, text="", bg=WHITE, fg=MUTED,
                                   font=("Helvetica",10))
        self._meta_lbl.pack(side="left")

        self._btn_csv = tk.Button(top, text="", bg=RED, fg=WHITE,
                                   font=("Helvetica",10,"bold"), relief="flat",
                                   cursor="hand2", bd=0, padx=12, pady=5,
                                   command=self._export_csv)
        self._btn_csv.pack(side="right")
        self._btn_copy = tk.Button(top, text="", bg=WHITE, fg=DARK,
                                    font=("Helvetica",10), relief="flat", bd=1,
                                    cursor="hand2", padx=10, pady=5,
                                    highlightbackground=BORDER,
                                    command=self._copy_emails)
        self._btn_copy.pack(side="right", padx=(0,8))

        tf = tk.Frame(f, bg=WHITE)
        tf.pack(fill="both", expand=True, padx=16, pady=(0,14))
        self._tree = ttk.Treeview(tf,
            columns=("num","name","addr","phone","email","src","role"),
            show="headings", selectmode="browse")
        for col,w in [("num",36),("name",200),("addr",160),
                      ("phone",105),("email",185),("src",80),("role",110)]:
            self._tree.column(col, width=w, minwidth=30)
        vsb = ttk.Scrollbar(tf, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)
        self._tree.tag_configure("miss", background="#FFF5F5")
        self._tree.tag_configure("web",  background="#FFFBF0")

    # ── TAB 3 : SETTINGS ──────────────────────────────────────────
    def _build_tab3(self):
        f = self._f3
        P = dict(padx=22, pady=8)
        self._set_title = tk.Label(f, text="", bg=WHITE, fg=DARK,
                                    font=("Helvetica",11,"bold"))
        self._set_title.pack(anchor="w", padx=22, pady=(16,2))
        self._set_desc = tk.Label(f, text="", bg=WHITE, fg=MUTED,
                                   font=("Helvetica",9))
        self._set_desc.pack(anchor="w", padx=22)
        self._excl_txt = tk.Text(f, height=10, font=("Courier",10),
                                  bg=GRAY, fg=DARK, relief="flat", bd=0,
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=RED)
        self._excl_txt.pack(fill="x", **P)
        self._excl_txt.insert("1.0", "\n".join(self.excl))

        self._btn_save = tk.Button(f, text="", bg=RED, fg=WHITE,
                                    font=("Helvetica",10,"bold"), relief="flat",
                                    cursor="hand2", bd=0, padx=14, pady=7,
                                    command=self._save)
        self._btn_save.pack(anchor="w", padx=22)

        self._info2_lbl = tk.Label(f, text="", bg=RED_LT, fg="#7a0a0a",
                                    font=("Helvetica",9), padx=12, pady=10)
        self._info2_lbl.pack(fill="x", padx=22, pady=14)

    # ── LANGUAGE ──────────────────────────────────────────────────
    def _switch(self, lang):
        self.lang = lang
        self._apply_lang()

    def _apply_lang(self):
        L = self.L
        self.title(L("title"))
        self._nb.tab(0, text=L("tab1"))
        self._nb.tab(1, text=L("tab2"))
        self._nb.tab(2, text=L("tab3"))
        self._lbl_url.configure(text=L("url_label"))
        self._btn.configure(text=L("btn_go") if not self._running else L("btn_running"))
        self._chk1.configure(text=L("opt1"))
        self._chk2.configure(text=L("opt2"))
        self._chk3.configure(text=L("opt3"))
        self._banner_lbl.configure(text=L("info"))
        self._log_lbl.configure(text=L("log_title"))
        for k,tk_key in [("s1","stat1"),("s2","stat2"),("s3","stat3"),("s4","stat4")]:
            self._slbl[k].configure(text=L(tk_key))
        # tree headings
        role_lbl = {"FR":"Rôle","ES":"Rol","EN":"Role"}.get(self.lang,"Rôle")
        for col,key in [("num","col_num"),("name","col_name"),("addr","col_addr"),
                        ("phone","col_phone"),("email","col_email"),("src","col_src")]:
            self._tree.heading(col, text=L(key))
        self._tree.heading("role", text=role_lbl)
        self._btn_copy.configure(text=L("btn_copy"))
        self._btn_csv.configure(text=L("btn_csv"))
        self._set_title.configure(text=L("set_title"))
        self._set_desc.configure(text=L("set_desc"))
        self._btn_save.configure(text=L("btn_save"))
        self._info2_lbl.configure(text=L("info2"))
        self._lbl_status.configure(text=L("ready"))
        if self.results:
            self._refresh_table()

    # ── LOGIC ─────────────────────────────────────────────────────
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
        messagebox.showinfo("OK", self.L("saved"))

    def _start(self):
        if self._running: return
        url = self._url_var.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("", self.L("err_url")); return
        self._running = True
        self._btn.configure(state="disabled", text=self.L("btn_running"))
        self._log.configure(state="normal"); self._log.delete("1.0","end")
        self._log.configure(state="disabled")
        self._set_prog(0,"")
        for v in self._sv.values(): v.set("—")
        excl = self.excl if self._v3.get() else []
        threading.Thread(target=self._run, args=(url,excl), daemon=True).start()

    def _run(self, url, excl):
        try:
            dealers = scrape(url, excl, self._log_add, self._set_prog)
            self._set_prog(50, "Enrichissement…")

            if self._v1.get():
                pending = [d for d in dealers if not d["emails"]]
                self._log_add(f"Recherche web pour {len(pending)} concessionnaires sans email…")
                for i,d in enumerate(pending):
                    pct = 50 + int(40*i/max(len(pending),1))
                    self._set_prog(pct, f"Recherche web {i+1}/{len(pending)}…")
                    self._log_add(f"  → {d['name'][:40]}")
                    found = web_search_all_emails(d["name"], d["addr"], excl, self._log_add)
                    if found:
                        d["emails"] = {e: guess_role(e) for e in found}
                        d["src"] = "web"
                        self._log_add(f"     ✓ {len(found)} email(s): {', '.join(sorted(found)[:3])}")
                    time.sleep(1.2)

            if self._v2.get():
                seen,uniq = set(),[]
                for d in dealers:
                    k = d["name"].lower()[:25]
                    if k not in seen: seen.add(k); uniq.append(d)
                dealers = uniq

            self._set_prog(100, "Terminé !")
            total_em = sum(len(d["emails"]) for d in dealers)
            self._log_add(f"─── {len(dealers)} concessionnaires, {total_em} emails au total")
            self.results = dealers
            self.after(0, self._finish)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
            self._log_add(f"ERREUR: {e}")
            self.after(0, lambda: self._btn.configure(state="normal", text=self.L("btn_go")))
            self._running = False

    def _finish(self):
        self._running = False
        d = self.results
        em = sum(len(x["emails"]) for x in d)
        wb = sum(1 for x in d if x["src"]=="web")
        ad = sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d)))
        self._sv["s2"].set(str(em))
        self._sv["s3"].set(str(wb))
        self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal", text=self.L("btn_again"))
        self._lbl_status.configure(
            text=self.L("last") + datetime.now().strftime("%H:%M"))
        self._refresh_table()
        self._nb.select(self._f2)

    def _refresh_table(self):
        d = self.results
        em = sum(len(x["emails"]) for x in d)
        ad = sum(1 for x in d if x["addr"])
        self._meta_lbl.configure(
            text=f"{len(d)} {self.L('stat1')} · {em} {self.L('stat2')} · {ad} {self.L('stat4')}")
        for row in self._tree.get_children(): self._tree.delete(row)
        row_num = 1
        for x in d:
            sl = {"page":self.L("src_page"),"web":self.L("src_web")}.get(x["src"],self.L("src_miss"))
            if not x["emails"]:
                # No emails found — one row
                self._tree.insert("","end", tags=("miss",),
                    values=(row_num, x["name"], x["addr"], x["phone"], "—", sl, "—"))
                row_num += 1
            else:
                # One row per email found
                for idx, (email, role) in enumerate(sorted(x["emails"].items())):
                    tag = "" if x["src"]=="page" else "web"
                    name_cell = x["name"] if idx==0 else ""
                    addr_cell = x["addr"] if idx==0 else ""
                    phone_cell = x["phone"] if idx==0 else ""
                    src_cell = sl if idx==0 else ""
                    self._tree.insert("","end", tags=(tag,),
                        values=(row_num if idx==0 else "", name_cell, addr_cell,
                                phone_cell, email, src_cell, role))
                row_num += 1

    def _copy_emails(self):
        em = []
        for x in self.results:
            em.extend(x["emails"].keys())
        em = sorted(set(em))
        if not em: messagebox.showinfo("",self.L("no_copy")); return
        self.clipboard_clear(); self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓", f"{len(em)} {self.L('copied')}")

    def _export_csv(self):
        if not self.results:
            messagebox.showinfo("",self.L("no_copy")); return
        desk = os.path.join(os.path.expanduser("~"),"Desktop")
        os.makedirs(desk, exist_ok=True)
        fname = f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        fpath = os.path.join(desk, fname)
        date_str = datetime.now().strftime("%d/%m/%Y")
        rows_written = 0
        with open(fpath,"w",newline="",encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([self.L("col_name"), self.L("col_addr"), self.L("col_phone"),
                        self.L("col_email"), "Rôle / Role", self.L("col_src"), "Date"])
            for x in self.results:
                sl = {"page":self.L("src_page"),"web":self.L("src_web")}.get(x["src"],self.L("src_miss"))
                if not x["emails"]:
                    w.writerow([x["name"],x["addr"],x["phone"],"","",sl,date_str])
                    rows_written += 1
                else:
                    for idx,(email,role) in enumerate(sorted(x["emails"].items())):
                        w.writerow([
                            x["name"] if idx==0 else "",
                            x["addr"] if idx==0 else "",
                            x["phone"] if idx==0 else "",
                            email, role,
                            sl if idx==0 else "",
                            date_str if idx==0 else "",
                        ])
                        rows_written += 1
        messagebox.showinfo("✓", f"{self.L('export_ok')}\n{fname}\n\n{rows_written} lignes")

if __name__ == "__main__":
    app = App()
    app.mainloop()
