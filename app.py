#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silence.eco — Dealer Finder v9"""
import tkinter as tk
import json, re, time, os, csv, random, threading
import urllib.request, urllib.parse, urllib.error
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

RED="#D01A20";RED_D="#A01015";RED_LT="#FAE8E8";DARK="#1C1C1E"
GRAY="#F2F2F2";WHITE="#FFFFFF";MUTED="#8A8A8E";BORDER="#E0E0E0"
GREEN="#15803d";GREEN_LT="#F0FFF4"

T={"FR":dict(title="Silence.eco — Dealer Finder",tab1="  Extraction  ",tab2="  Résultats  ",tab3="  Paramètres  ",url_label="URL de la page réseau concessionnaires :",btn_go="  Extraire  ",btn_running="  En cours…  ",btn_again="  Relancer  ",opt1="Recherche emails (web + Hunter + IA)",opt2="Dédupliquer",opt3="Exclure emails constructeur",info="Analyse la page → extrait tous les concessionnaires\n→ trouve leur site web → scrape les emails\n→ interroge Hunter.io → enrichit via Claude AI",log_title="Journal :",col_num="#",col_name="Nom",col_addr="Adresse",col_phone="Téléphone",col_email="Email",col_src="Source",col_role="Rôle / Personne",src_page="Page",src_web="Web",src_hunter="Hunter.io",src_ai="Claude AI",stat1="Concessionnaires",stat2="Emails trouvés",stat3="Via web/IA",stat4="Adresses",btn_copy="Copier les emails",btn_csv="Exporter CSV",no_results="Aucun résultat — lancez une extraction",set_hunter="Hunter.io — Clé API",set_hunter_desc="Trouve tous les emails d'un domaine avec nom et poste",set_claude="Claude AI — Clé API",set_claude_desc="Recherche intelligente anti-blocage et enrichissement",set_excl="Domaines constructeurs à exclure :",set_excl_desc="(un par ligne)",btn_verify="Vérifier",btn_save="  Enregistrer  ",info2="Données traitées localement.",copied="emails copiés !",no_copy="Aucun email à copier.",saved="Paramètres enregistrés !",err_url="URL invalide",export_ok="CSV sauvegardé :",ready="Prêt",last="Dernier run : "),
"ES":dict(title="Silence.eco — Dealer Finder",tab1="  Extracción  ",tab2="  Resultados  ",tab3="  Ajustes  ",url_label="URL de la página red de concesionarios:",btn_go="  Extraer  ",btn_running="  En proceso…  ",btn_again="  Reiniciar  ",opt1="Buscar emails (web + Hunter + IA)",opt2="Eliminar duplicados",opt3="Excluir emails fabricante",info="Analiza la página → extrae concesionarios\n→ encuentra su web → extrae emails\n→ Hunter.io → Claude AI",log_title="Registro:",col_num="#",col_name="Nombre",col_addr="Dirección",col_phone="Teléfono",col_email="Email",col_src="Fuente",col_role="Rol / Persona",src_page="Página",src_web="Web",src_hunter="Hunter.io",src_ai="Claude AI",stat1="Concesionarios",stat2="Emails encontrados",stat3="Vía web/IA",stat4="Direcciones",btn_copy="Copiar emails",btn_csv="Exportar CSV",no_results="Sin resultados",set_hunter="Hunter.io — Clave API",set_hunter_desc="Encuentra todos los emails de un dominio",set_claude="Claude AI — Clave API",set_claude_desc="Búsqueda inteligente anti-bloqueo",set_excl="Dominios del fabricante a excluir:",set_excl_desc="(uno por línea)",btn_verify="Verificar",btn_save="  Guardar  ",info2="Datos procesados localmente.",copied="emails copiados!",no_copy="Sin emails.",saved="¡Guardado!",err_url="URL inválida",export_ok="CSV guardado:",ready="Listo",last="Última extracción: "),
"EN":dict(title="Silence.eco — Dealer Finder",tab1="  Extraction  ",tab2="  Results  ",tab3="  Settings  ",url_label="Dealer network page URL:",btn_go="  Extract  ",btn_running="  Running…  ",btn_again="  Run Again  ",opt1="Find emails (web + Hunter + AI)",opt2="Deduplicate",opt3="Exclude manufacturer emails",info="Scans the page → extracts all dealers\n→ finds their website → scrapes emails\n→ Hunter.io → Claude AI",log_title="Log:",col_num="#",col_name="Name",col_addr="Address",col_phone="Phone",col_email="Email",col_src="Source",col_role="Role / Person",src_page="Page",src_web="Web",src_hunter="Hunter.io",src_ai="Claude AI",stat1="Dealers",stat2="Emails found",stat3="Via web/AI",stat4="Addresses",btn_copy="Copy emails",btn_csv="Export CSV",no_results="No results yet",set_hunter="Hunter.io — API Key",set_hunter_desc="Find all emails for a domain with name and position",set_claude="Claude AI — API Key",set_claude_desc="Smart anti-block search and enrichment",set_excl="Manufacturer domains to exclude:",set_excl_desc="(one per line)",btn_verify="Verify",btn_save="  Save  ",info2="Data processed locally.",copied="emails copied!",no_copy="No emails to copy.",saved="Settings saved!",err_url="Invalid URL",export_ok="CSV saved:",ready="Ready",last="Last run: ")}

