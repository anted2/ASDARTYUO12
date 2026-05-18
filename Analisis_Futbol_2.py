# ╔══════════════════════════════════════════════════════════════╗
# ║   ⚽  ANÁLISIS DE FÚTBOL — Streamlit App (Analisis_Futbol_2) ║
# ║   Uso: streamlit run Analisis_Futbol_2.py                   ║
# ╚══════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
import plotly.graph_objects as go
warnings.filterwarnings("ignore")



# ─── CONFIGURACIÓN DE PÁGINA ───────────────────────────────
st.set_page_config(
    page_title="⚽ Análisis de Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .main { background-color: #0d1117; }
  .block-container { padding-top: 1rem; }
  .stSelectbox label, .stSlider label { color: #ccc !important; }
  h1, h2, h3 { color: #00e676 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SIDEBAR — Configuración
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚽ Análisis de Fútbol")
    st.markdown("---")

    FOLDER = st.text_input(
        "📁 Carpeta de datos",
        value="/content/drive/MyDrive/Colab Notebooks/Futbool/Premier"
    )

    if not os.path.exists(FOLDER):
        st.error("❌ Carpeta no encontrada")
        st.stop()

    archivos_csv = sorted([f for f in os.listdir(FOLDER) if f.endswith('.csv')])
    if not archivos_csv:
        st.error("❌ No hay archivos CSV en la carpeta")
        st.stop()

    archivo = st.selectbox("📄 Selecciona la liga", archivos_csv)
    DATA_PATH = os.path.join(FOLDER, archivo)
    liga_nombre = archivo.replace('.csv','').replace('_',' ').title()

    st.markdown("---")
    UMBRAL_PTS = st.slider("🎯 Umbral puntos (contexto)", 5, 15, 10)
    st.markdown("---")
    st.caption("v5 · Premier / La Liga / Serie A / Liga MX")

# ═══════════════════════════════════════════════════════════
# CARGA Y PROCESAMIENTO (cacheado)
# ═══════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⚙️ Procesando datos...")
def procesar(path):
    df_raw = pd.read_csv(path, encoding="utf-8", sep=None, engine='python')

    FORMATO_NUEVO = "HomeTeam" in df_raw.columns
    FORMATO_VIEJO = "home" in df_raw.columns
    if not FORMATO_NUEVO and not FORMATO_VIEJO:
        return None, None, None, None

    def normalizar(df, es_nuevo):
        out = pd.DataFrame()
        if es_nuevo:
            out["fecha"]                 = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
            out["home"]                  = df["HomeTeam"]
            out["away"]                  = df["AwayTeam"]
            out["home_goals"]            = pd.to_numeric(df["FTHG"], errors="coerce")
            out["away_goals"]            = pd.to_numeric(df["FTAG"], errors="coerce")
            out["home_total_shots"]      = pd.to_numeric(df.get("HS",  pd.Series(dtype=float)), errors="coerce")
            out["away_total_shots"]      = pd.to_numeric(df.get("AS",  pd.Series(dtype=float)), errors="coerce")
            out["home_shots_on_target"]  = pd.to_numeric(df.get("HST", pd.Series(dtype=float)), errors="coerce")
            out["away_shots_on_target"]  = pd.to_numeric(df.get("AST", pd.Series(dtype=float)), errors="coerce")
            out["home_corner_kicks"]     = pd.to_numeric(df.get("HC",  pd.Series(dtype=float)), errors="coerce")
            out["away_corner_kicks"]     = pd.to_numeric(df.get("AC",  pd.Series(dtype=float)), errors="coerce")
            out["home_fouls"]            = pd.to_numeric(df.get("HF",  pd.Series(dtype=float)), errors="coerce")
            out["away_fouls"]            = pd.to_numeric(df.get("AF",  pd.Series(dtype=float)), errors="coerce")
            out["home_yellow_cards"]     = pd.to_numeric(df.get("HY",  pd.Series(dtype=float)), errors="coerce")
            out["away_yellow_cards"]     = pd.to_numeric(df.get("AY",  pd.Series(dtype=float)), errors="coerce")
            out["home_red_cards"]        = pd.to_numeric(df.get("HR",  pd.Series(dtype=float)), errors="coerce")
            out["away_red_cards"]        = pd.to_numeric(df.get("AR",  pd.Series(dtype=float)), errors="coerce")
            out["home_expected_goals"]   = np.nan
            out["away_expected_goals"]   = np.nan
            out["home_goalkeeper_saves"] = pd.to_numeric(df.get("HGS", pd.Series(dtype=float)), errors="coerce")
            out["away_goalkeeper_saves"] = pd.to_numeric(df.get("AGS", pd.Series(dtype=float)), errors="coerce")
            for c in ["home_passes","away_passes","home_tackles","away_tackles",
                      "home_interceptions","away_interceptions"]:
                out[c] = np.nan
            out["odd_h"]   = pd.to_numeric(df.get("B365H",    pd.Series(dtype=float)), errors="coerce")
            out["odd_d"]   = pd.to_numeric(df.get("B365D",    pd.Series(dtype=float)), errors="coerce")
            out["odd_a"]   = pd.to_numeric(df.get("B365A",    pd.Series(dtype=float)), errors="coerce")
            out["odd_o25"] = pd.to_numeric(df.get("B365>2.5", pd.Series(dtype=float)), errors="coerce")
            out["odd_u25"] = pd.to_numeric(df.get("B365<2.5", pd.Series(dtype=float)), errors="coerce")
            out["ah_line"] = pd.to_numeric(df.get("AHh",      pd.Series(dtype=float)), errors="coerce")
        else:
            cols = ["fecha","home","away","home_goals","away_goals",
                    "home_expected_goals","away_expected_goals",
                    "home_total_shots","away_total_shots",
                    "home_shots_on_target","away_shots_on_target",
                    "home_corner_kicks","away_corner_kicks",
                    "home_fouls","away_fouls","home_yellow_cards","away_yellow_cards",
                    "home_red_cards","away_red_cards",
                    "home_goalkeeper_saves","away_goalkeeper_saves",
                    "home_tackles","away_tackles","home_passes","away_passes",
                    "home_interceptions","away_interceptions"]
            for c in cols:
                out[c] = df[c] if c in df.columns else np.nan
            if "fecha" in out.columns:
                out["fecha"] = pd.to_datetime(out["fecha"], dayfirst=True, errors="coerce")
            for c in ["odd_h","odd_d","odd_a","odd_o25","odd_u25","ah_line"]:
                out[c] = np.nan
        return out

    df = normalizar(df_raw, FORMATO_NUEVO)
    df = df.sort_values("fecha").reset_index(drop=True)
    df["HomeGK_Saves"] = df["home_goalkeeper_saves"]
    df["AwayGK_Saves"] = df["away_goalkeeper_saves"]

    # Atajadas inferidas si no hay reales
    if df["HomeGK_Saves"].isna().all():
        df["HomeGK_Saves"] = (pd.to_numeric(df["away_shots_on_target"], errors='coerce') -
                               pd.to_numeric(df["away_goals"], errors='coerce')).clip(lower=0)
        df["AwayGK_Saves"] = (pd.to_numeric(df["home_shots_on_target"], errors='coerce') -
                               pd.to_numeric(df["home_goals"], errors='coerce')).clip(lower=0)

    df["FTR"] = df.apply(
        lambda r: "H" if r["home_goals"] > r["away_goals"] else
                  ("A" if r["home_goals"] < r["away_goals"] else "D"), axis=1
    )

    # Temporadas Liga MX vs Europa
    es_liga_mx = "ronda" in df_raw.columns
    if es_liga_mx:
        df["season_start"] = df["fecha"].apply(
            lambda d: d.year * 10 + 1 if d.month <= 6 else d.year * 10 + 2
        )
    else:
        df["season_start"] = df["fecha"].apply(
            lambda d: d.year if d.month >= 7 else d.year - 1
        )

    # Tabla de posiciones
    def build_standings(sdf):
        records = {}
        for _, row in sdf.iterrows():
            ht, at = row["home"], row["away"]
            hg = int(row["home_goals"]) if pd.notna(row["home_goals"]) else 0
            ag = int(row["away_goals"]) if pd.notna(row["away_goals"]) else 0
            ftr = row["FTR"]
            for team in [ht, at]:
                if team not in records:
                    records[team] = dict(PJ=0, G=0, E=0, P=0, GF=0, GC=0, PTS=0)
            records[ht]["PJ"] += 1; records[at]["PJ"] += 1
            records[ht]["GF"] += hg; records[ht]["GC"] += ag
            records[at]["GF"] += ag; records[at]["GC"] += hg
            if ftr == "H":
                records[ht]["G"] += 1; records[ht]["PTS"] += 3; records[at]["P"] += 1
            elif ftr == "A":
                records[at]["G"] += 1; records[at]["PTS"] += 3; records[ht]["P"] += 1
            else:
                records[ht]["E"] += 1; records[ht]["PTS"] += 1
                records[at]["E"] += 1; records[at]["PTS"] += 1
        t = pd.DataFrame(records).T
        t["DG"] = t["GF"] - t["GC"]
        t = t.sort_values(["PTS", "DG", "GF"], ascending=False)
        t["Pos"] = range(1, len(t) + 1)
        return t[["Pos", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]]

    def standings_at_date(sdf, fecha_lim):
        sub = sdf[sdf["fecha"] < fecha_lim]
        return pd.DataFrame() if sub.empty else build_standings(sub)

    # Posiciones históricas
    h_pos = {}; a_pos = {}; h_pts = {}; a_pts = {}
    for season, s_df in df.groupby("season_start"):
        s_df_s = s_df.sort_values("fecha")
        for idx, row in s_df_s.iterrows():
            st_h = standings_at_date(s_df_s, row["fecha"])
            ht, at = row["home"], row["away"]
            if st_h.empty:
                h_pos[idx] = np.nan; a_pos[idx] = np.nan
                h_pts[idx] = np.nan; a_pts[idx] = np.nan
            else:
                h_pos[idx] = int(st_h.loc[ht, "Pos"]) if ht in st_h.index else np.nan
                a_pos[idx] = int(st_h.loc[at, "Pos"]) if at in st_h.index else np.nan
                h_pts[idx] = int(st_h.loc[ht, "PTS"]) if ht in st_h.index else np.nan
                a_pts[idx] = int(st_h.loc[at, "PTS"]) if at in st_h.index else np.nan

    df["hist_pos_home"] = pd.Series(h_pos)
    df["hist_pos_away"] = pd.Series(a_pos)
    df["hist_pts_home"] = pd.Series(h_pts)
    df["hist_pts_away"] = pd.Series(a_pts)

    standings = build_standings(df)
    flags = {
        "cuotas":   df["odd_h"].notna().sum() > 0,
        "corners":  df["home_corner_kicks"].notna().sum() > 0,
        "remates":  df["home_total_shots"].notna().sum() > 0,
        "atajadas": df["HomeGK_Saves"].notna().sum() > 0,
    }
    return df, standings, flags, es_liga_mx


df, standings, flags, es_liga_mx = procesar(DATA_PATH)

if df is None:
    st.error("❌ Formato CSV no reconocido")
    st.stop()

TIENE_CUOTAS   = flags["cuotas"]
TIENE_CORNERS  = flags["corners"]
TIENE_REMATES  = flags["remates"]
TIENE_ATAJADAS = flags["atajadas"]

# ═══════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ═══════════════════════════════════════════════════════════
tab_pos, tab_analisis, tab_stats = st.tabs([
    "🏆 Tabla de Posiciones",
    "🔍 Análisis de Partido",
    "📊 Stats de Liga"
])

# ───────────────────────────────────────────────────────────
# TAB 1 — TABLA DE POSICIONES
# ───────────────────────────────────────────────────────────
with tab_pos:
    st.header(f"🏆 {liga_nombre}")
    n_equipos = len(standings)

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Partidos totales", len(df))
    with c2: st.metric("Equipos", n_equipos)
    with c3:
        rango = f"{df['fecha'].min().strftime('%d/%m/%Y')} → {df['fecha'].max().strftime('%d/%m/%Y')}"
        st.metric("Rango de fechas", rango)

    st.markdown("---")

    sd = standings.copy().reset_index()
    sd.columns = ["Equipo", "Pos", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]
    sd = sd[["Pos", "Equipo", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]]
    sd["DG"] = sd["DG"].apply(lambda x: f"+{int(x)}" if x > 0 else str(int(x)))

    def color_pos(row):
        p = row["Pos"]
        if p <= 4:              return ["background-color:#0d2e0d"] * len(row)
        elif p <= 6:            return ["background-color:#0d1e3a"] * len(row)
        elif p >= n_equipos - 2: return ["background-color:#2e0d0d"] * len(row)
        return [""] * len(row)

    styled = sd.style.apply(color_pos, axis=1).hide(axis="index")
    st.dataframe(styled, use_container_width=True, height=min(650, n_equipos * 36 + 50))
    st.caption("🟢 Champions/Playoff   🔵 Europa   🔴 Descenso/playoff descenso")

# ───────────────────────────────────────────────────────────
# TAB 2 — ANÁLISIS DE PARTIDO
# ───────────────────────────────────────────────────────────
with tab_analisis:
    st.header("🔍 Análisis de Partido")

    equipos = list(standings.index)
    col_l, col_vs, col_v = st.columns([5, 1, 5])
    with col_l:
        HOME_TEAM = st.selectbox("🏠 Equipo LOCAL", equipos, key="sel_home")
    with col_vs:
        st.markdown("<br><h3 style='text-align:center;color:#555'>vs</h3>",
                    unsafe_allow_html=True)
    with col_v:
        away_opts = [e for e in equipos if e != HOME_TEAM]
        AWAY_TEAM = st.selectbox("✈️ Equipo VISITANTE", away_opts, key="sel_away")

    if not st.button("⚡ Analizar partido", type="primary", use_container_width=True):
        st.info("👆 Selecciona los equipos y pulsa Analizar")
        st.stop()

    # Contexto
    home_pts = int(standings.loc[HOME_TEAM, "PTS"])
    away_pts = int(standings.loc[AWAY_TEAM, "PTS"])
    home_pos_n = int(standings.loc[HOME_TEAM, "Pos"])
    away_pos_n = int(standings.loc[AWAY_TEAM, "Pos"])
    diff_pts = home_pts - away_pts

    if diff_pts >= UMBRAL_PTS:
        contexto = "FAVORITO"; ctx_color = "#4CAF50"; ctx_emoji = "⭐"
        ctx_txt = f"Local FAVORITO (+{diff_pts} pts)"
    elif diff_pts <= -UMBRAL_PTS:
        contexto = "UNDERDOG"; ctx_color = "#ef5350"; ctx_emoji = "💪"
        ctx_txt = f"Local UNDERDOG ({diff_pts} pts)"
    else:
        contexto = "REÑIDO"; ctx_color = "#FFC107"; ctx_emoji = "⚔️"
        ctx_txt = f"Partido REÑIDO ({diff_pts:+d} pts)"

    contexto_v = {"FAVORITO": "UNDERDOG", "UNDERDOG": "FAVORITO", "REÑIDO": "REÑIDO"}[contexto]

    # Header del partido
    c1, c2, c3 = st.columns([4, 2, 4])
    with c1:
        st.markdown(f"""
        <div style='text-align:center;background:#161b22;border-radius:10px;padding:16px'>
          <div style='font-size:22px;font-weight:bold;color:#eee'>🏠 {HOME_TEAM}</div>
          <div style='color:#888;font-size:13px'>#{home_pos_n} · {home_pts} pts</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='text-align:center;padding:16px 0'>
          <div style='font-size:26px;color:#555;font-weight:bold'>vs</div>
          <div style='color:{ctx_color};font-size:12px;font-weight:bold;margin-top:4px'>
              {ctx_emoji} {ctx_txt}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='text-align:center;background:#161b22;border-radius:10px;padding:16px'>
          <div style='font-size:22px;font-weight:bold;color:#eee'>✈️ {AWAY_TEAM}</div>
          <div style='color:#888;font-size:13px'>#{away_pos_n} · {away_pts} pts</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Funciones auxiliares ───────────────────────────────
    def swap_v(df_f):
        df_f = df_f.copy()
        pairs = [
            ("home","away"),("home_goals","away_goals"),
            ("home_expected_goals","away_expected_goals"),
            ("home_total_shots","away_total_shots"),
            ("home_shots_on_target","away_shots_on_target"),
            ("home_corner_kicks","away_corner_kicks"),
            ("home_fouls","away_fouls"),("home_yellow_cards","away_yellow_cards"),
            ("home_red_cards","away_red_cards"),
            ("home_goalkeeper_saves","away_goalkeeper_saves"),
            ("HomeGK_Saves","AwayGK_Saves"),
            ("home_passes","away_passes"),("home_tackles","away_tackles"),
            ("home_interceptions","away_interceptions"),
            ("odd_h","odd_a"),
            ("hist_pos_home","hist_pos_away"),("hist_pts_home","hist_pts_away"),
        ]
        for a, b in pairs:
            if a in df_f.columns and b in df_f.columns:
                df_f[a], df_f[b] = df_f[b].copy(), df_f[a].copy()
        df_f["FTR"] = df_f["FTR"].map({"H":"A","A":"H","D":"D"})
        return df_f

    def over_s(serie, umbral):
        s = pd.to_numeric(serie, errors='coerce').dropna()
        if len(s) == 0: return np.nan, 0, 0
        n = int((s > umbral).sum())
        return n / len(s), n, len(s)

    def cj(p): return f"{1/p:.2f}" if p and p > 0 else "∞"

    def filtrar_ctx(base_df, ctx, umbral, es_visit=False):
        ids = []
        for idx, row in base_df.iterrows():
            if es_visit:
                l_ = row.get("hist_pts_home", np.nan)
                v_ = row.get("hist_pts_away", np.nan)
                if pd.isna(l_) or pd.isna(v_): continue
                d = int(v_) - int(l_)
            else:
                h_ = row.get("hist_pts_home", np.nan)
                a_ = row.get("hist_pts_away", np.nan)
                if pd.isna(h_) or pd.isna(a_): continue
                d = int(h_) - int(a_)
            if   ctx == "FAVORITO" and d >=  umbral: ids.append(idx)
            elif ctx == "UNDERDOG" and d <= -umbral: ids.append(idx)
            elif ctx == "REÑIDO"   and -umbral < d < umbral: ids.append(idx)
        return df.loc[ids].copy() if ids else pd.DataFrame()

    df_c1 = df[df["home"] == HOME_TEAM].copy()
    df_c2 = filtrar_ctx(df_c1, contexto,   UMBRAL_PTS)
    df_c3 = df[df["away"] == AWAY_TEAM].copy()
    df_c4 = filtrar_ctx(df_c3, contexto_v, UMBRAL_PTS, es_visit=True)

    ctx_labels = {
        "FAVORITO": f"⭐ Favorito (≥{UMBRAL_PTS}pts)",
        "UNDERDOG": f"💪 Underdog (≥{UMBRAL_PTS}pts)",
        "REÑIDO":   f"⚔️ Reñido (<{UMBRAL_PTS}pts)",
    }
    ctx_v_labels = {
        "FAVORITO": "⭐ Fav. Visitante",
        "UNDERDOG": "💪 Underdog Visit.",
        "REÑIDO":   "⚔️ Reñido Visit.",
    }

    caso_tabs = st.tabs([
        f"📋 C1 · {HOME_TEAM} Local ({len(df_c1)}pj)",
        f"🎯 C2 · {ctx_labels[contexto]} ({len(df_c2)}pj)",
        f"📋 C3 · {AWAY_TEAM} Visit. ({len(df_c3)}pj)",
        f"🎯 C4 · {ctx_v_labels[contexto_v]} ({len(df_c4)}pj)",
    ])

    # ── Render de cada caso ────────────────────────────────
    def render_caso(df_raw_filt, team_name, es_visit, tab_key):
        if df_raw_filt is None or df_raw_filt.empty:
            st.warning("⚠️ Sin partidos para este contexto")
            return

        df_f = swap_v(df_raw_filt) if es_visit else df_raw_filt.copy()
        n = len(df_f)

        w = int((df_f["FTR"] == "H").sum())
        d = int((df_f["FTR"] == "D").sum())
        l = int((df_f["FTR"] == "A").sum())
        p_w = w/n; p_d = d/n; p_l = l/n

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("✅ Gana",   f"{p_w:.1%}", f"{w} pj · CJ {cj(p_w)}")
        with c2: st.metric("🟡 Empata", f"{p_d:.1%}", f"{d} pj · CJ {cj(p_d)}")
        with c3: st.metric("❌ Pierde", f"{p_l:.1%}", f"{l} pj · CJ {cj(p_l)}")
        with c4: st.metric("📊 Total",  f"{n} partidos")

        # Tabla historial
        st.markdown("##### 📅 Historial")
        rows = []
        for _, r in df_f.sort_values("fecha").iterrows():
            ghl = int(r["home_goals"]) if pd.notna(r["home_goals"]) else 0
            gha = int(r["away_goals"]) if pd.notna(r["away_goals"]) else 0
            ftr = r.get("FTR", "")
            res = "✅ Ganó" if ftr=="H" else ("❌ Perdió" if ftr=="A" else "🟡 Empate")
            row = {
                "Fecha":   r["fecha"].strftime("%d/%m/%Y") if pd.notna(r["fecha"]) else "N/D",
                "Rival":   str(r["away"]),
                "Pos.L":   str(int(r["hist_pos_home"])) if pd.notna(r.get("hist_pos_home")) else "?",
                "Pos.V":   str(int(r["hist_pos_away"])) if pd.notna(r.get("hist_pos_away")) else "?",
                "Pts.L":   str(int(r["hist_pts_home"])) if pd.notna(r.get("hist_pts_home")) else "?",
                "Pts.V":   str(int(r["hist_pts_away"])) if pd.notna(r.get("hist_pts_away")) else "?",
                "Result":  res,
                "Marc":    f"{ghl}-{gha}",
            }
            if TIENE_CORNERS:
                hc = r.get("home_corner_kicks", np.nan)
                ac = r.get("away_corner_kicks", np.nan)
                row["Cór.L"]   = str(int(hc)) if pd.notna(hc) else "-"
                row["Cór.V"]   = str(int(ac)) if pd.notna(ac) else "-"
                row["Cór.Tot"] = str(int(hc+ac)) if pd.notna(hc) and pd.notna(ac) else "-"
            if TIENE_REMATES:
                ht = r.get("home_total_shots",     np.nan)
                at = r.get("away_total_shots",     np.nan)
                hs = r.get("home_shots_on_target", np.nan)
                av = r.get("away_shots_on_target", np.nan)
                row["R.L"]   = str(int(ht)) if pd.notna(ht) else "-"
                row["R.V"]   = str(int(at)) if pd.notna(at) else "-"
                row["SOT.L"] = str(int(hs)) if pd.notna(hs) else "-"
                row["SOT.V"] = str(int(av)) if pd.notna(av) else "-"
            if TIENE_ATAJADAS:
                hgk = r.get("HomeGK_Saves", np.nan)
                agk = r.get("AwayGK_Saves", np.nan)
                row["Atj.L"] = str(int(hgk)) if pd.notna(hgk) else "-"
                row["Atj.V"] = str(int(agk)) if pd.notna(agk) else "-"
            if TIENE_CUOTAS:
                row["Cuota1"] = f"{r['odd_h']:.2f}" if pd.notna(r.get("odd_h")) else "-"
                row["CuotaX"] = f"{r['odd_d']:.2f}" if pd.notna(r.get("odd_d")) else "-"
                row["Cuota2"] = f"{r['odd_a']:.2f}" if pd.notna(r.get("odd_a")) else "-"
            rows.append(row)

        st.dataframe(pd.DataFrame(rows), use_container_width=True,
                     height=min(480, n*36+60))

        # ── Gráficos Over ──────────────────────────────────
        st.markdown("##### 📈 Probabilidades Over")

        _key_ctr = [0]
        def bar_chart(over_dict, title, color="#00e676"):
            _key_ctr[0] += 1
            labels = list(over_dict.keys())
            values = [v[0]*100 if not np.isnan(v[0]) else 0 for v in over_dict.values()]
            annots = [f"{v:.1f}% ({d[1]}/{d[2]})" for v, d in zip(values, over_dict.values())]
            fig = go.Figure(go.Bar(
                x=values, y=labels, orientation='h',
                marker_color=[color if v >= 50 else "#ef5350" for v in values],
                text=annots, textposition='outside', cliponaxis=False,
            ))
            fig.add_vline(x=50, line_dash="dot", line_color="rgba(255,255,255,0.15)")
            fig.update_layout(
                title=dict(text=title, font=dict(size=12, color="white")),
                xaxis=dict(range=[0, 118], ticksuffix="%",
                           gridcolor="#1f2333", color="#888"),
                yaxis=dict(autorange="reversed", color="#ccc"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(13,17,23,0)',
                font=dict(color="white", size=11),
                height=max(160, len(labels)*44+60),
                margin=dict(l=5, r=115, t=36, b=5),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True,
                            key=f"{tab_key}_{_key_ctr[0]}")

        hg  = pd.to_numeric(df_f["home_goals"], errors='coerce')
        ag  = pd.to_numeric(df_f["away_goals"], errors='coerce')
        tg  = (hg + ag).dropna()

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            bar_chart({f"Over {t}": over_s(tg, t) for t in [1.5,2.5,3.5,4.5]},
                      "⚽ Goles Totales", "#4CAF50")
        with col_g2:
            gd = {f"{team_name[:12]} O{t}": over_s(hg, t) for t in [0.5,1.5,2.5]}
            gd.update({f"Rival O{t}": over_s(ag, t) for t in [0.5,1.5]})
            bar_chart(gd, "⚽ Goles por equipo", "#81C784")

        if TIENE_CORNERS:
            hc  = pd.to_numeric(df_f["home_corner_kicks"], errors='coerce')
            ac  = pd.to_numeric(df_f["away_corner_kicks"], errors='coerce')
            tc  = (hc + ac).dropna()
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                bar_chart({f"Over {t}": over_s(tc, t) for t in [6.5,7.5,8.5,9.5,10.5,11.5]},
                          "🔄 Córners Totales", "#2196F3")
            with col_c2:
                cd = {f"{team_name[:12]} O{t}": over_s(hc, t) for t in [3.5,4.5,5.5]}
                cd.update({f"Rival O{t}": over_s(ac, t) for t in [3.5,4.5]})
                bar_chart(cd, "🔄 Córners por equipo", "#64B5F6")

        if TIENE_REMATES:
            hs  = pd.to_numeric(df_f["home_shots_on_target"], errors='coerce')
            as_ = pd.to_numeric(df_f["away_shots_on_target"], errors='coerce')
            ts  = (hs + as_).dropna()
            ht2 = pd.to_numeric(df_f["home_total_shots"], errors='coerce')
            at2 = pd.to_numeric(df_f["away_total_shots"], errors='coerce')
            tt  = (ht2 + at2).dropna()
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                bar_chart({f"Over {t}": over_s(ts, t) for t in [4.5,5.5,6.5,7.5,8.5]},
                          "🎯 SOT Totales", "#9C27B0")
            with col_r2:
                bar_chart({f"Over {t}": over_s(tt, t) for t in [17.5,19.5,22.5,25.5]},
                          "💥 Remates Totales", "#00BCD4")

        if TIENE_ATAJADAS:
            hs2 = pd.to_numeric(df_f["HomeGK_Saves"], errors='coerce')
            as2 = pd.to_numeric(df_f["AwayGK_Saves"], errors='coerce')
            ts2 = (hs2 + as2).dropna()
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                bar_chart({f"Over {t}": over_s(ts2, t) for t in [3.5,4.5,5.5,6.5]},
                          "🧤 Atajadas Totales", "#607D8B")
            with col_a2:
                ad = {f"{team_name[:12]} O{t}": over_s(hs2, t) for t in [2.5,3.5,4.5]}
                ad.update({f"Rival O{t}": over_s(as2, t) for t in [2.5,3.5]})
                bar_chart(ad, "🧤 Atajadas por equipo", "#90A4AE")

        hyw = pd.to_numeric(df_f["home_yellow_cards"], errors='coerce').fillna(0)
        ayw = pd.to_numeric(df_f["away_yellow_cards"], errors='coerce').fillna(0)
        hrd = pd.to_numeric(df_f["home_red_cards"] if "home_red_cards" in df_f.columns
                             else pd.Series(0, index=df_f.index), errors='coerce').fillna(0)
        ard = pd.to_numeric(df_f["away_red_cards"] if "away_red_cards" in df_f.columns
                             else pd.Series(0, index=df_f.index), errors='coerce').fillna(0)
        tc_c = hyw + ayw + hrd + ard

        hf = pd.to_numeric(df_f["home_fouls"], errors='coerce')
        af = pd.to_numeric(df_f["away_fouls"], errors='coerce')
        tf = (hf + af).dropna()

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            bar_chart({f"Over {t}": over_s(tc_c, t) for t in [2.5,3.5,4.5,5.5]},
                      "🟨 Tarjetas Totales", "#FF9800")
        with col_t2:
            if tf.notna().sum() > 0:
                bar_chart({f"Over {t}": over_s(tf, t) for t in [19.5,22.5,25.5,28.5]},
                          "🦵 Faltas Totales", "#795548")

        # Cuotas B365
        if TIENE_CUOTAS:
            oh = pd.to_numeric(df_f["odd_h"], errors='coerce').mean()
            od = pd.to_numeric(df_f["odd_d"], errors='coerce').mean()
            oa = pd.to_numeric(df_f["odd_a"], errors='coerce').mean()
            val_h = (1/oh - p_w) if not np.isnan(oh) and oh > 0 else np.nan
            val_d = (1/od - p_d) if not np.isnan(od) and od > 0 else np.nan
            val_a = (1/oa - p_l) if not np.isnan(oa) and oa > 0 else np.nan

            st.markdown("##### 💰 Cuotas promedio B365")
            cq1, cq2, cq3 = st.columns(3)
            with cq1:
                st.metric("1 Local",  f"{oh:.2f}",
                          f"{val_h:+.3f} value" if not np.isnan(val_h) else "")
            with cq2:
                st.metric("X Empate", f"{od:.2f}",
                          f"{val_d:+.3f} value" if not np.isnan(val_d) else "")
            with cq3:
                st.metric("2 Visit.", f"{oa:.2f}",
                          f"{val_a:+.3f} value" if not np.isnan(val_a) else "")
            st.caption("🟢 value positivo = potencial valor · 🔴 negativo = la casa sobrevalora")

    with caso_tabs[0]: render_caso(df_c1, HOME_TEAM, False, "c1")
    with caso_tabs[1]: render_caso(df_c2, HOME_TEAM, False, "c2")
    with caso_tabs[2]: render_caso(df_c3, AWAY_TEAM, True,  "c3")
    with caso_tabs[3]: render_caso(df_c4, AWAY_TEAM, True,  "c4")

# ───────────────────────────────────────────────────────────
# TAB 3 — STATS DE LIGA
# ───────────────────────────────────────────────────────────
with tab_stats:
    st.header(f"📊 Stats generales — {liga_nombre}")

    metrica = st.selectbox("Métrica a comparar", [
        "Goles anotados", "Goles recibidos", "Remates totales",
        "Remates al arco", "Córners", "Atajadas", "Amarillas", "Faltas"
    ])

    col_map_stats = {
        "Goles anotados":  ("home_goals",           "away_goals"),
        "Goles recibidos": ("away_goals",            "home_goals"),
        "Remates totales": ("home_total_shots",      "away_total_shots"),
        "Remates al arco": ("home_shots_on_target",  "away_shots_on_target"),
        "Córners":         ("home_corner_kicks",     "away_corner_kicks"),
        "Atajadas":        ("HomeGK_Saves",          "AwayGK_Saves"),
        "Amarillas":       ("home_yellow_cards",     "away_yellow_cards"),
        "Faltas":          ("home_fouls",            "away_fouls"),
    }

    col_h, col_a = col_map_stats[metrica]
    equipos_stats = []
    for eq in standings.index:
        como_local = df[df["home"] == eq][col_h]
        como_visit = df[df["away"] == eq][col_a]
        todos = pd.concat([
            pd.to_numeric(como_local, errors='coerce'),
            pd.to_numeric(como_visit, errors='coerce')
        ]).dropna()
        if len(todos) > 0:
            equipos_stats.append({
                "Equipo": eq,
                "Promedio": round(todos.mean(), 2),
                "Partidos": len(todos)
            })

    df_stats = pd.DataFrame(equipos_stats).sort_values("Promedio", ascending=False)
    top_n = st.slider("Top equipos a mostrar", 5, len(df_stats), min(12, len(df_stats)))
    df_top = df_stats.head(top_n)

    fig_s = go.Figure(go.Bar(
        x=df_top["Promedio"],
        y=df_top["Equipo"],
        orientation='h',
        marker_color="#00e676",
        text=df_top["Promedio"].apply(lambda x: f"{x:.2f}"),
        textposition='outside',
    ))
    fig_s.update_layout(
        title=f"{metrica} — Promedio por partido",
        xaxis=dict(gridcolor="#1f2333", color="#888"),
        yaxis=dict(autorange="reversed", color="#ccc"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(13,17,23,0)',
        font=dict(color="white", size=12),
        height=max(300, top_n*44+80),
        margin=dict(l=5, r=80, t=50, b=5),
        showlegend=False,
    )
    st.plotly_chart(fig_s, use_container_width=True)
    st.dataframe(df_stats, use_container_width=True)
