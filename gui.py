import math, threading, time, os, csv, re
from datetime import datetime
from tkinter import ttk, messagebox, scrolledtext
import tkinter as tk

# ── Palette ───────────────────────────────────────────────────────────────────
R = "#E8192C"   # Silence red
RH= "#C41424"   # red hover
RL= "#FFF1F2"   # red light bg
W = "#FFFFFF"   # white
G1= "#F8F8FA"   # lightest surface
G2= "#F1F1F5"   # input bg
G3= "#E4E4EB"   # border
G4= "#C4C4D0"   # border strong
T1= "#111118"   # primary text
T2= "#555566"   # secondary text
T3= "#9999AA"   # muted text
GN= "#16A34A"   # green
GL= "#F0FDF4"   # green light
AM= "#D97706"   # amber
AL= "#FFFBEB"   # amber light

FONT      = "Segoe UI"
FONT_MONO = "Consolas"

class App(tk.Tk):
    def __init__(self, STRINGS, EXCL_DEFAULT, scrape_page, enrich_dealer,
                 norm, EMAIL_RE, T_dict=None):
        super().__init__()
        self._SP  = scrape_page
        self._ED  = enrich_dealer
        self._NRM = norm
        self.lang = "FR"
        self.S    = STRINGS
        self.results = []
        self._run    = False
        self._paused = False
        self._pause_ev = threading.Event()
        self._pause_ev.set()
        self.excl      = list(EXCL_DEFAULT)
        self.delay     = tk.DoubleVar(value=0.8)
        self.timeout_v = tk.IntVar(value=18)
        self.retries_v = tk.IntVar(value=3)
        self.inc_no    = tk.BooleanVar(value=True)
        self.open_csv  = tk.BooleanVar(value=False)
        self._anim_id  = None
        self._tick     = 0

        self.configure(bg=W)
        self.title("Silence.eco — Dealer Finder")
        self.geometry("1140x780")
        self.minsize(920, 640)

        self._build_styles()
        self._build_header()
        self._build_nb()
        self._apply_lang()

    def L(self, k): return self.S[self.lang].get(k, k)

    # ── Styles ─────────────────────────────────────────────────────────────
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TNotebook", background=W, borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab", background=W, foreground=T3,
                    padding=[22, 11], font=(FONT, 10), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", W)],
              foreground=[("selected", T1)])

        s.configure("TFrame", background=W)
        s.configure("G1.TFrame", background=G1)

        s.configure("Red.Horizontal.TProgressbar",
                    troughcolor=G3, background=R,
                    borderwidth=0, thickness=3)

        s.configure("Treeview",
                    background=W, fieldbackground=W,
                    foreground=T1, rowheight=34,
                    font=(FONT, 9), borderwidth=0)
        s.configure("Treeview.Heading",
                    background=G1, foreground=T2,
                    font=(FONT, 8, "bold"),
                    relief="flat", padding=[10, 7])
        s.map("Treeview",
              background=[("selected", RL)],
              foreground=[("selected", R)])

    # ── Header ─────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=W)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=R, height=3).pack(fill="x")

        nav = tk.Frame(hdr, bg=W)
        nav.pack(fill="x", padx=32, pady=16)

        # Logo
        lo = tk.Frame(nav, bg=W)
        lo.pack(side="left")
        cv = tk.Canvas(lo, width=42, height=42, bg=W, highlightthickness=0)
        cv.pack(side="left", padx=(0, 14))
        cx, cy, r = 21, 21, 19
        pts = sum([[cx+r*math.cos(math.pi/2+i*math.pi/3),
                    cy+r*math.sin(math.pi/2+i*math.pi/3)] for i in range(6)], [])
        cv.create_polygon(pts, fill=R, outline="")
        r2 = 11
        pts2 = sum([[cx+r2*math.cos(math.pi/2+i*math.pi/3),
                     cy+r2*math.sin(math.pi/2+i*math.pi/3)] for i in range(6)], [])
        cv.create_polygon(pts2, fill=W, outline="")
        cv.create_oval(cx-5, cy-5, cx+5, cy+5, fill=R, outline="")

        nm = tk.Frame(lo, bg=W)
        nm.pack(side="left")
        tk.Label(nm, text="SILENCE", bg=W, fg=T1,
                 font=(FONT, 17, "bold")).pack(anchor="w")
        tk.Label(nm, text="ECO", bg=W, fg=R,
                 font=(FONT, 7, "bold")).pack(anchor="w")

        tk.Frame(nav, bg=G3, width=1).pack(side="left", fill="y", padx=22)

        sub = tk.Frame(nav, bg=W)
        sub.pack(side="left")
        tk.Label(sub, text="Dealer Finder", bg=W, fg=T1,
                 font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(sub, text="Extraction  ·  Validation  ·  Enrichissement",
                 bg=W, fg=T3, font=(FONT, 8)).pack(anchor="w")

        # Right
        rt = tk.Frame(nav, bg=W)
        rt.pack(side="right")
        self._status_lbl = tk.Label(rt, text="", bg=W, fg=T3, font=(FONT, 9))
        self._status_lbl.pack(side="left", padx=(0, 24))

        for code in ("FR", "ES", "EN"):
            b = tk.Button(rt, text=code,
                          bg=G1, fg=T2,
                          font=(FONT, 8, "bold"),
                          relief="flat", bd=0, width=3,
                          cursor="hand2", pady=5,
                          activebackground=R,
                          activeforeground=W,
                          command=lambda c=code: self._switch(c))
            b.pack(side="left", padx=1)

        tk.Frame(hdr, bg=G3, height=1).pack(fill="x")

    # ── Notebook ───────────────────────────────────────────────────────────
    def _build_nb(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self._nb = nb
        self._f1 = ttk.Frame(nb); self._f2 = ttk.Frame(nb); self._f3 = ttk.Frame(nb)
        nb.add(self._f1, text=""); nb.add(self._f2, text=""); nb.add(self._f3, text="")
        self._build_t1()
        self._build_t2()
        self._build_t3()

    # ── Tab 1: Extraction ──────────────────────────────────────────────────
    def _build_t1(self):
        f = self._f1
        P = dict(padx=32)

        # URL row
        self._lbl_url = tk.Label(f, text="", bg=W, fg=T2,
                                  font=(FONT, 8, "bold"))
        self._lbl_url.pack(anchor="w", padx=32, pady=(24, 8))

        row = tk.Frame(f, bg=W)
        row.pack(fill="x", **P)

        # Input field — clean with bottom border only
        ef = tk.Frame(row, bg=G2, highlightthickness=1,
                      highlightbackground=G3, highlightcolor=R)
        ef.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._url = tk.StringVar(
            value="https://www.aixam.com/fr/reseau/voiture-sans-permis-france")
        self._url_entry = tk.Entry(
            ef, textvariable=self._url,
            font=(FONT, 10), bg=G2, fg=T1,
            insertbackground=R, relief="flat", bd=0,
            highlightthickness=0)
        self._url_entry.pack(fill="x", padx=14, pady=10)

        # Extract button
        self._btn = tk.Button(
            row, text="",
            bg=R, fg=W, font=(FONT, 10, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=26, pady=11,
            activebackground=RH, activeforeground=W,
            command=self._start)
        self._btn.pack(side="left")

        # Pause button
        self._pause_btn = tk.Button(
            row, text="⏸",
            bg=G1, fg=T2, font=(FONT, 11),
            relief="flat", bd=0, cursor="hand2",
            padx=13, pady=11, state="disabled",
            activebackground=AL,
            command=self._toggle_pause)
        self._pause_btn.pack(side="left", padx=(8, 0))

        # Options
        opt = tk.Frame(f, bg=W)
        opt.pack(fill="x", **P, pady=(14, 0))
        self._v1 = tk.BooleanVar(value=True)
        self._v2 = tk.BooleanVar(value=True)
        self._v3 = tk.BooleanVar(value=True)
        for v, a in [(self._v1,"_c1"),(self._v2,"_c2"),(self._v3,"_c3")]:
            c = tk.Checkbutton(opt, text="", variable=v,
                               bg=W, fg=T1, font=(FONT, 9),
                               activebackground=W, selectcolor=W,
                               cursor="hand2", highlightthickness=0)
            c.pack(side="left", padx=(0, 26))
            setattr(self, a, c)

        # Status pills
        pills = tk.Frame(f, bg=W)
        pills.pack(fill="x", **P, pady=(12, 0))

        hp = tk.Frame(pills, bg=GL, padx=10, pady=5)
        hp.pack(side="left", padx=(0, 8))
        self._hunter_dot = tk.Canvas(hp, width=7, height=7, bg=GL,
                                      highlightthickness=0)
        self._hunter_dot.pack(side="left", padx=(0, 5))
        self._hunter_dot.create_oval(0, 0, 7, 7, fill=GN, outline="")
        tk.Label(hp, text="Hunter.io actif", bg=GL, fg=GN,
                 font=(FONT, 8, "bold")).pack(side="left")

        self._pause_pill = tk.Frame(pills, bg=AL, padx=10, pady=5)
        tk.Label(self._pause_pill, text="⏸  En pause",
                 bg=AL, fg=AM, font=(FONT, 8, "bold")).pack()

        # Progress block
        pg = tk.Frame(f, bg=W)
        pg.pack(fill="x", **P, pady=(18, 0))

        pgr = tk.Frame(pg, bg=W)
        pgr.pack(fill="x", pady=(0, 8))

        # Animated indicator
        self._ind = tk.Canvas(pgr, width=10, height=10, bg=W,
                               highlightthickness=0)
        self._ind.pack(side="left", padx=(0, 10))
        self._ind.create_oval(1, 1, 9, 9, fill=G2, outline="", tags="dot")

        self._prog_lbl = tk.Label(pgr, text="", bg=W, fg=T1,
                                   font=(FONT, 9, "bold"))
        self._prog_lbl.pack(side="left")
        self._pct_lbl = tk.Label(pgr, text="", bg=W, fg=T3,
                                  font=(FONT, 9))
        self._pct_lbl.pack(side="right")

        # Live email counter
        self._em_frame = tk.Frame(pg, bg=RL, padx=12, pady=6)
        self._em_lbl = tk.Label(self._em_frame,
                                 text="0 emails trouvés",
                                 bg=RL, fg=R,
                                 font=(FONT, 8, "bold"))
        self._em_lbl.pack()

        # Annuaire.gouv check indicator
        self._gouv_frame = tk.Frame(pg, bg=GL, padx=12, pady=6)
        self._gouv_frame.pack(fill="x", pady=(4, 0))
        self._gouv_frame.pack_forget()
        tk.Label(self._gouv_frame,
                 text="✓  Vérification annuaire-entreprises.data.gouv.fr",
                 bg=GL, fg=GN, font=(FONT, 8)).pack()

        self._prog_var = tk.DoubleVar()
        ttk.Progressbar(pg, variable=self._prog_var, maximum=100,
                        style="Red.Horizontal.TProgressbar").pack(
                        fill="x", pady=(6, 0))

        # Log
        lf = tk.Frame(f, bg=W)
        lf.pack(fill="both", expand=True, **P, pady=(18, 0))

        lh = tk.Frame(lf, bg=W)
        lh.pack(fill="x", pady=(0, 6))
        self._log_hdr = tk.Label(lh, text="", bg=W, fg=T2,
                                  font=(FONT, 8, "bold"))
        self._log_hdr.pack(side="left")

        lw = tk.Frame(lf, bg=G1, highlightthickness=1,
                      highlightbackground=G3)
        lw.pack(fill="both", expand=True)
        self._log = scrolledtext.ScrolledText(
            lw, height=7, font=(FONT_MONO, 8),
            bg=G1, fg=T2, insertbackground=R,
            relief="flat", bd=0, state="disabled",
            wrap="word", highlightthickness=0,
            padx=16, pady=10)
        self._log.pack(fill="both", expand=True)

        # Log colors
        self._log.tag_configure("ok",   foreground=GN, font=(FONT_MONO, 8, "bold"))
        self._log.tag_configure("fail", foreground="#DC2626")
        self._log.tag_configure("info", foreground="#2563EB")
        self._log.tag_configure("head", foreground=T1, font=(FONT_MONO, 8, "bold"))
        self._log.tag_configure("dim",  foreground=T3)

        # Stats cards
        sf = tk.Frame(f, bg=W)
        sf.pack(fill="x", **P, pady=(14, 26))
        self._sv = {}; self._slbl = {}
        cards = [
            ("s1", T1, W,   G3),
            ("s2", R,  RL,  R),
            ("s3", GN, GL,  GN),
            ("s4", T1, W,   G3),
        ]
        for i, (k, vc, bg, ac) in enumerate(cards):
            card = tk.Frame(sf, bg=bg,
                            highlightthickness=1,
                            highlightbackground=ac if k == "s2" else G3,
                            padx=18, pady=14)
            card.pack(side="left", fill="x", expand=True,
                      padx=(0, 10) if i < 3 else 0)
            lbl = tk.Label(card, text="", bg=bg, fg=T3,
                           font=(FONT, 8))
            lbl.pack(anchor="w")
            v = tk.StringVar(value="—")
            tk.Label(card, textvariable=v, bg=bg, fg=vc,
                     font=(FONT, 26, "bold")).pack(anchor="w")
            self._sv[k] = v; self._slbl[k] = lbl

    # ── Tab 2: Results ─────────────────────────────────────────────────────
    def _build_t2(self):
        f = self._f2

        top = tk.Frame(f, bg=W)
        top.pack(fill="x", padx=24, pady=(16, 8))
        self._meta = tk.Label(top, text="", bg=W, fg=T3, font=(FONT, 9))
        self._meta.pack(side="left")

        self._btn_csv = tk.Button(top, text="",
                                   bg=R, fg=W, font=(FONT, 9, "bold"),
                                   relief="flat", bd=0, cursor="hand2",
                                   padx=18, pady=7,
                                   activebackground=RH,
                                   command=self._export)
        self._btn_csv.pack(side="right")

        self._btn_copy = tk.Button(top, text="",
                                    bg=W, fg=T1, font=(FONT, 9),
                                    relief="flat", bd=0, cursor="hand2",
                                    padx=14, pady=7,
                                    highlightthickness=1,
                                    highlightbackground=G3,
                                    command=self._copy)
        self._btn_copy.pack(side="right", padx=(0, 10))

        # Table
        tw = tk.Frame(f, bg=W, highlightthickness=1,
                      highlightbackground=G3)
        tw.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        cols = ("num","name","addr","phone","email","role","src")
        self._tree = ttk.Treeview(tw, columns=cols,
                                   show="headings", selectmode="browse")
        for col, w in [("num",38),("name",195),("addr",148),
                       ("phone",98),("email",185),("role",142),("src",90)]:
            self._tree.column(col, width=w, minwidth=28)

        vsb = ttk.Scrollbar(tw, orient="vertical",
                             command=self._tree.yview)
        hsb = ttk.Scrollbar(tw, orient="horizontal",
                             command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        self._tree.tag_configure("miss",   background="#FFF5F5")
        self._tree.tag_configure("web",    background="#FFFBEB")
        self._tree.tag_configure("hunter", background="#F0FDF4")

    # ── Tab 3: Settings ────────────────────────────────────────────────────
    def _build_t3(self):
        f = self._f3
        cv = tk.Canvas(f, bg=W, highlightthickness=0)
        sb = ttk.Scrollbar(f, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)
        inner = tk.Frame(cv, bg=W)
        win = cv.create_window((0, 0), window=inner, anchor="nw")
        def _r(e):
            cv.configure(scrollregion=cv.bbox("all"))
            cv.itemconfig(win, width=e.width)
        cv.bind("<Configure>", _r)

        def sec(title, subtitle=""):
            fr = tk.Frame(inner, bg=W)
            fr.pack(fill="x", padx=32, pady=(28, 0))
            tk.Label(fr, text=title, bg=W, fg=T1,
                     font=(FONT, 10, "bold")).pack(anchor="w")
            if subtitle:
                tk.Label(fr, text=subtitle, bg=W, fg=T3,
                         font=(FONT, 8)).pack(anchor="w", pady=(2, 0))
            tk.Frame(fr, bg=G3, height=1).pack(fill="x", pady=(8, 14))
            return fr

        def spin_row(parent, label, hint, var, frm, to, step=1):
            r = tk.Frame(parent, bg=W)
            r.pack(fill="x", padx=4, pady=6)
            lf = tk.Frame(r, bg=W)
            lf.pack(side="left", fill="x", expand=True)
            tk.Label(lf, text=label, bg=W, fg=T1,
                     font=(FONT, 9)).pack(anchor="w")
            if hint:
                tk.Label(lf, text=hint, bg=W, fg=T3,
                         font=(FONT, 8)).pack(anchor="w")
            sw = tk.Frame(r, bg=G3, padx=1, pady=1)
            sw.pack(side="right")
            sp = tk.Spinbox(sw, textvariable=var,
                            from_=frm, to=to, increment=step,
                            width=7, font=(FONT, 9),
                            bg=G2, fg=T1, relief="flat", bd=0,
                            insertbackground=R, highlightthickness=0)
            sp.pack(ipady=6, padx=6)

        s1 = sec("Recherche",
                 "Paramètres de vitesse et de robustesse de l'extraction")
        spin_row(s1, "Délai entre requêtes (s)",
                 "Augmenter si le site bloque (recommandé: 0.8–2s)",
                 self.delay, 0.3, 10, 0.1)
        spin_row(s1, "Timeout connexion (s)",
                 "Temps max d'attente par page (recommandé: 15–25s)",
                 self.timeout_v, 5, 60, 1)
        spin_row(s1, "Tentatives en cas d'erreur",
                 "Nombre de réessais si une page ne répond pas",
                 self.retries_v, 1, 6, 1)

        s2 = sec("Filtres",
                 "Domaines à ignorer lors de la recherche d'emails")
        tk.Label(s2, text=self.L("p_excl"), bg=W, fg=T1,
                 font=(FONT, 9)).pack(anchor="w", padx=4)
        tk.Label(s2, text=self.L("p_excl_desc"), bg=W, fg=T3,
                 font=(FONT, 8)).pack(anchor="w", padx=4, pady=(2, 8))
        tw2 = tk.Frame(s2, bg=G3, padx=1, pady=1)
        tw2.pack(fill="x", padx=4)
        self._excl_txt = tk.Text(tw2, height=8,
                                  font=(FONT_MONO, 8),
                                  bg=G2, fg=T1, insertbackground=R,
                                  relief="flat", bd=0,
                                  highlightthickness=0,
                                  padx=12, pady=8)
        self._excl_txt.pack(fill="x")
        self._excl_txt.insert("1.0", "\n".join(self.excl))

        s3 = sec("Export")
        self._ck_no = tk.Checkbutton(s3,
            text=self.L("p_include_no_email"),
            variable=self.inc_no,
            bg=W, fg=T1, font=(FONT, 9),
            activebackground=W, selectcolor=W, cursor="hand2")
        self._ck_no.pack(anchor="w", padx=4, pady=2)
        self._ck_open = tk.Checkbutton(s3,
            text=self.L("p_open_csv"),
            variable=self.open_csv,
            bg=W, fg=T1, font=(FONT, 9),
            activebackground=W, selectcolor=W, cursor="hand2")
        self._ck_open.pack(anchor="w", padx=4, pady=2)

        br = tk.Frame(inner, bg=W)
        br.pack(fill="x", padx=32, pady=22)
        self._btn_save = tk.Button(br, text="",
            bg=R, fg=W, font=(FONT, 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=18, pady=9,
            activebackground=RH, command=self._save)
        self._btn_save.pack(side="left")
        self._btn_rst = tk.Button(br, text="",
            bg=W, fg=T2, font=(FONT, 9),
            relief="flat", bd=0, cursor="hand2",
            padx=14, pady=9,
            highlightthickness=1, highlightbackground=G3,
            command=self._reset)
        self._btn_rst.pack(side="left", padx=(10, 0))

    # ── Language ───────────────────────────────────────────────────────────
    def _switch(self, lang): self.lang = lang; self._apply_lang()

    def _apply_lang(self):
        L = self.L
        self.title(L("title"))
        self._nb.tab(0, text=f"  {L('tab1')}  ")
        self._nb.tab(1, text=f"  {L('tab2')}  ")
        self._nb.tab(2, text=f"  {L('tab3')}  ")
        self._lbl_url.configure(text=L("url_label"))
        self._btn.configure(
            text=L("btn_run") if (self._run and not self._paused)
            else L("btn_go") if not self._run else L("btn_again"))
        self._c1.configure(text=L("opt1"))
        self._c2.configure(text=L("opt2"))
        self._c3.configure(text=L("opt3"))
        self._log_hdr.configure(text=L("log_lbl"))
        for k, tk_k in [("s1","stat1"),("s2","stat2"),
                         ("s3","stat3"),("s4","stat4")]:
            self._slbl[k].configure(text=L(tk_k))
        rl = {"FR":"Rôle","ES":"Rol","EN":"Role"}.get(self.lang, "Rôle")
        for col, key in [("num","col_num"),("name","col_name"),
                         ("addr","col_addr"),("phone","col_phone"),
                         ("email","col_email"),("src","col_src")]:
            self._tree.heading(col, text=L(key))
        self._tree.heading("role", text=rl)
        self._btn_copy.configure(text=L("btn_copy"))
        self._btn_csv.configure(text=L("btn_csv"))
        self._btn_save.configure(text=L("btn_save"))
        self._btn_rst.configure(text=L("btn_reset"))
        self._ck_no.configure(text=L("p_include_no_email"))
        self._ck_open.configure(text=L("p_open_csv"))
        self._status_lbl.configure(text=L("ready"))
        if self.results: self._render()

    # ── Animation ──────────────────────────────────────────────────────────
    def _start_anim(self):
        self._tick = 0
        self._em_frame.pack(fill="x", pady=(6, 0))
        self._anim_loop()

    def _stop_anim(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        try:
            self._ind.itemconfig("dot", fill=GN)
            self._em_frame.pack_forget()
        except Exception:
            pass

    def _anim_loop(self):
        if not self._run: return
        self._tick += 1
        t = self._tick * 0.22
        v = int(60 + 45 * math.sin(t))
        if self._paused:
            fill = AM
        else:
            fill = f"#{232:02x}{v:02x}{44:02x}"
        try:
            self._ind.itemconfig("dot", fill=fill)
            count = sum(len(d.get("emails", {})) for d in self.results)
            self._em_lbl.configure(
                text=f"{count} email{'s' if count!=1 else ''} trouvé{'s' if count!=1 else ''}")
        except Exception:
            pass
        self._anim_id = self.after(70, self._anim_loop)

    # ── Pause ──────────────────────────────────────────────────────────────
    def _toggle_pause(self):
        if not self._run: return
        self._paused = not self._paused
        if self._paused:
            self._pause_ev.clear()
            self._pause_btn.configure(text="▶", bg=AL, fg=AM)
            self._pause_pill.pack(side="left")
            self._prog_lbl.configure(text="En pause…")
            self._log_add("⏸  Extraction en pause — cliquez ▶ pour reprendre", "head")
        else:
            self._pause_ev.set()
            self._pause_btn.configure(text="⏸", bg=G1, fg=T2)
            self._pause_pill.pack_forget()
            self._log_add("▶  Reprise de l'extraction…", "ok")

    # ── Log ────────────────────────────────────────────────────────────────
    def _log_add(self, msg, force_tag=None):
        self._log.configure(state="normal")
        if force_tag:
            tag = force_tag
        elif any(x in msg for x in ("✅","✔","✓","━━","email(s)")):
            tag = "ok"
        elif any(x in msg for x in ("✗","ERREUR","rejeté","⚠")):
            tag = "fail"
        elif any(x in msg for x in ("🔍","🗺","💡","Hunter","1/3","2/3","3/3","gouv")):
            tag = "info"
        elif msg.startswith(("┌","└","━","─")):
            tag = "head"
        else:
            tag = "dim"
        self._log.insert("end", f"{msg}\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_prog(self, pct, lbl=""):
        self._prog_var.set(pct)
        if lbl:
            self._prog_lbl.configure(text=lbl)
            self._pct_lbl.configure(text=f"{int(pct)}%" if pct else "")
        self.update_idletasks()

    # ── Save / Reset ───────────────────────────────────────────────────────
    def _save(self):
        raw = self._excl_txt.get("1.0", "end").strip()
        self.excl = [l.strip().lstrip("@")
                     for l in raw.splitlines() if l.strip()]
        messagebox.showinfo("Silence", self.L("info_saved"))

    def _reset(self):
        from app import EXCL_DEFAULT
        self.excl = list(EXCL_DEFAULT)
        self._excl_txt.delete("1.0", "end")
        self._excl_txt.insert("1.0", "\n".join(self.excl))
        self.delay.set(0.8); self.timeout_v.set(18)
        self.retries_v.set(3); self.inc_no.set(True)
        self.open_csv.set(False)
        messagebox.showinfo("Silence", self.L("info_reset"))

    # ── Start / Worker ─────────────────────────────────────────────────────
    def _start(self):
        if self._run:
            if self._paused: self._toggle_pause()
            return
        url = self._url.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("", self.L("err_url")); return
        self._run = True; self._paused = False; self._pause_ev.set()
        self._btn.configure(state="disabled", text=self.L("btn_run"))
        self._pause_btn.configure(state="normal")
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        self._set_prog(0, "Démarrage…")
        self._pct_lbl.configure(text="")
        for v in self._sv.values(): v.set("—")
        self._gouv_frame.pack_forget()
        self._start_anim()
        excl = self.excl if self._v3.get() else []
        threading.Thread(target=self._worker, args=(url, excl),
                         daemon=True).start()

    def _worker(self, url, excl):
        try:
            to = self.timeout_v.get()
            rt = self.retries_v.get()
            dly = self.delay.get()

            dealers = self._SP(url, excl, self._log_add,
                               self._set_prog, timeout=to, retries=rt)
            self._set_prog(44, "Enrichissement des emails…")

            if self._v1.get():
                no_em  = sum(1 for d in dealers if not d["emails"])
                has_em = len(dealers) - no_em
                self._log_add(
                    f"━━  {len(dealers)} concessionnaires  ·  "
                    f"{has_em} avec email  ·  {no_em} à enrichir  ━━", "head")

                # Show gouv indicator
                self.after(0, self._gouv_frame.pack,
                           {"fill":"x","pady":(4,0)})

                lock = threading.Lock()
                done = [0]

                def do_one(d):
                    self._pause_ev.wait()
                    try:
                        em, src = self._ED(d, excl, self._log_add,
                                           delay=dly, timeout=to)
                        if em: d["emails"] = em; d["src"] = src
                    except Exception as e:
                        self._log_add(f"  ⚠  {d['name'][:30]}: {e}")
                    finally:
                        with lock:
                            done[0] += 1
                            pct = 44 + int(50 * done[0] /
                                           max(len(dealers), 1))
                            self._set_prog(
                                pct,
                                f"{done[0]}/{len(dealers)}"
                                f"  —  {d['name'][:32]}")

                threads = []
                for d in dealers:
                    self._pause_ev.wait()
                    t = threading.Thread(target=do_one, args=(d,),
                                         daemon=True)
                    threads.append(t); t.start()
                    while sum(1 for x in threads if x.is_alive()) >= 4:
                        time.sleep(0.3)
                for t in threads: t.join(timeout=40)

            if self._v2.get():
                seen, uniq = set(), []
                for d in dealers:
                    k = self._NRM(d["name"])[:20]
                    if k not in seen: seen.add(k); uniq.append(d)
                dealers = uniq

            total = sum(len(d["emails"]) for d in dealers)
            self._set_prog(100, "Extraction terminée ✓")
            self._log_add(
                f"━━  {len(dealers)} concessionnaires  ·  "
                f"{total} emails validés  ━━", "head")
            self.results = dealers
            self.after(0, self._finish)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
            self._log_add(f"✗  Erreur critique : {e}", "fail")
            self.after(0, lambda: (
                self._btn.configure(state="normal",
                                    text=self.L("btn_go")),
                self._pause_btn.configure(state="disabled")
            ))
            self._run = False
            self._stop_anim()

    def _finish(self):
        self._run = False; self._paused = False
        self._stop_anim()
        self._pause_btn.configure(state="disabled", text="⏸",
                                   bg=G1, fg=T2)
        self._pause_pill.pack_forget()
        d = self.results
        em = sum(len(x["emails"]) for x in d)
        wb = sum(1 for x in d if x["src"] in ("web","hunter"))
        ad = sum(1 for x in d if x["addr"])
        self._sv["s1"].set(str(len(d))); self._sv["s2"].set(str(em))
        self._sv["s3"].set(str(wb));     self._sv["s4"].set(str(ad))
        self._btn.configure(state="normal", text=self.L("btn_again"))
        self._status_lbl.configure(
            text=self.L("last") + datetime.now().strftime("%H:%M"))
        self._render()
        self._nb.select(self._f2)

    def _render(self):
        d = self.results
        em = sum(len(x["emails"]) for x in d)
        ad = sum(1 for x in d if x["addr"])
        sm = {"page": self.L("src_page"),
              "web":  self.L("src_web"),
              "hunter": self.L("src_hunter")}
        self._meta.configure(
            text=f"{len(d)} {self.L('stat1')}  ·  "
                 f"{em} {self.L('stat2')}  ·  "
                 f"{ad} {self.L('stat4')}")
        for r in self._tree.get_children():
            self._tree.delete(r)
        n = 1
        for x in d:
            sl = sm.get(x["src"], "—")
            if not x["emails"]:
                self._tree.insert("", "end", tags=("miss",), values=(
                    n, x["name"], x["addr"], x["phone"], "—", "—", sl))
                n += 1
            else:
                for i, (email, role) in enumerate(
                        sorted(x["emails"].items())):
                    tag = {"page":"","web":"web",
                           "hunter":"hunter"}.get(x["src"], "")
                    self._tree.insert("", "end", tags=(tag,), values=(
                        n  if i==0 else "",
                        x["name"]  if i==0 else "",
                        x["addr"]  if i==0 else "",
                        x["phone"] if i==0 else "",
                        email, role,
                        sl if i==0 else ""))
                n += 1

    def _copy(self):
        em = sorted({e for x in self.results for e in x["emails"]})
        if not em:
            messagebox.showinfo("", self.L("no_copy")); return
        self.clipboard_clear()
        self.clipboard_append("\n".join(em))
        messagebox.showinfo("✓", f"{len(em)} {self.L('copied')}")

    def _export(self):
        if not self.results:
            messagebox.showinfo("", self.L("no_copy")); return
        desk = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desk, exist_ok=True)
        fname = f"silence_dealers_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        fpath = os.path.join(desk, fname)
        sm = {"page": self.L("src_page"),
              "web":  self.L("src_web"),
              "hunter": self.L("src_hunter")}
        date_s = datetime.now().strftime("%d/%m/%Y"); rows = 0
        with open(fpath, "w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp)
            w.writerow([self.L("col_name"), self.L("col_addr"),
                        self.L("col_phone"), self.L("col_email"),
                        self.L("col_role"), "Site web",
                        self.L("col_src"), "Date"])
            for x in self.results:
                if not x["emails"] and not self.inc_no.get(): continue
                sl = sm.get(x["src"], "—")
                site = x.get("website", "")
                if not x["emails"]:
                    w.writerow([x["name"],x["addr"],x["phone"],
                                "","",site,sl,date_s]); rows += 1
                else:
                    for i,(email,role) in enumerate(
                            sorted(x["emails"].items())):
                        w.writerow([
                            x["name"]  if i==0 else "",
                            x["addr"]  if i==0 else "",
                            x["phone"] if i==0 else "",
                            email, role,
                            site       if i==0 else "",
                            sl         if i==0 else "",
                            date_s     if i==0 else ""])
                        rows += 1
        messagebox.showinfo(
            "✓", f"{self.L('export_ok')}\n{fname}\n\n{rows} lignes")
        if self.open_csv.get():
            try: os.startfile(fpath)
            except Exception:
                try: os.system(f'open "{fpath}"')
                except Exception: pass