EXCL_DEFAULT=["silence.eco","aixam.com","microcar.fr","ligier.fr","chatenet.com","casalini.it","bellier.fr","grecav.com"]
CONSTRUCTOR_DOMS=EXCL_DEFAULT+["renault.fr","peugeot.fr","citroen.fr","toyota.fr","volkswagen.fr","ford.fr","opel.fr","seat.es","skoda.fr","bmw.fr","mercedes.fr","audi.fr"]
PLATFORM_DOMS=["duckduckgo.com","google.","facebook.","instagram.","twitter.","linkedin.","youtube.","yelp.","tripadvisor.","pagesjaunes.","societe.com","wix.","squarespace.","shopify.","wordpress.","example.com","test.com","noreply.","sentry.","w3.org","schema.org","cloudflare.","microsoft.","apple.","amazon."]
EMAIL_RE=re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE=re.compile(r"(?:\+33|\+34|\+44|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}")
ADDR_RE=re.compile(r"\d{1,4}[\s,]+[^\d\n]{5,50}[\s,]+\d{5}[\s,]+[A-ZÀ-Ÿa-zà-ÿ\s\-]{2,30}",re.I)
UA_POOL=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.3 Safari/605.1.15","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"]

def make_hdrs(ref="https://www.google.com"):
    return {"User-Agent":random.choice(UA_POOL),"Accept":"text/html,application/xhtml+xml,*/*;q=0.8","Accept-Language":"fr-FR,fr;q=0.9,en;q=0.7","Accept-Encoding":"gzip, deflate","Connection":"keep-alive","Referer":ref,"DNT":"1"}

def fetch(url,timeout=18,retries=3,ref="https://www.google.com"):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers=make_hdrs(ref))
            with urllib.request.urlopen(req,timeout=timeout) as r:
                raw=r.read()
                enc=r.headers.get_content_charset("utf-8") or "utf-8"
                return raw.decode(enc,errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in(403,429): time.sleep(2**i+random.uniform(1,3))
            last=e
        except Exception as e:
            last=e
            if i<retries-1: time.sleep(1.5*(i+1))
    raise last or Exception(f"Failed: {url}")

def is_real(e):
    if not e or len(e)<7 or "@" not in e: return False
    dom=e.split("@")[-1].lower()
    if any(f in dom for f in PLATFORM_DOMS): return False
    if re.search(r"\.(png|jpg|gif|css|js|svg|ico|woff)$",dom): return False
    return "." in dom and len(dom.split(".")[0])>=2

ROLE_MAP=[
    (["direction","directeur","directrice","pdg","ceo","dg","gerant","patron"],"Direction"),
    (["commercial","vente","ventes","sales","vendeur","vendeuse"],"Commercial"),
    (["marketing","communication","comm","media","promo","digital"],"Marketing"),
    (["comptabilite","comptable","compta","facturation","finance"],"Comptabilité"),
    (["contact","info","information","hello","bonjour","accueil","reception"],"Contact"),
    (["apv","atelier","technique","sav","service","reparation"],"Après-vente"),
    (["rh","hr","recrutement","emploi"],"RH"),
    (["secretariat","admin","administration","assistante"],"Administration"),
]
def guess_role(e):
    local=re.sub(r"[.\-_]","",e.split("@")[0].lower())
    for kws,lbl in ROLE_MAP:
        if any(k in local for k in kws): return lbl
    return "Équipe"

def get_emails(text,excl):
    out=set()
    for m in EMAIL_RE.finditer(text):
        e=m.group(0).lower().strip(".,;:<>\"'")
        dom=e.split("@")[-1]
        if not any(x in dom for x in excl) and is_real(e): out.add(e)
    return out

def get_phones(text):
    seen,out=set(),[]
    for m in PHONE_RE.finditer(text):
        p=re.sub(r"[\s.\-]","",m.group(0))
        if p not in seen: seen.add(p);out.append(p)
    return out

def claude_find_emails(name,addr,api_key,log):
    if not api_key: return {}
    log(f"  Claude AI → {name[:35]}")
    try:
        city=""
        if addr:
            m=re.search(r"\d{5}\s+(\S+)",addr)
            if m: city=m.group(1)
        prompt=(f"Trouve le site web officiel ET tous les emails professionnels de ce concessionnaire:\n"
                f"Nom: {name}\nAdresse: {addr or 'inconnue'}\nVille: {city or 'inconnue'}\n\n"
                f"Trouve leur PROPRE site (pas le constructeur). Collecte TOUS les emails avec rôle/nom.\n"
                f"Réponds UNIQUEMENT en JSON: {{\"website\":\"domaine.fr\",\"emails\":{{\"email@ex.com\":\"Directeur Jean Dupont\"}}}}\n"
                f"Si rien: {{}}")
        payload=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":1024,"tools":[{"type":"web_search_20250305","name":"web_search"}],"messages":[{"role":"user","content":prompt}]}).encode()
        req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=payload,headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01","anthropic-beta":"web-search-2025-03-05"},method="POST")
        with urllib.request.urlopen(req,timeout=45) as r: data=json.loads(r.read())
        txt=" ".join(b["text"] for b in data.get("content",[]) if b.get("type")=="text")
        m=re.search(r'\{[^{}]*"emails"\s*:\s*\{[^{}]*\}[^{}]*\}',txt,re.S) or re.search(r'\{.*\}',txt,re.S)
        if m:
            res=json.loads(m.group(0))
            clean={e:r for e,r in res.get("emails",{}).items() if is_real(e)}
            if clean: log(f"     ✅ Claude: {len(clean)} email(s)")
            return clean
    except Exception as e: log(f"     Claude err: {str(e)[:50]}")
    return {}

def hunter_search(domain,api_key,excl,log):
    if not api_key or not domain: return {}
    try:
        url=f"https://api.hunter.io/v2/domain-search?domain={urllib.parse.quote(domain)}&api_key={api_key}&limit=100"
        data=json.loads(fetch(url,timeout=15))
        res={}
        for item in data.get("data",{}).get("emails",[]):
            e=item.get("value","").lower()
            if not e or not is_real(e) or any(x in e.split("@")[-1] for x in excl): continue
            fn=(item.get("first_name") or "").strip();ln=(item.get("last_name") or "").strip()
            pos=(item.get("position") or "").strip()
            parts=[p for p in [f"{fn} {ln}".strip(),pos] if p]
            res[e]=" — ".join(parts) if parts else guess_role(e)
        log(f"  Hunter ({domain}): {len(res)} email(s)")
        return res
    except Exception as e: log(f"  Hunter err: {str(e)[:40]}"); return {}

def find_domain(name,addr,log):
    city=""
    if addr:
        m=re.search(r"\d{5}\s+(\S+)",addr)
        if m: city=m.group(1)
    for q in [f'"{name}" site officiel',f'{name} {city} site web' if city else f'{name} site web']:
        try:
            html=fetch("https://html.duckduckgo.com/html/?q="+urllib.parse.quote(q),timeout=15,ref="https://duckduckgo.com")
            for href in re.findall(r'href="(https?://[^"&]{8,})"',html):
                dom=re.sub(r"https?://(?:www\.)?","",href).split("/")[0].lower().strip()
                if not dom or "." not in dom or len(dom)<5: continue
                if any(c in dom for c in CONSTRUCTOR_DOMS): continue
                if any(p in dom for p in PLATFORM_DOMS): continue
                log(f"  Site: {dom}"); return dom
            time.sleep(random.uniform(1,2))
        except Exception as e: log(f"  find_domain err: {str(e)[:35]}")
    return ""

def scrape_domain(domain,excl,log):
    found=set()
    for page in [f"https://{domain}",f"https://www.{domain}",f"https://{domain}/contact",f"https://www.{domain}/contact",f"https://{domain}/nous-contacter"]:
        try:
            html=fetch(page,timeout=12,ref=f"https://{domain}")
            base=domain.replace("www.","")
            same={e for e in get_emails(html,excl) if base in e}
            if same: found.update(same);log(f"  Scrape {page}: {len(same)} email(s)")
            if len(found)>=8: break
            time.sleep(random.uniform(0.5,1.2))
        except: continue
    return found

def enrich(dealer,excl,hunter_key,claude_key,log):
    all_em=dict(dealer.get("emails",{}));src=dealer.get("src","pending")
    domain=find_domain(dealer["name"],dealer["addr"],log)
    if domain:
        dealer["website"]=domain
        for e in scrape_domain(domain,excl,log):
            if e not in all_em: all_em[e]=guess_role(e)
        if all_em: src="web"
    if domain and hunter_key:
        h=hunter_search(domain,hunter_key,excl,log)
        all_em.update(h)
        if h: src="hunter"
    if not all_em and claude_key:
        ai=claude_find_emails(dealer["name"],dealer["addr"],claude_key,log)
        all_em.update(ai)
        if ai: src="ai"
    return {e:r for e,r in all_em.items() if is_real(e)},src

def scrape_page(url,excl,log,prog):
    prog(5,"Chargement de la page…");log(f"GET {url}")
    html=fetch(url,retries=4);log(f"Page: {len(html)//1024} Ko")
    prog(18,"Analyse des blocs…");dealers=[]
    try:
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(html,"html.parser")
        for t in soup(["script","style","nav","footer","head"]): t.decompose()
        blocks,best=[],0
        for sel in ["[class*='dealer']","[class*='concess']","[class*='revendeur']","[class*='reseau']","[class*='network']","[class*='store']","[class*='location']","[class*='point']","[class*='retailer']","[class*='item']","[class*='card']","article","li"]:
            found=soup.select(sel)
            valid=[b for b in found if PHONE_RE.search(b.get_text()) or EMAIL_RE.search(b.get_text()) or len(b.get_text(strip=True))>30]
            if len(valid)>best: best=len(valid);blocks=valid
        log(f"Meilleur sélecteur → {len(blocks)} blocs")
        if best<3:
            blocks=[d for d in soup.find_all(["div","li","article","section"]) if PHONE_RE.search(d.get_text())]
            log(f"Fallback → {len(blocks)} blocs")
        seen=set()
        for blk in blocks:
            txt=blk.get_text(" ",strip=True)
            if len(txt)<12: continue
            name=""
            for tag in blk.find_all(["h1","h2","h3","h4","h5","strong","b"]):
                v=tag.get_text(strip=True)
                if 3<len(v)<90 and not PHONE_RE.match(v) and not v.replace(" ","").isdigit(): name=v;break
            if not name:
                for line in re.split(r"[\n|·•]",txt):
                    line=line.strip()
                    if 3<len(line)<90 and not PHONE_RE.match(line): name=line;break
            if not name: continue
            if re.match(r"^(t[eé]l\.?\s*:?\s*)[\d\s.\-\+]{6,}$",name,re.I): continue
            key=re.sub(r"[^a-z0-9]","",name.lower())[:20]
            if not key or key in seen: continue
            seen.add(key)
            am=ADDR_RE.search(txt);addr=am.group(0).strip()[:100] if am else ""
            phones=get_phones(txt);phone=phones[0] if phones else ""
            pg=get_emails(txt,excl)
            for a in blk.find_all("a",href=True):
                h=a["href"]
                if h.startswith("mailto:"):
                    e=h[7:].split("?")[0].strip().lower()
                    if is_real(e) and not any(x in e.split("@")[-1] for x in excl): pg.add(e)
            dealers.append({"name":name[:80],"addr":addr,"phone":phone,"website":"","emails":{e:guess_role(e) for e in pg},"src":"page" if pg else "pending"})
    except ImportError:
        log("bs4 non dispo — regex")
        clean=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",html));phones=get_phones(clean);seen=set()
        for ph in phones:
            idx=clean.find(re.sub(r"[\s.\-]","",ph)[:6])
            if idx<0: continue
            ctx=clean[max(0,idx-200):idx+200];em_l=list(get_emails(ctx,excl))
            nm=re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿa-zà-ÿ\-]+){1,4})",ctx)
            name=nm.group(1) if nm else f"Dealer {len(dealers)+1}"
            key=re.sub(r"[^a-z0-9]","",name.lower())[:15]
            if key in seen: continue
            seen.add(key)
            dealers.append({"name":name[:80],"addr":"","phone":ph,"website":"","emails":{e:guess_role(e) for e in em_l},"src":"page" if em_l else "pending"})
    final,seen2=[],set()
    for d in dealers:
        k=re.sub(r"[^a-z0-9]","",d["name"].lower())[:18]
        if k and k not in seen2: seen2.add(k);final.append(d)
    log(f"✓ {len(final)} concessionnaires uniques");return final

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang="FR";self.results=[];self.excl=list(EXCL_DEFAULT)
        self.hunter_key="6f720d52e7ff130ef0717a890cd35abcac84c6fd";self.claude_key="";self._running=False
        self.configure(bg=DARK);self.geometry("1050x700");self.minsize(820,580)
        self._build();self._apply_lang()
    def L(self,k): return T[self.lang].get(k,k)
    def _build(self): self._mk_hdr();self._mk_nb()
    def _mk_hdr(self):
        hdr=tk.Frame(self,bg=DARK,pady=10);hdr.pack(fill="x")
        left=tk.Frame(hdr,bg=DARK);left.pack(side="left",padx=20)
        c=tk.Canvas(left,width=34,height=34,bg=DARK,highlightthickness=0);c.pack(side="left")
        c.create_rectangle(0,0,34,34,fill=RED,outline="")
        c.create_polygon([17,4,28,10,28,24,17,30,6,24,6,10],outline=WHITE,fill="",width=2)
        c.create_oval(12,12,22,22,fill=WHITE,outline="")
        tk.Label(left,text="  SILENCE",bg=DARK,fg=WHITE,font=("Helvetica",16,"bold")).pack(side="left")
        tk.Label(left,text=" ECO · DEALER FINDER",bg=DARK,fg=RED,font=("Helvetica",9)).pack(side="left")
        right=tk.Frame(hdr,bg=DARK);right.pack(side="right",padx=20)
        self._lbl_status=tk.Label(right,text="",bg=DARK,fg=MUTED,font=("Helvetica",10))
        self._lbl_status.pack(side="left",padx=(0,16))
        for code in ("FR","ES","EN"):
            tk.Button(right,text=code,bg="#2C2C2E",fg=WHITE,font=("Helvetica",9,"bold"),relief="flat",width=3,cursor="hand2",bd=0,pady=4,command=lambda c=code:self._switch(c)).pack(side="left",padx=2)
    def _mk_nb(self):
        s=ttk.Style(self);s.theme_use("clam")
        s.configure("TNotebook",background=DARK,borderwidth=0,tabmargins=0)
        s.configure("TNotebook.Tab",background="#2C2C2E",foreground=MUTED,padding=[16,9],font=("Helvetica",11))
        s.map("TNotebook.Tab",background=[("selected",WHITE)],foreground=[("selected",RED)])
        s.configure("TFrame",background=WHITE)
        s.configure("Red.Horizontal.TProgressbar",troughcolor=BORDER,background=RED,thickness=5)
        s.configure("Treeview",rowheight=26,font=("Helvetica",10),background=WHITE,fieldbackground=WHITE,foreground=DARK)
        s.configure("Treeview.Heading",font=("Helvetica",9,"bold"),background=GRAY,foreground=MUTED)
        s.map("Treeview",background=[("selected",RED_LT)],foreground=[("selected",DARK)])
        self._nb=ttk.Notebook(self);self._nb.pack(fill="both",expand=True)
        self._f1=ttk.Frame(self._nb);self._f2=ttk.Frame(self._nb);self._f3=ttk.Frame(self._nb)
        self._nb.add(self._f1,text="");self._nb.add(self._f2,text="");self._nb.add(self._f3,text="")
        self._build_t1();self._build_t2();self._build_t3()
    def _build_t1(self):
        f=self._f1;P=dict(padx=22,pady=6)
        self._lbl_url=tk.Label(f,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9,"bold"))
        self._lbl_url.pack(anchor="w",padx=22,pady=(16,3))
        row=tk.Frame(f,bg=WHITE);row.pack(fill="x",**P)
        self._url_var=tk.StringVar(value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        tk.Entry(row,textvariable=self._url_var,font=("Helvetica",11),bg=GRAY,relief="flat",bd=0,highlightthickness=1,highlightbackground=BORDER,highlightcolor=RED).pack(side="left",fill="x",expand=True,ipady=8,padx=(0,8))
        self._btn=tk.Button(row,text="",bg=RED,fg=WHITE,font=("Helvetica",11,"bold"),relief="flat",cursor="hand2",bd=0,padx=16,pady=8,command=self._start)
        self._btn.pack(side="left")
        opt=tk.Frame(f,bg=WHITE);opt.pack(fill="x",**P)
        self._v1=tk.BooleanVar(value=True);self._v2=tk.BooleanVar(value=True);self._v3=tk.BooleanVar(value=True)
        self._chk1=tk.Checkbutton(opt,text="",variable=self._v1,bg=WHITE,fg=DARK,font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk2=tk.Checkbutton(opt,text="",variable=self._v2,bg=WHITE,fg=DARK,font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk3=tk.Checkbutton(opt,text="",variable=self._v3,bg=WHITE,fg=DARK,font=("Helvetica",10),activebackground=WHITE,selectcolor=WHITE,cursor="hand2")
        self._chk1.pack(side="left",padx=(0,14));self._chk2.pack(side="left",padx=(0,14));self._chk3.pack(side="left")
        ai_row=tk.Frame(f,bg=WHITE);ai_row.pack(fill="x",padx=22,pady=(0,4))
        self._hunter_ind=tk.Label(ai_row,text="⬤ Hunter.io : non configuré",bg=WHITE,fg=MUTED,font=("Helvetica",9))
        self._hunter_ind.pack(side="left",padx=(0,16))
        self._claude_ind=tk.Label(ai_row,text="⬤ Claude AI : non configuré",bg=WHITE,fg=MUTED,font=("Helvetica",9))
        self._claude_ind.pack(side="left")
        banner=tk.Frame(f,bg=RED_LT);banner.pack(fill="x",padx=22,pady=(0,8))
        tk.Frame(banner,bg=RED,width=3).pack(side="left",fill="y")
        self._banner_lbl=tk.Label(banner,text="",bg=RED_LT,fg="#7a0a0a",font=("Helvetica",9),justify="left")
        self._banner_lbl.pack(padx=10,pady=8,anchor="w")
        pf=tk.Frame(f,bg=WHITE);pf.pack(fill="x",**P)
        self._prog_lbl=tk.Label(pf,text="",bg=WHITE,fg=DARK,font=("Helvetica",10,"bold"))
        self._prog_lbl.pack(anchor="w")
        self._prog_var=tk.DoubleVar()
        ttk.Progressbar(pf,variable=self._prog_var,maximum=100,style="Red.Horizontal.TProgressbar").pack(fill="x",pady=(4,0))
        lf=tk.Frame(f,bg=WHITE);lf.pack(fill="both",expand=True,**P)
        self._log_lbl=tk.Label(lf,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9,"bold"))
        self._log_lbl.pack(anchor="w")
        self._log=scrolledtext.ScrolledText(lf,height=7,font=("Courier",9),bg=GRAY,fg=DARK,relief="flat",bd=0,state="disabled",wrap="word",highlightthickness=0)
        self._log.pack(fill="both",expand=True,pady=(3,0))
        sf=tk.Frame(f,bg=WHITE);sf.pack(fill="x",padx=22,pady=(4,16))
        self._sv={};self._slbl={}
        for k in ("s1","s2","s3","s4"):
            c=tk.Frame(sf,bg=GRAY,padx=14,pady=10);c.pack(side="left",fill="x",expand=True,padx=(0,8))
            lbl=tk.Label(c,text="",bg=GRAY,fg=MUTED,font=("Helvetica",9));lbl.pack(anchor="w")
            v=tk.StringVar(value="—");col=RED if k=="s2" else DARK
            tk.Label(c,textvariable=v,bg=GRAY,fg=col,font=("Helvetica",22,"bold")).pack(anchor="w")
            self._sv[k]=v;self._slbl[k]=lbl
    def _build_t2(self):
        f=self._f2
        top=tk.Frame(f,bg=WHITE);top.pack(fill="x",padx=16,pady=10)
        self._meta_lbl=tk.Label(top,text="",bg=WHITE,fg=MUTED,font=("Helvetica",10));self._meta_lbl.pack(side="left")
        self._btn_csv=tk.Button(top,text="",bg=RED,fg=WHITE,font=("Helvetica",10,"bold"),relief="flat",cursor="hand2",bd=0,padx=12,pady=5,command=self._export_csv);self._btn_csv.pack(side="right")
        self._btn_copy=tk.Button(top,text="",bg=WHITE,fg=DARK,font=("Helvetica",10),relief="flat",bd=1,cursor="hand2",padx=10,pady=5,highlightbackground=BORDER,command=self._copy_emails);self._btn_copy.pack(side="right",padx=(0,8))
        tf=tk.Frame(f,bg=WHITE);tf.pack(fill="both",expand=True,padx=16,pady=(0,14))
        self._tree=ttk.Treeview(tf,columns=("num","name","addr","phone","email","role","src"),show="headings",selectmode="browse")
        for col,w in [("num",36),("name",195),("addr",155),("phone",100),("email",180),("role",145),("src",85)]:
            self._tree.column(col,width=w,minwidth=30)
        vsb=ttk.Scrollbar(tf,orient="vertical",command=self._tree.yview)
        hsb=ttk.Scrollbar(tf,orient="horizontal",command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.pack(side="right",fill="y");hsb.pack(side="bottom",fill="x");self._tree.pack(fill="both",expand=True)
        self._tree.tag_configure("miss",background="#FFF5F5")
        self._tree.tag_configure("web",background="#FFFBF0")
        self._tree.tag_configure("hunter",background=GREEN_LT)
        self._tree.tag_configure("ai",background="#EEF4FF")
    def _build_t3(self):
        f=self._f3;P=dict(padx=22,pady=6)
        def api_sec(title_k,desc_k,var_attr,stat_attr,verify_cmd):
            fr=tk.Frame(f,bg=WHITE,highlightthickness=1,highlightbackground=BORDER);fr.pack(fill="x",padx=22,pady=(14,0))
            top=tk.Frame(fr,bg=WHITE);top.pack(fill="x",padx=14,pady=(10,3))
            tk.Label(top,text=self.L(title_k),bg=WHITE,fg=DARK,font=("Helvetica",11,"bold")).pack(side="left")
            lbl=tk.Label(top,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9));lbl.pack(side="right")
            setattr(self,stat_attr,lbl)
            tk.Label(fr,text=self.L(desc_k),bg=WHITE,fg=MUTED,font=("Helvetica",9)).pack(anchor="w",padx=14,pady=(0,6))
            row=tk.Frame(fr,bg=WHITE);row.pack(fill="x",padx=14,pady=(0,10))
            var=tk.StringVar();setattr(self,var_attr,var)
            tk.Entry(row,textvariable=var,font=("Helvetica",11),bg=GRAY,relief="flat",bd=0,show="•",highlightthickness=1,highlightbackground=BORDER,highlightcolor=RED).pack(side="left",fill="x",expand=True,ipady=7,padx=(0,8))
            tk.Button(row,text=self.L("btn_verify"),bg=DARK,fg=WHITE,font=("Helvetica",10),relief="flat",bd=0,padx=12,pady=7,cursor="hand2",command=verify_cmd).pack(side="left")
        api_sec("set_hunter","set_hunter_desc","_hunter_var","_hunter_st",self._test_hunter)
        api_sec("set_claude","set_claude_desc","_claude_var","_claude_st",self._test_claude)
        self._set_excl_title=tk.Label(f,text="",bg=WHITE,fg=DARK,font=("Helvetica",11,"bold"));self._set_excl_title.pack(anchor="w",padx=22,pady=(16,2))
        self._set_excl_desc=tk.Label(f,text="",bg=WHITE,fg=MUTED,font=("Helvetica",9));self._set_excl_desc.pack(anchor="w",padx=22)
        self._excl_txt=tk.Text(f,height=6,font=("Courier",10),bg=GRAY,fg=DARK,relief="flat",bd=0,highlightthickness=1,highlightbackground=BORDER,highlightcolor=RED)
        self._excl_txt.pack(fill="x",**P);self._excl_txt.insert("1.0","\n".join(self.excl))
        self._btn_save=tk.Button(f,text="",bg=RED,fg=WHITE,font=("Helvetica",10,"bold"),relief="flat",cursor="hand2",bd=0,padx=14,pady=7,command=self._save);self._btn_save.pack(anchor="w",padx=22)
        self._info2_lbl=tk.Label(f,text="",bg=RED_LT,fg="#7a0a0a",font=("Helvetica",9),padx=12,pady=10);self._info2_lbl.pack(fill="x",padx=22,pady=10)
    def _switch(self,lang): self.lang=lang;self._apply_lang()
    def _upd_ind(self):
        self._hunter_ind.configure(text="⬤ Hunter.io : actif" if self.hunter_key else "⬤ Hunter.io : non configuré",fg=GREEN if self.hunter_key else MUTED)
        self._claude_ind.configure(text="⬤ Claude AI : actif" if self.claude_key else "⬤ Claude AI : non configuré",fg=GREEN if self.claude_key else MUTED)
    def _apply_lang(self):
        L=self.L;self.title(L("title"))
        self._nb.tab(0,text=L("tab1"));self._nb.tab(1,text=L("tab2"));self._nb.tab(2,text=L("tab3"))
        self._lbl_url.configure(text=L("url_label"))
        self._btn.configure(text=L("btn_go") if not self._running else L("btn_running"))
        self._chk1.configure(text=L("opt1"));self._chk2.configure(text=L("opt2"));self._chk3.configure(text=L("opt3"))
        self._banner_lbl.configure(text=L("info"));self._log_lbl.configure(text=L("log_title"))
        for k,tk_key in [("s1","stat1"),("s2","stat2"),("s3","stat3"),("s4","stat4")]: self._slbl[k].configure(text=L(tk_key))
        rl={"FR":"Rôle","ES":"Rol","EN":"Role"}.get(self.lang,"Rôle")
        for col,key in [("num","col_num"),("name","col_name"),("addr","col_addr"),("phone","col_phone"),("email","col_email"),("src","col_src")]: self._tree.heading(col,text=L(key))
        self._tree.heading("role",text=rl)
        self._btn_copy.configure(text=L("btn_copy"));self._btn_csv.configure(text=L("btn_csv"))
        self._set_excl_title.configure(text=L("set_excl"));self._set_excl_desc.configure(text=L("set_excl_desc"))
        self._btn_save.configure(text=L("btn_save"));self._info2_lbl.configure(text=L("info2"))
        self._lbl_status.configure(text=L("ready"));self._upd_ind()
        if self.results: self._refresh()
    def _test_hunter(self):
        key=self._hunter_var.get().strip()
        if not key: messagebox.showwarning("","Entrez votre clé Hunter.io"); return
        self._hunter_st.configure(text="…",fg=MUTED);self.update_idletasks()
        try:
            data=json.loads(fetch(f"https://api.hunter.io/v2/account?api_key={key}",timeout=10))
            plan=data.get("data",{}).get("plan_name","")
            s=data.get("data",{}).get("requests",{}).get("searches",{})
            self._hunter_st.configure(text=f"✓ {plan} {s.get('used','?')}/ {s.get('available','?')}",fg=GREEN)
            self.hunter_key=key;self._upd_ind()
            messagebox.showinfo("Hunter.io ✓",f"Plan: {plan}  Recherches: {s.get('used','?')} / {s.get('available','?')} ")
        except Exception as e: self._hunter_st.configure(text="✗",fg=RED);messagebox.showerror("Hunter.io",str(e))
    def _test_claude(self):
        key=self._claude_var.get().strip()
        if not key: messagebox.showwarning("","Entrez votre clé Claude"); return
        self._claude_st.configure(text="…",fg=MUTED);self.update_idletasks()
        try:
            payload=json.dumps({"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}).encode()
            req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=payload,headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"},method="POST")
            try:
                with urllib.request.urlopen(req,timeout=10): pass
            except urllib.error.HTTPError as e:
                if e.code!=400: raise
            self._claude_st.configure(text="✓ Valide",fg=GREEN);self.claude_key=key;self._upd_ind()
            messagebox.showinfo("Claude AI ✓","Clé API Claude valide !")
        except Exception as e: self._claude_st.configure(text="✗",fg=RED);messagebox.showerror("Claude AI",str(e))
    def _save(self):
        # keys are built-in
        raw=self._excl_txt.get("1.0","end").strip()
        self.excl=[l.strip().lstrip("@") for l in raw.splitlines() if l.strip()]
        self._upd_ind();messagebox.showinfo("OK",self.L("saved"))
    def _log_add(self,msg):
        self._log.configure(state="normal");self._log.insert("end",f"▸ {msg}\n");self._log.see("end");self._log.configure(state="disabled")
    def _set_prog(self,pct,lbl=""):
        self._prog_var.set(pct)
        if lbl: self._prog_lbl.configure(text=lbl)
        self.update_idletasks()
    def _start(self):
        if self._running: return
        url=self._url_var.get().strip()
        if not url.startswith("http"): messagebox.showerror("",self.L("err_url")); return
        self._running=True;self._btn.configure(state="disabled",text=self.L("btn_running"))
        self._log.configure(state="normal");self._log.delete("1.0","end");self._log.configure(state="disabled")
        self._set_prog(0,"")
        for v in self._sv.values(): v.set("—")
        excl=self.excl if self._v3.get() else []
        threading.Thread(target=self._run,args=(url,excl),daemon=True).start()
    def _run(self,url,excl):
        try:
            dealers=scrape_page(url,excl,self._log_add,self._set_prog);self._set_prog(45,"Enrichissement…")
            if self._v1.get():
                pending=[d for d in dealers if not d["emails"]]
                self._log_add(f"Enrichissement: {len(pending)} sans email…")
                for i,d in enumerate(pending):
                    self._set_prog(45+int(48*i/max(len(pending),1)),f"Enrichissement {i+1}/{len(pending)}")
                    self._log_add(f"→ {d['name'][:45]}")
                    ne,src=enrich(d,excl,self.hunter_key,self.claude_key,self._log_add)
                    if ne: d["emails"]=ne;d["src"]=src
                    time.sleep(random.uniform(0.8,1.5))
            if self._v2.get():
                seen,uniq=set(),[]
                for d in dealers:
                    k=re.sub(r"[^a-z0-9]","",d["name"].lower())[:20]
                    if k not in seen: seen.add(k);uniq.append(d)
                dealers=uniq
            self._set_prog(100,"Terminé !")
            total=sum(len(d["emails"]) for d in dealers)
            self._log_add(f"─── {len(dealers)} concessionnaires, {total} emails")
            self.results=dealers;self.after(0,self._finish)
        except Exception as e:
            self.after(0,lambda:messagebox.showerror("Erreur",str(e)))
            self._log_add(f"ERREUR: {e}")
            self.after(0,lambda:self._btn.configure(state="normal",text=self.L("btn_go")))
            self._running=False
    def _finish(self):
        self._running=False;d=self.results
        em=sum(len(x["emails"]) for x in d);wb=sum(1 for x in d if x["src"] in("web","hunter","ai"));ad=sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d)));self._sv["s2"].set(str(em));self._sv["s3"].set(str(wb));self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal",text=self.L("btn_again"))
        self._lbl_status.configure(text=self.L("last")+datetime.now().strftime("%H:%M"))
        self._refresh();self._nb.select(self._f2)
    def _refresh(self):
        d=self.results;em=sum(len(x["emails"]) for x in d);ad=sum(1 for x in d if x["addr"])
        self._meta_lbl.configure(text=f"{len(d)} {self.L('stat1')} · {em} {self.L('stat2')} · {ad} {self.L('stat4')}")
        for row in self._tree.get_children(): self._tree.delete(row)
        sm={"page":self.L("src_page"),"web":self.L("src_web"),"hunter":self.L("src_hunter"),"ai":self.L("src_ai")}
        n=1
        for x in d:
            sl=sm.get(x["src"],"—")
            if not x["emails"]:
                self._tree.insert("","end",tags=("miss",),values=(n,x["name"],x["addr"],x["phone"],"—","—",sl));n+=1
            else:
                for i,(email,role) in enumerate(sorted(x["emails"].items())):
                    tag={"page":"","web":"web","hunter":"hunter","ai":"ai"}.get(x["src"],"")
                    self._tree.insert("","end",tags=(tag,),values=(n if i==0 else "",x["name"] if i==0 else "",x["addr"] if i==0 else "",x["phone"] if i==0 else "",email,role,sl if i==0 else ""))
                n+=1
    def _copy_emails(self):
        em=sorted({e for x in self.results for e in x["emails"]})
        if not em: messagebox.showinfo("",self.L("no_copy")); return
        self.clipboard_clear();self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓",f"{len(em)} {self.L('copied')}")
    def _export_csv(self):
        if not self.results: messagebox.showinfo("",self.L("no_copy")); return
        desk=os.path.join(os.path.expanduser("~"),"Desktop");os.makedirs(desk,exist_ok=True)
        fname=f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv";fpath=os.path.join(desk,fname)
        sm={"page":self.L("src_page"),"web":self.L("src_web"),"hunter":self.L("src_hunter"),"ai":self.L("src_ai")}
        rows=0;date_s=datetime.now().strftime("%d/%m/%Y")
        with open(fpath,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f)
            w.writerow([self.L("col_name"),self.L("col_addr"),self.L("col_phone"),self.L("col_email"),self.L("col_role"),"Site web",self.L("col_src"),"Date"])
            for x in self.results:
                sl=sm.get(x["src"],"—");site=x.get("website","")
                if not x["emails"]:
                    w.writerow([x["name"],x["addr"],x["phone"],"","",site,sl,date_s]);rows+=1
                else:
                    for i,(email,role) in enumerate(sorted(x["emails"].items())):
                        w.writerow([x["name"] if i==0 else "",x["addr"] if i==0 else "",x["phone"] if i==0 else "",email,role,site if i==0 else "",sl if i==0 else "",date_s if i==0 else ""]);rows+=1
        messagebox.showinfo("✓",f"{self.L('export_ok')}\n{fname}\n\n{rows} lignes")

if __name__=="__main__":
    App().mainloop()
