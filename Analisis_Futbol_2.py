# ─── INSTALAR: pip install streamlit plotly
# ─── CORRER  : python -m streamlit run Analisis_Futbol_2.py

import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
import plotly.graph_objects as go
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════
# CONTADOR GLOBAL DE KEYS — se reinicia en cada rerun de Streamlit
# ══════════════════════════════════════════════════════════════
_KEY_CTR = [0]
def _ck():
    _KEY_CTR[0] += 1
    return f"k{_KEY_CTR[0]}"


st.set_page_config(page_title="⚽ Análisis de Fútbol", page_icon="⚽",
                   layout="wide", initial_sidebar_state="expanded")

FOLDER = "."  # Streamlit Cloud: CSVs en la raíz del repositorio

st.markdown("""
<style>
    .main-title {
        font-size:2.2rem; font-weight:900; letter-spacing:-1px;
        background:linear-gradient(135deg,#00e676,#1de9b6);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .ctx-badge { display:inline-block; padding:7px 18px; border-radius:25px;
                 font-weight:700; font-size:0.95rem; margin:8px 0 16px 0; }
    .favorito { background:#0d2e0d; color:#4CAF50; border:1.5px solid #4CAF50; }
    .underdog  { background:#2e0d0d; color:#ef5350; border:1.5px solid #ef5350; }
    .renido    { background:#2e280d; color:#FFC107; border:1.5px solid #FFC107; }
    div[data-testid="metric-container"] {
        background:#0e1117; border:1px solid #1f2333; border-radius:10px; padding:14px 18px; }
    .stTabs [data-baseweb="tab"] { font-weight:600; font-size:0.85rem; }
    .stExpander { border:1px solid #1f2333 !important; border-radius:8px; }
    .outlier-badge { background:#3a1a1a; color:#ef5350; border:1px solid #ef5350;
                     border-radius:12px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE DATOS
# ══════════════════════════════════════════════════════════════

def normalizar_df(df, es_nuevo):
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
        out["home_passes"]  = np.nan; out["away_passes"]        = np.nan
        out["home_tackles"] = np.nan; out["away_tackles"]       = np.nan
        out["home_interceptions"] = np.nan; out["away_interceptions"] = np.nan
        out["odd_h"]   = pd.to_numeric(df.get("B365H",    pd.Series(dtype=float)), errors="coerce")
        out["odd_d"]   = pd.to_numeric(df.get("B365D",    pd.Series(dtype=float)), errors="coerce")
        out["odd_a"]   = pd.to_numeric(df.get("B365A",    pd.Series(dtype=float)), errors="coerce")
        out["odd_o25"] = pd.to_numeric(df.get("B365>2.5", pd.Series(dtype=float)), errors="coerce")
        out["odd_u25"] = pd.to_numeric(df.get("B365<2.5", pd.Series(dtype=float)), errors="coerce")
        out["odd_ahh"] = pd.to_numeric(df.get("B365AHH",  pd.Series(dtype=float)), errors="coerce")
        out["odd_aha"] = pd.to_numeric(df.get("B365AHA",  pd.Series(dtype=float)), errors="coerce")
        out["ah_line"] = pd.to_numeric(df.get("AHh",      pd.Series(dtype=float)), errors="coerce")
    else:
        col_map = {
            "fecha":"fecha","home":"home","away":"away",
            "home_goals":"home_goals","away_goals":"away_goals",
            "home_expected_goals":"home_expected_goals","away_expected_goals":"away_expected_goals",
            "home_total_shots":"home_total_shots","away_total_shots":"away_total_shots",
            "home_shots_on_target":"home_shots_on_target","away_shots_on_target":"away_shots_on_target",
            "home_corner_kicks":"home_corner_kicks","away_corner_kicks":"away_corner_kicks",
            "home_fouls":"home_fouls","away_fouls":"away_fouls",
            "home_yellow_cards":"home_yellow_cards","away_yellow_cards":"away_yellow_cards",
            "home_red_cards":"home_red_cards","away_red_cards":"away_red_cards",
            "home_goalkeeper_saves":"home_goalkeeper_saves","away_goalkeeper_saves":"away_goalkeeper_saves",
            "home_tackles":"home_tackles","away_tackles":"away_tackles",
            "home_passes":"home_passes","away_passes":"away_passes",
            "home_interceptions":"home_interceptions","away_interceptions":"away_interceptions",
        }
        for src, dst in col_map.items():
            out[dst] = df[src] if src in df.columns else np.nan
        if "fecha" in out.columns:
            out["fecha"] = pd.to_datetime(out["fecha"], dayfirst=True, errors="coerce")
        for col in ["odd_h","odd_d","odd_a","odd_o25","odd_u25","odd_ahh","odd_aha","ah_line"]:
            out[col] = np.nan
    return out


def build_standings(sdf):
    records = {}
    for _, row in sdf.iterrows():
        ht, at = row["home"], row["away"]
        hg = int(row["home_goals"]) if pd.notna(row["home_goals"]) else 0
        ag = int(row["away_goals"]) if pd.notna(row["away_goals"]) else 0
        ftr = row["FTR"]
        for team in [ht, at]:
            if team not in records:
                records[team] = dict(PJ=0,G=0,E=0,P=0,GF=0,GC=0,PTS=0)
        records[ht]["PJ"]+=1; records[at]["PJ"]+=1
        records[ht]["GF"]+=hg; records[ht]["GC"]+=ag
        records[at]["GF"]+=ag; records[at]["GC"]+=hg
        if ftr=="H":
            records[ht]["G"]+=1; records[ht]["PTS"]+=3; records[at]["P"]+=1
        elif ftr=="A":
            records[at]["G"]+=1; records[at]["PTS"]+=3; records[ht]["P"]+=1
        else:
            records[ht]["E"]+=1; records[ht]["PTS"]+=1
            records[at]["E"]+=1; records[at]["PTS"]+=1
    t = pd.DataFrame(records).T
    t["DG"] = t["GF"]-t["GC"]
    t = t.sort_values(["PTS","DG","GF"], ascending=False)
    t["Pos"] = range(1,len(t)+1)
    return t[["Pos","PJ","G","E","P","GF","GC","DG","PTS"]]


def standings_at_date(season_df, fecha_limite):
    sdf = season_df[season_df["fecha"] < fecha_limite]
    return pd.DataFrame() if sdf.empty else build_standings(sdf)


@st.cache_data(show_spinner=False)
def load_and_process(data_path):
    df_raw = pd.read_csv(data_path, encoding="utf-8")
    FORMATO_NUEVO = "HomeTeam" in df_raw.columns
    FORMATO_VIEJO = "home"     in df_raw.columns
    if not FORMATO_NUEVO and not FORMATO_VIEJO:
        return None, None, None

    df = normalizar_df(df_raw, FORMATO_NUEVO)
    df = df.sort_values("fecha").reset_index(drop=True)
    df["HomeGK_Saves"] = df["home_goalkeeper_saves"]
    df["AwayGK_Saves"] = df["away_goalkeeper_saves"]

    # ── Atajadas inferidas: SOT rival − goles rival = atajadas portero ──
    home_sot = pd.to_numeric(df["away_shots_on_target"], errors='coerce')
    away_sot = pd.to_numeric(df["home_shots_on_target"], errors='coerce')
    home_g   = pd.to_numeric(df["away_goals"], errors='coerce')
    away_g   = pd.to_numeric(df["home_goals"], errors='coerce')
    df["home_inferred_saves"] = (home_sot - home_g).clip(lower=0)
    df["away_inferred_saves"] = (away_sot - away_g).clip(lower=0)

    # Usar inferidas si no hay reales
    if df["HomeGK_Saves"].isna().all():
        df["HomeGK_Saves"] = df["home_inferred_saves"]
        df["AwayGK_Saves"] = df["away_inferred_saves"]
        df["home_goalkeeper_saves"] = df["home_inferred_saves"]
        df["away_goalkeeper_saves"] = df["away_inferred_saves"]

    df["season"] = df["fecha"].dt.year
    df["FTR"] = df.apply(
        lambda r: "H" if r["home_goals"] > r["away_goals"] else
                  ("A" if r["home_goals"] < r["away_goals"] else "D"), axis=1
    )
    df["season_start"] = df["fecha"].apply(lambda d: d.year if d.month>=7 else d.year-1)

    hist_pos_home={}; hist_pos_away={}; hist_pts_home={}; hist_pts_away={}
    for _, s_df in df.groupby("season_start"):
        s_df_s = s_df.sort_values("fecha")
        for idx, row in s_df_s.iterrows():
            std = standings_at_date(s_df_s, row["fecha"])
            ht, at = row["home"], row["away"]
            if std.empty:
                hist_pos_home[idx]=np.nan; hist_pos_away[idx]=np.nan
                hist_pts_home[idx]=np.nan; hist_pts_away[idx]=np.nan
            else:
                hist_pos_home[idx]=int(std.loc[ht,"Pos"]) if ht in std.index else np.nan
                hist_pos_away[idx]=int(std.loc[at,"Pos"]) if at in std.index else np.nan
                hist_pts_home[idx]=int(std.loc[ht,"PTS"]) if ht in std.index else np.nan
                hist_pts_away[idx]=int(std.loc[at,"PTS"]) if at in std.index else np.nan

    df["hist_pos_home"]=pd.Series(hist_pos_home)
    df["hist_pos_away"]=pd.Series(hist_pos_away)
    df["hist_pts_home"]=pd.Series(hist_pts_home)
    df["hist_pts_away"]=pd.Series(hist_pts_away)

    standings = build_standings(df)
    fmt = "football-data.co.uk" if FORMATO_NUEVO else "Formato propio"
    return df, standings, fmt


# ══════════════════════════════════════════════════════════════
# ESTADÍSTICAS DE LIGA
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def build_liga_stats(df_path):
    """
    Construye ranking de todos los equipos por métricas promedio
    (perspectiva unificada: home + away).
    """
    df_raw = pd.read_csv(df_path, encoding="utf-8")
    FORMATO_NUEVO = "HomeTeam" in df_raw.columns
    df = normalizar_df(df_raw, FORMATO_NUEVO)
    df["HomeGK_Saves"] = pd.to_numeric(df.get("home_goalkeeper_saves", pd.Series(dtype=float)), errors='coerce')
    df["AwayGK_Saves"] = pd.to_numeric(df.get("away_goalkeeper_saves", pd.Series(dtype=float)), errors='coerce')
    home_sot = pd.to_numeric(df["away_shots_on_target"], errors='coerce')
    away_sot = pd.to_numeric(df["home_shots_on_target"], errors='coerce')
    df["home_inf_saves"] = (home_sot - pd.to_numeric(df["away_goals"],errors='coerce')).clip(lower=0)
    df["away_inf_saves"] = (away_sot - pd.to_numeric(df["home_goals"],errors='coerce')).clip(lower=0)
    if df["HomeGK_Saves"].isna().all():
        df["HomeGK_Saves"] = df["home_inf_saves"]
        df["AwayGK_Saves"] = df["away_inf_saves"]

    def col(df, c): return pd.to_numeric(df[c], errors='coerce') if c in df.columns else pd.Series(np.nan, index=df.index)

    home_rows = pd.DataFrame({
        "team":     df["home"],
        "corners":  col(df,"home_corner_kicks"),
        "shots":    col(df,"home_total_shots"),
        "sot":      col(df,"home_shots_on_target"),
        "goles":    col(df,"home_goals"),
        "gc":       col(df,"away_goals"),
        "saves":    df["HomeGK_Saves"],
        "amarillas":col(df,"home_yellow_cards"),
        "rojas":    col(df,"home_red_cards"),
    })
    away_rows = pd.DataFrame({
        "team":     df["away"],
        "corners":  col(df,"away_corner_kicks"),
        "shots":    col(df,"away_total_shots"),
        "sot":      col(df,"away_shots_on_target"),
        "goles":    col(df,"away_goals"),
        "gc":       col(df,"home_goals"),
        "saves":    df["AwayGK_Saves"],
        "amarillas":col(df,"away_yellow_cards"),
        "rojas":    col(df,"away_red_cards"),
    })

    all_rows = pd.concat([home_rows, away_rows], ignore_index=True)
    agg = all_rows.groupby("team").agg(
        PJ=("goles","count"),
        Corners=("corners","mean"),
        Remates=("shots","mean"),
        SOT=("sot","mean"),
        Goles=("goles","mean"),
        GC=("gc","mean"),
        Atajadas=("saves","mean"),
        Amarillas=("amarillas","mean"),
        Rojas=("rojas","mean"),
    ).round(2)
    return agg


# ══════════════════════════════════════════════════════════════
# ANÁLISIS
# ══════════════════════════════════════════════════════════════

def swap_visitante(df_filt):
    df_filt = df_filt.copy()
    pairs = [
        ("home","away"),("home_goals","away_goals"),
        ("home_expected_goals","away_expected_goals"),
        ("home_total_shots","away_total_shots"),
        ("home_shots_on_target","away_shots_on_target"),
        ("home_corner_kicks","away_corner_kicks"),
        ("home_fouls","away_fouls"),
        ("home_yellow_cards","away_yellow_cards"),
        ("home_red_cards","away_red_cards"),
        ("home_goalkeeper_saves","away_goalkeeper_saves"),
        ("HomeGK_Saves","AwayGK_Saves"),
        ("home_inferred_saves","away_inferred_saves"),
        ("home_passes","away_passes"),
        ("home_tackles","away_tackles"),
        ("home_interceptions","away_interceptions"),
        ("odd_h","odd_a"),("odd_ahh","odd_aha"),
        ("hist_pos_home","hist_pos_away"),
        ("hist_pts_home","hist_pts_away"),
    ]
    for a, b in pairs:
        if a in df_filt.columns and b in df_filt.columns:
            df_filt[a], df_filt[b] = df_filt[b].copy(), df_filt[a].copy()
    df_filt["FTR"] = df_filt["FTR"].map({"H":"A","A":"H","D":"D"})
    return df_filt


def over_stat(serie, umbral):
    s = pd.to_numeric(serie, errors='coerce').dropna()
    if len(s)==0: return np.nan, 0, 0
    n = int((s>umbral).sum())
    return n/len(s), n, len(s)


def detect_outliers_iqr(serie):
    """Retorna máscara booleana de outliers usando método IQR × 1.5."""
    s = pd.to_numeric(serie, errors='coerce')
    valid = s.dropna()
    if len(valid) < 5:
        return pd.Series(False, index=serie.index)
    Q1, Q3 = valid.quantile(0.25), valid.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    return (s < lower) | (s > upper)


def compute_stats(df_filt, tiene):
    n = len(df_filt)
    if n==0: return None
    s = {"n":n}
    w=int((df_filt["FTR"]=="H").sum()); d=int((df_filt["FTR"]=="D").sum()); l=int((df_filt["FTR"]=="A").sum())
    s.update(wins=w,draws=d,losses=l,p_w=w/n,p_d=d/n,p_l=l/n)

    def m(col):
        return pd.to_numeric(df_filt[col],errors='coerce').mean() if col in df_filt.columns else np.nan

    s["avg"] = {
        "Goles":           (m("home_goals"),             m("away_goals")),
        "Remates totales": (m("home_total_shots"),       m("away_total_shots")),
        "Remates al arco": (m("home_shots_on_target"),   m("away_shots_on_target")),
        "Córners":         (m("home_corner_kicks"),      m("away_corner_kicks")),
        "Atajadas (portero EQ)": (m("HomeGK_Saves"),    m("AwayGK_Saves")),
        "Faltas":          (m("home_fouls"),             m("away_fouls")),
        "Amarillas":       (m("home_yellow_cards"),      m("away_yellow_cards")),
        "Rojas":           (m("home_red_cards"),         m("away_red_cards")),
    }

    hg=pd.to_numeric(df_filt["home_goals"],errors='coerce')
    ag=pd.to_numeric(df_filt["away_goals"],errors='coerce')
    tg=(hg+ag).dropna()
    s["goles_total_over"]={t:over_stat(tg,t) for t in [1.5,2.5,3.5,4.5]}
    s["goles_home_over"] ={t:over_stat(hg,t) for t in [0.5,1.5,2.5]}
    s["goles_away_over"] ={t:over_stat(ag,t) for t in [0.5,1.5]}

    if tiene["corners"]:
        hc=pd.to_numeric(df_filt["home_corner_kicks"],errors='coerce')
        ac=pd.to_numeric(df_filt["away_corner_kicks"],errors='coerce')
        tc=(hc+ac).dropna()
        s["corn_total_over"]={t:over_stat(tc,t) for t in [6.5,7.5,8.5,9.5,10.5,11.5]}
        s["corn_home_over"] ={t:over_stat(hc,t) for t in [3.5,4.5,5.5]}
        s["corn_away_over"] ={t:over_stat(ac,t) for t in [3.5,4.5]}

    if tiene["remates"]:
        hs =pd.to_numeric(df_filt["home_shots_on_target"],errors='coerce')
        as_=pd.to_numeric(df_filt["away_shots_on_target"],errors='coerce')
        s["sot_over"]  ={t:over_stat((hs+as_).dropna(),t) for t in [4.5,5.5,6.5,7.5,8.5]}
        ht2=pd.to_numeric(df_filt["home_total_shots"],errors='coerce')
        at2=pd.to_numeric(df_filt["away_total_shots"],errors='coerce')
        s["shots_over"]={t:over_stat((ht2+at2).dropna(),t) for t in [17.5,19.5,22.5,25.5]}

    hyw=pd.to_numeric(df_filt["home_yellow_cards"],errors='coerce').fillna(0)
    ayw=pd.to_numeric(df_filt["away_yellow_cards"],errors='coerce').fillna(0)
    ix=df_filt.index
    hrd=pd.to_numeric(df_filt["home_red_cards"] if "home_red_cards" in df_filt.columns else pd.Series(0,index=ix),errors='coerce').fillna(0)
    ard=pd.to_numeric(df_filt["away_red_cards"] if "away_red_cards" in df_filt.columns else pd.Series(0,index=ix),errors='coerce').fillna(0)
    s["cards_over"]={t:over_stat(hyw+ayw+hrd+ard,t) for t in [2.5,3.5,4.5,5.5]}

    if tiene["atajadas"]:
        hs2=pd.to_numeric(df_filt["HomeGK_Saves"],errors='coerce')
        as2=pd.to_numeric(df_filt["AwayGK_Saves"],errors='coerce')
        s["saves_over"]={t:over_stat((hs2+as2).dropna(),t) for t in [3.5,4.5,5.5,6.5]}

    hf=pd.to_numeric(df_filt["home_fouls"],errors='coerce')
    af=pd.to_numeric(df_filt["away_fouls"],errors='coerce')
    tf=(hf+af).dropna()
    if tf.notna().sum()>0:
        s["fouls_over"]={t:over_stat(tf,t) for t in [19.5,22.5,25.5,28.5]}

    if tiene["cuotas"]:
        s["odd_h"]  =pd.to_numeric(df_filt["odd_h"],  errors='coerce').mean()
        s["odd_d"]  =pd.to_numeric(df_filt["odd_d"],  errors='coerce').mean()
        s["odd_a"]  =pd.to_numeric(df_filt["odd_a"],  errors='coerce').mean()
        s["odd_o25"]=pd.to_numeric(df_filt["odd_o25"],errors='coerce').mean()
        s["odd_u25"]=pd.to_numeric(df_filt["odd_u25"],errors='coerce').mean()

    return s


def build_match_df(df_filt, tiene):
    rows = []
    for _, r in df_filt.sort_values("fecha").iterrows():
        ghl=int(r["home_goals"]) if pd.notna(r["home_goals"]) else 0
        gha=int(r["away_goals"]) if pd.notna(r["away_goals"]) else 0
        ftr=r.get("FTR","")
        res="✅ Ganó" if ftr=="H" else ("❌ Perdió" if ftr=="A" else "🟡 Empate")
        row={
            "Fecha":   r["fecha"].strftime("%Y-%m-%d") if pd.notna(r["fecha"]) else "N/D",
            "Rival":   str(r["away"]),
            "Pos.EQ":  str(int(r["hist_pos_home"])) if pd.notna(r.get("hist_pos_home")) else "?",
            "Pos.Rv":  str(int(r["hist_pos_away"])) if pd.notna(r.get("hist_pos_away")) else "?",
            "Pts.EQ":  str(int(r["hist_pts_home"])) if pd.notna(r.get("hist_pts_home")) else "?",
            "Pts.Rv":  str(int(r["hist_pts_away"])) if pd.notna(r.get("hist_pts_away")) else "?",
            "Resultado":res, "Marcador":f"{ghl}-{gha}",
        }
        if tiene["corners"]:
            hc=r.get("home_corner_kicks",np.nan); ac=r.get("away_corner_kicks",np.nan)
            row["Cór.L"]=str(int(hc)) if pd.notna(hc) else "-"
            row["Cór.V"]=str(int(ac)) if pd.notna(ac) else "-"
            row["Cór.Tot"]=str(int(hc+ac)) if pd.notna(hc) and pd.notna(ac) else "-"
        if tiene["remates"]:
            hrt=r.get("home_total_shots",np.nan); art=r.get("away_total_shots",np.nan)
            hta=r.get("home_shots_on_target",np.nan); ata=r.get("away_shots_on_target",np.nan)
            row["R.Tot.L"]=str(int(hrt)) if pd.notna(hrt) else "-"
            row["R.Tot.V"]=str(int(art)) if pd.notna(art) else "-"
            row["R.Tot"]=str(int(hrt+art)) if pd.notna(hrt) and pd.notna(art) else "-"
            row["R.Arc.L"]=str(int(hta)) if pd.notna(hta) else "-"
            row["R.Arc.V"]=str(int(ata)) if pd.notna(ata) else "-"
            row["R.Arc.Tot"]=str(int(hta+ata)) if pd.notna(hta) and pd.notna(ata) else "-"
        if tiene["atajadas"]:
            hgk=r.get("HomeGK_Saves",np.nan); agk=r.get("AwayGK_Saves",np.nan)
            row["Ataj.L"]=str(int(hgk)) if pd.notna(hgk) else "-"
            row["Ataj.V"]=str(int(agk)) if pd.notna(agk) else "-"
        if tiene["cuotas"]:
            def fr(col): v=r.get(col,np.nan); return str(round(float(v),2)) if pd.notna(v) else "-"
            row["1(L)"]=fr("odd_h"); row["X"]=fr("odd_d")
            row["2(V)"]=fr("odd_a"); row["O2.5"]=fr("odd_o25"); row["AH"]=fr("ah_line")
        rows.append(row)
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════
# GRÁFICO DE TENDENCIA / ATÍPICOS
# ══════════════════════════════════════════════════════════════

def make_trend_chart(df_sorted, serie, title, color):
    """
    Gráfico de línea partido-a-partido con detección de atípicos.
    Devuelve (fig, serie_ordenada, mask_outliers) o None si hay pocos datos.
    """
    s = pd.to_numeric(serie, errors='coerce')
    valid = s.dropna()
    if len(valid) < 4:
        return None, s, pd.Series(False, index=s.index)

    mean_v = valid.mean()
    std_v  = valid.std()
    Q1, Q3 = valid.quantile(0.25), valid.quantile(0.75)
    IQR = Q3 - Q1
    lower_f = Q1 - 1.5*IQR
    upper_f = Q3 + 1.5*IQR
    is_out = (s < lower_f) | (s > upper_f)

    dates   = df_sorted["fecha"].dt.strftime("%Y-%m-%d").fillna("?")
    rivals  = df_sorted["away"].fillna("?")
    pos_rv  = df_sorted["hist_pos_away"].fillna("?").astype(str)
    pts_rv  = df_sorted["hist_pts_away"].fillna("?").astype(str)
    ftr_col = df_sorted["FTR"].map({"H":"✅","A":"❌","D":"🟡"}).fillna("?")

    vals = s.tolist()
    x    = list(range(1, len(df_sorted)+1))

    hover_norm = [
        f"<b>{d}</b>  {res}<br>vs {r}  (#{p} · {pt}pts)<br><b>{title}: {v:.0f}</b>"
        for d,r,p,pt,v,res,o in zip(dates,rivals,pos_rv,pts_rv,vals,ftr_col,is_out) if not o
    ]
    hover_out = [
        f"<b>⚠️ ATÍPICO</b><br><b>{d}</b>  {res}<br>vs {r}  (#{p} · {pt}pts)<br><b>{title}: {v:.0f}</b>"
        for d,r,p,pt,v,res,o in zip(dates,rivals,pos_rv,pts_rv,vals,ftr_col,is_out) if o
    ]
    x_norm = [xi for xi,o in zip(x,is_out) if not o]
    y_norm = [vi for vi,o in zip(vals,is_out) if not o]
    x_out  = [xi for xi,o in zip(x,is_out) if o]
    y_out  = [vi for vi,o in zip(vals,is_out) if o]

    fig = go.Figure()

    # Banda ±1σ
    fig.add_hrect(y0=max(0,mean_v-std_v), y1=mean_v+std_v,
                  fillcolor=color, opacity=0.07, line_width=0)

    # Límites IQR (zona de atípicos)
    fig.add_hline(y=upper_f, line_dash="dot", line_color="rgba(239,83,80,0.35)", line_width=1)
    if lower_f > 0:
        fig.add_hline(y=lower_f, line_dash="dot", line_color="rgba(239,83,80,0.35)", line_width=1)

    # Media
    fig.add_hline(y=mean_v, line_dash="dash", line_color=color, opacity=0.8,
                  annotation_text=f" μ={mean_v:.1f}", annotation_position="right",
                  annotation_font_color=color)

    # Línea de conexión
    fig.add_trace(go.Scatter(x=x, y=vals, mode='lines',
                             line=dict(color=color, width=1.5), opacity=0.35,
                             showlegend=False, hoverinfo='skip'))

    # Puntos normales
    if x_norm:
        fig.add_trace(go.Scatter(
            x=x_norm, y=y_norm, mode='markers',
            marker=dict(color=color, size=9, line=dict(color='white',width=1)),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_norm, showlegend=False
        ))

    # Puntos atípicos
    if x_out:
        fig.add_trace(go.Scatter(
            x=x_out, y=y_out, mode='markers',
            marker=dict(color='#ef5350', size=14, symbol='diamond',
                        line=dict(color='white',width=1.5)),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_out, showlegend=False, name="⚠️ Atípico"
        ))

    n_out = int(is_out.sum())
    out_txt = f" · <span style='color:#ef5350'>⚠️ {n_out} atípico{'s' if n_out!=1 else ''}</span>" if n_out else ""
    fig.update_layout(
        title=dict(
            text=f"{title}  ·  μ={mean_v:.1f}  σ={std_v:.1f}  ({len(valid)}pj){out_txt}",
            font=dict(size=12)
        ),
        xaxis=dict(title="N° partido", gridcolor="#1f2333", tickmode='linear',
                   tick0=1, dtick=max(1,len(x)//10)),
        yaxis=dict(gridcolor="#1f2333"),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=11),
        height=260, margin=dict(l=5,r=100,t=48,b=30),
        showlegend=False,
    )
    return fig, s, is_out


def display_variabilidad(df_filt, team_name, tiene):
    """
    Muestra gráficos de tendencia partido-a-partido con detección de atípicos
    y tabla de partidos atípicos con contexto del rival.
    """
    df_s = df_filt.sort_values("fecha").reset_index(drop=True)

    # Definir métricas a analizar
    stats_def = []

    # Remates — más relevantes para el usuario
    if tiene["remates"]:
        hs_eq  = pd.to_numeric(df_s["home_total_shots"],      errors='coerce')
        sot_eq = pd.to_numeric(df_s["home_shots_on_target"],  errors='coerce')
        hs_rv  = pd.to_numeric(df_s["away_total_shots"],      errors='coerce')
        sot_rv = pd.to_numeric(df_s["away_shots_on_target"],  errors='coerce')
        stats_def += [
            (f"💥 Remates Totales — {team_name[:18]}", hs_eq,       "#00BCD4"),
            (f"🎯 Remates al Arco — {team_name[:18]}", sot_eq,      "#9C27B0"),
            ("💥 Remates Totales — Rival",              hs_rv,       "#546E7A"),
            ("🎯 Remates al Arco — Rival",              sot_rv,      "#7B1FA2"),
            ("💥💥 Remates Totales (ambos)",            hs_eq+hs_rv,  "#4DD0E1"),
            ("🎯🎯 Remates al Arco (ambos)",            sot_eq+sot_rv,"#CE93D8"),
        ]

    # Córners
    if tiene["corners"]:
        hc = pd.to_numeric(df_s["home_corner_kicks"], errors='coerce')
        ac = pd.to_numeric(df_s["away_corner_kicks"], errors='coerce')
        stats_def += [
            (f"🔄 Córners — {team_name[:18]}", hc,    "#2196F3"),
            ("🔄 Córners — Rival",             ac,    "#546E7A"),
            ("🔄🔄 Córners Totales",           hc+ac, "#64B5F6"),
        ]

    # Goles
    hg = pd.to_numeric(df_s["home_goals"], errors='coerce')
    ag = pd.to_numeric(df_s["away_goals"], errors='coerce')
    stats_def += [
        (f"⚽ Goles — {team_name[:18]}", hg,    "#4CAF50"),
        ("⚽ Goles — Rival",             ag,    "#EF9A9A"),
        ("⚽⚽ Goles Totales",           hg+ag, "#81C784"),
    ]

    # Atajadas
    if tiene["atajadas"]:
        hs2 = pd.to_numeric(df_s["HomeGK_Saves"], errors='coerce')
        stats_def.append((f"🧤 Atajadas portero — {team_name[:14]}", hs2, "#607D8B"))

    # Tarjetas
    hyw = pd.to_numeric(df_s["home_yellow_cards"], errors='coerce').fillna(0)
    ayw = pd.to_numeric(df_s["away_yellow_cards"], errors='coerce').fillna(0)
    stats_def.append(("🟨 Tarjetas (ambos)", hyw+ayw, "#FF9800"))

    # Mostrar en grid 2 columnas
    all_outliers = []  # recolectar todos los partidos atípicos

    for i in range(0, len(stats_def), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j >= len(stats_def): break
            title, serie, color = stats_def[i+j]
            result = make_trend_chart(df_s, serie, title, color)
            if result[0] is None: continue
            fig, s_ordered, is_out = result
            col.plotly_chart(fig, use_container_width=True, key=_ck())

            # Recolectar atípicos para esta métrica
            for idx2 in df_s.index[is_out.values]:
                r = df_s.loc[idx2]
                val = s_ordered.iloc[idx2] if idx2 < len(s_ordered) else np.nan
                all_outliers.append({
                    "Métrica":  title,
                    "Fecha":    r["fecha"].strftime("%Y-%m-%d") if pd.notna(r["fecha"]) else "?",
                    "Rival":    str(r["away"]),
                    "Pos.Rv":   str(int(r["hist_pos_away"])) if pd.notna(r.get("hist_pos_away")) else "?",
                    "Pts.Rv":   str(int(r["hist_pts_away"])) if pd.notna(r.get("hist_pts_away")) else "?",
                    "Valor":    f"{val:.0f}" if pd.notna(val) else "?",
                    "Resultado":f"{int(r['home_goals']) if pd.notna(r.get('home_goals')) else '?'}-"
                                f"{int(r['away_goals']) if pd.notna(r.get('away_goals')) else '?'}",
                })

    # Tabla resumen de atípicos
    if all_outliers:
        st.markdown("---")
        st.markdown("### ⚠️ Resumen de partidos atípicos")
        st.caption("Puntos fuera del rango IQR × 1.5 — pasa el cursor sobre los diamantes rojos para ver el detalle.")
        out_df = pd.DataFrame(all_outliers).drop_duplicates(subset=["Fecha","Rival","Métrica"])
        def color_atipico(val):
            return "color:#ef5350;font-weight:700"
        st.dataframe(
            out_df.style.map(lambda v: "color:#ef5350", subset=["Valor"]),
            use_container_width=True, hide_index=True
        )
        st.caption("💡 Tip: si el atípico es antiguo y el equipo se niveló después, los datos recientes son más fiables para apostar.")
    else:
        st.success("✅ No se detectaron partidos atípicos con los umbrales IQR × 1.5.")


# ══════════════════════════════════════════════════════════════
# VISUALES — OVER CHARTS
# ══════════════════════════════════════════════════════════════

def over_chart(over_dict, title, color="#00e676", label_prefix="Over"):
    labels=[f"{label_prefix} {k}" for k in over_dict]
    values=[v[0]*100 if not np.isnan(v[0]) else 0 for v in over_dict.values()]
    annots=[f"{v:.1f}%  ({d[1]}/{d[2]})" for v,d in zip(values,over_dict.values())]
    fig=go.Figure(go.Bar(
        x=values, y=labels, orientation='h',
        marker_color=[color if v>=50 else "#ef5350" for v in values],
        text=annots, textposition='outside',
        hovertemplate='%{y}: %{x:.1f}%<extra></extra>', cliponaxis=False,
    ))
    fig.add_vline(x=50, line_dash="dot", line_color="rgba(255,255,255,0.25)")
    fig.update_layout(
        title=dict(text=title, font=dict(size=13)),
        xaxis=dict(range=[0,115], ticksuffix="%", gridcolor="#1f2333", showgrid=True),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=12),
        height=max(180, len(labels)*48+70),
        margin=dict(l=5,r=90,t=38,b=5),
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════
# DISPLAY CASO COMPLETO
# ══════════════════════════════════════════════════════════════

def display_caso(df_filt, team_name, es_visitante, tiene):
    if df_filt is None or df_filt.empty:
        st.warning("⚠️ Sin partidos en este contexto"); return
    if es_visitante:
        df_filt = swap_visitante(df_filt)
    s = compute_stats(df_filt, tiene)
    if not s: return

    # Métricas
    c1,c2,c3=st.columns(3)
    cj=lambda p: f"Cuota justa: {1/p:.2f}" if p>0 else "Cuota justa: ∞"
    with c1: st.metric("✅ Gana",   f"{s['p_w']:.1%}  ({s['wins']})",   cj(s['p_w']))
    with c2: st.metric("🟡 Empata", f"{s['p_d']:.1%}  ({s['draws']})",  cj(s['p_d']))
    with c3: st.metric("❌ Pierde", f"{s['p_l']:.1%}  ({s['losses']})", cj(s['p_l']))

    # Historial
    with st.expander(f"📋 Historial — {s['n']} partidos", expanded=False):
        match_df=build_match_df(df_filt, tiene)
        def color_res(val):
            if "Ganó"   in str(val): return "color:#4CAF50;font-weight:700"
            if "Perdió" in str(val): return "color:#ef5350;font-weight:700"
            if "Empate" in str(val): return "color:#FFC107;font-weight:700"
            return ""
        st.dataframe(match_df.style.map(color_res, subset=["Resultado"]),
                     use_container_width=True, hide_index=True)

    # Promedios
    with st.expander("📊 Promedios por partido", expanded=False):
        avg_rows=[]
        for metrica,(hv,av) in s["avg"].items():
            if np.isnan(hv): continue
            avg_rows.append({"Métrica":metrica, team_name[:22]:f"{hv:.2f}",
                             "Rival":f"{av:.2f}" if not np.isnan(av) else "N/D",
                             "Total":f"{hv+av:.2f}" if not np.isnan(av) else f"{hv:.2f}"})
        if avg_rows:
            st.dataframe(pd.DataFrame(avg_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Over charts ─────────────────────────────────────────
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.plotly_chart(over_chart(s["goles_total_over"],"⚽ Goles Totales Over","#4CAF50"),
                        use_container_width=True, key=_ck())
        if tiene["corners"] and "corn_total_over" in s:
            st.plotly_chart(over_chart(s["corn_total_over"],"🔄 Córners Totales Over","#2196F3"),
                            use_container_width=True, key=_ck())
        if "cards_over" in s:
            st.plotly_chart(over_chart(s["cards_over"],"🟨 Tarjetas Totales Over","#FF9800"),
                            use_container_width=True, key=_ck())
        if "fouls_over" in s:
            st.plotly_chart(over_chart(s["fouls_over"],"🦵 Faltas Totales Over","#795548"),
                            use_container_width=True, key=_ck())
    with col_der:
        goles_det={**{f"EQ Over {k}":v for k,v in s["goles_home_over"].items()},
                   **{f"Rv Over {k}":v for k,v in s["goles_away_over"].items()}}
        st.plotly_chart(over_chart(goles_det,"⚽ Goles EQ / Rival detalle","#81C784",label_prefix=""),
                        use_container_width=True, key=_ck())
        if tiene["remates"] and "sot_over" in s:
            st.plotly_chart(over_chart(s["sot_over"],"🎯 Remates al Arco Over","#9C27B0"),
                            use_container_width=True, key=_ck())
        if tiene["remates"] and "shots_over" in s:
            st.plotly_chart(over_chart(s["shots_over"],"💥 Remates Totales Over","#00BCD4"),
                            use_container_width=True, key=_ck())
        if tiene["atajadas"] and "saves_over" in s:
            st.plotly_chart(over_chart(s["saves_over"],"🧤 Atajadas Over","#607D8B"),
                            use_container_width=True, key=_ck())
        if tiene["corners"] and "corn_home_over" in s:
            corn_det={**{f"EQ Over {k}":v for k,v in s["corn_home_over"].items()},
                      **{f"Rv Over {k}":v for k,v in s["corn_away_over"].items()}}
            st.plotly_chart(over_chart(corn_det,"🔄 Córners EQ / Rival detalle","#64B5F6",label_prefix=""),
                            use_container_width=True, key=_ck())

    # ── Cuotas ───────────────────────────────────────────────
    if tiene["cuotas"] and "odd_h" in s:
        st.markdown("---")
        st.markdown("**💰 Cuotas promedio B365 en estos partidos**")
        qc=st.columns(5)
        qc[0].metric("1 (Local)",  f"{s['odd_h']:.2f}"   if not np.isnan(s['odd_h'])   else "N/D")
        qc[1].metric("X (Empate)", f"{s['odd_d']:.2f}"   if not np.isnan(s['odd_d'])   else "N/D")
        qc[2].metric("2 (Visit.)", f"{s['odd_a']:.2f}"   if not np.isnan(s['odd_a'])   else "N/D")
        qc[3].metric("O 2.5",      f"{s['odd_o25']:.2f}" if not np.isnan(s['odd_o25']) else "N/D")
        qc[4].metric("U 2.5",      f"{s['odd_u25']:.2f}" if not np.isnan(s['odd_u25']) else "N/D")
        st.markdown("**📌 Value indicativo** *(positivo = potencial valor)*")
        vc=st.columns(3)
        def val_metric(col,odd_key,prob,label):
            o=s.get(odd_key,np.nan)
            v=(1/o-prob) if not np.isnan(o) and o>0 else np.nan
            ico="🟢" if not np.isnan(v) and v>0 else "🔴"
            col.metric(f"{ico} {label}", f"{v:+.3f}" if not np.isnan(v) else "N/D")
        val_metric(vc[0],"odd_h",s["p_w"],"Local")
        val_metric(vc[1],"odd_d",s["p_d"],"Empate")
        val_metric(vc[2],"odd_a",s["p_l"],"Visitante")

    # ── VARIABILIDAD Y ATÍPICOS ──────────────────────────────
    st.markdown("---")
    with st.expander("📈 Evolución partido a partido — Detección de atípicos", expanded=False):
        st.caption(
            "Los **diamantes rojos** son partidos atípicos (fuera del rango IQR × 1.5). "
            "Pasa el cursor para ver rival, posición y resultado. "
            "La línea punteada marca los límites; la banda sombreada = media ± 1σ."
        )
        display_variabilidad(df_filt, team_name, tiene)


# ══════════════════════════════════════════════════════════════
# ESTADÍSTICAS DE LIGA
# ══════════════════════════════════════════════════════════════

def display_liga_stats(liga_df, standings, tiene, data_path):
    """Ranking de todos los equipos por métricas clave."""
    agg = build_liga_stats(data_path)

    # Determinar columnas disponibles
    metrics_available = []
    if agg["Corners"].notna().any():    metrics_available.append(("🔄 Córners",       "Corners",   "#2196F3"))
    if agg["Remates"].notna().any():    metrics_available.append(("💥 Remates Tot.",  "Remates",   "#00BCD4"))
    if agg["SOT"].notna().any():        metrics_available.append(("🎯 SOT",           "SOT",       "#9C27B0"))
    if agg["Atajadas"].notna().any():   metrics_available.append(("🧤 Atajadas",      "Atajadas",  "#607D8B"))
    if agg["Goles"].notna().any():      metrics_available.append(("⚽ Goles favor",   "Goles",     "#4CAF50"))
    if agg["GC"].notna().any():         metrics_available.append(("⚽ Goles contra",  "GC",        "#ef5350"))
    if agg["Amarillas"].notna().any():  metrics_available.append(("🟨 Amarillas",     "Amarillas", "#FF9800"))

    if not metrics_available:
        st.info("No hay métricas disponibles para este CSV.")
        return

    # Tabla completa con posición de standings
    st.markdown("#### 📋 Tabla completa de equipos")
    pos_map = standings["Pos"].to_dict()
    agg_display = agg.copy()
    agg_display.insert(0, "Pos", agg_display.index.map(pos_map).fillna("-").astype(str))
    agg_display = agg_display.sort_values("Pos", key=lambda x: pd.to_numeric(x, errors='coerce'))

    def color_top(val):
        try:
            v = float(val)
            return "color:#4CAF50;font-weight:700" if v > 0 else ""
        except: return ""

    st.dataframe(agg_display.reset_index().rename(columns={"team":"Equipo"}),
                 use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 🏆 Rankings por métrica (top 8)")

    # Bar charts de ranking
    for i in range(0, len(metrics_available), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j >= len(metrics_available): break
            label, col_name, color = metrics_available[i+j]
            sorted_agg = agg[col_name].dropna().sort_values(ascending=False).head(8)
            if sorted_agg.empty: continue

            fig = go.Figure(go.Bar(
                y=sorted_agg.index.tolist(),
                x=sorted_agg.values.tolist(),
                orientation='h',
                marker_color=color,
                text=[f"{v:.2f}" for v in sorted_agg.values],
                textposition='outside',
            ))
            fig.update_layout(
                title=dict(text=f"{label} — promedio por partido", font=dict(size=12)),
                xaxis=dict(gridcolor="#1f2333"),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white", size=11),
                height=320, margin=dict(l=5,r=70,t=42,b=5),
                showlegend=False,
            )
            col.plotly_chart(fig, use_container_width=True, key=_ck())

    # Nota sobre atajadas inferidas
    if agg["Atajadas"].notna().any():
        st.caption(
            "🧤 **Atajadas**: si no hay datos de portero (HGS/AGS), se calculan como "
            "*remates al arco del rival − goles del rival* (approx. confiable cuando hay datos de SOT)."
        )


# ══════════════════════════════════════════════════════════════
# NAVEGACIÓN CELULAR FIJA CON NÚMEROS 1-2-3-4
# ══════════════════════════════════════════════════════════════

def sync_vista_from_url():
    """Lee ?vista=N desde la URL para que los botones flotantes funcionen."""
    try:
        v = st.query_params.get("vista", None)
        if isinstance(v, list):
            v = v[0] if v else None
        if v is not None:
            idx = int(v)
            if 0 <= idx <= 3:
                st.session_state["vista_idx"] = idx
    except Exception:
        pass


def set_vista_idx(idx):
    """Guarda la vista actual y la sincroniza en la URL."""
    idx = int(idx) % 4
    st.session_state["vista_idx"] = idx
    try:
        st.query_params["vista"] = str(idx)
    except Exception:
        pass


def render_sticky_mobile_nav(vista_idx, casos):
    """Barra flotante fija con números 1-2-3-4 para cambiar de caso."""
    labels = ["Local General", "Local Contexto", "Visitante General", "Visitante Contexto"]
    
    st.markdown(f"""
    <style>
    .mobile-floating-nav {{
        position: fixed;
        top: 3.8rem;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999999;
        background: rgba(15, 23, 35, 0.98);
        border: 2px solid #00e676;
        border-radius: 50px;
        padding: 8px 12px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.6);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        gap: 6px;
        width: 92%;
        max-width: 380px;
    }}
    .nav-number {{
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 1.1rem;
        border-radius: 50%;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.2s;
    }}
    .nav-number-active {{
        background: #00e676 !important;
        color: #0d1117 !important;
        box-shadow: 0 0 0 4px rgba(0, 230, 118, 0.3);
    }}
    .nav-number-inactive {{
        background: #1f2937;
        color: #9ca3af;
        border: 1px solid #374151;
    }}
    .mobile-nav-spacer {{ height: 78px; }}
    </style>

    <div class="mobile-floating-nav">
    """, unsafe_allow_html=True)

    for i in range(4):
        active = "nav-number-active" if i == vista_idx else "nav-number-inactive"
        st.markdown(f"""
        <a href="?vista={i}" target="_self" class="nav-number {active}">
            {i+1}
        </a>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="margin-left: 12px; color:#9ca3af; font-size:0.82rem; font-weight:600;">
            {labels[vista_idx]}
        </div>
    </div>
    <div class="mobile-nav-spacer"></div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    try:
        archivos = sorted([f for f in os.listdir(FOLDER) if f.endswith(".csv")])
    except Exception:
        st.error("❌ Carpeta no encontrada.\nVerifica el path FOLDER."); st.stop()
    if not archivos:
        st.error("No hay archivos CSV en la carpeta."); st.stop()

    archivo_sel = st.selectbox("📂 Archivo CSV", archivos,
                                format_func=lambda x: x.replace(".csv","").replace("_"," ").title())
    liga_nombre = archivo_sel.replace(".csv","").replace("_"," ").title()
    data_path   = os.path.join(FOLDER, archivo_sel)

    st.markdown("---")
    with st.spinner("⚙️ Cargando datos..."):
        resultado = load_and_process(data_path)

    if resultado[0] is None:
        st.error("❌ Formato CSV no reconocido."); st.stop()

    df, standings, fmt = resultado

    # Detectar disponibilidad (incluyendo atajadas inferidas)
    TIENE_CUOTAS   = df["odd_h"].notna().sum() > 0
    TIENE_CORNERS  = df["home_corner_kicks"].notna().sum() > 0
    TIENE_REMATES  = df["home_total_shots"].notna().sum() > 0
    TIENE_ATAJADAS = df["HomeGK_Saves"].notna().sum() > 0  # ya incluye inferidas
    tiene = {"cuotas":TIENE_CUOTAS,"corners":TIENE_CORNERS,"remates":TIENE_REMATES,"atajadas":TIENE_ATAJADAS}

    # Detectar si son inferidas o reales
    tiene_saves_real = df["home_goalkeeper_saves"].notna().sum() > 0 and \
                       not (df["home_goalkeeper_saves"] == df["home_inferred_saves"]).all()

    st.success(f"✅ {len(df)} partidos cargados")
    st.caption(f"📅 {df['fecha'].min().date()} → {df['fecha'].max().date()}")
    st.caption(f"🔍 {fmt}")
    cols=st.columns(2)
    cols[0].markdown(f"{'✅' if TIENE_CUOTAS  else '❌'} Cuotas")
    cols[1].markdown(f"{'✅' if TIENE_CORNERS else '❌'} Córners")
    cols[0].markdown(f"{'✅' if TIENE_REMATES else '❌'} Remates")
    ataj_label = "✅ Atajadas" if tiene_saves_real else ("🔶 Ataj. (inf.)" if TIENE_ATAJADAS else "❌ Atajadas")
    cols[1].markdown(ataj_label)

    st.markdown("---")
    teams    = list(standings.index)
    fmt_team = lambda t: f"{int(standings.loc[t,'Pos'])}. {t}  ({int(standings.loc[t,'PTS'])}pts)"
    home_sel = st.selectbox("🏠 Equipo LOCAL",      teams, index=0, format_func=fmt_team)
    away_sel = st.selectbox("✈️  Equipo VISITANTE", teams, index=min(1,len(teams)-1), format_func=fmt_team)
    UMBRAL   = st.slider("Umbral puntos (contexto)", 5, 20, 10, 1)
    analizar = st.button("🔍 Analizar partido", type="primary", use_container_width=True)

    st.markdown("---")
    vista_uso = st.radio(
        "🖥️/📱 Vista de uso",
        ["🖥️ PC / escritorio", "📱 Celular"],
        index=0,
        help="PC mantiene las pestañas. Celular usa una sola pantalla con números 1-4 fijos arriba."
    )
    MODO_CELULAR = vista_uso.startswith("📱")
    st.caption("La misma app funciona en ambos: usa PC en computadora y Celular en teléfono.")

    if "vista_idx" not in st.session_state:
        st.session_state["vista_idx"] = 0
    sync_vista_from_url()

    VISTA_LABELS_SIDE = [
        "🏠 Local general",
        "⭐ Local según contexto",
        "✈️ Visitante general",
        "🎯 Visitante según contexto",
    ]

    if MODO_CELULAR:
        st.markdown("### 🧭 Navegación")
        nav_prev, nav_next = st.columns(2)
        with nav_prev:
            if st.button("⬅️ Atrás", key="side_prev", use_container_width=True):
                set_vista_idx(st.session_state["vista_idx"] - 1)
                st.rerun()
        with nav_next:
            if st.button("Next ➡️", key="side_next", use_container_width=True):
                set_vista_idx(st.session_state["vista_idx"] + 1)
                st.rerun()

        vista_idx_side = st.selectbox(
            "Saltar a vista",
            options=list(range(4)),
            index=st.session_state["vista_idx"],
            format_func=lambda i: VISTA_LABELS_SIDE[i],
            key="vista_idx_selector",
        )
        set_vista_idx(vista_idx_side)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

st.markdown('<p class="main-title">⚽ Análisis de Fútbol</p>', unsafe_allow_html=True)

# ── Pantalla inicial ──────────────────────────────────────
if not analizar and "home_analyzed" not in st.session_state:
    st.markdown(f"### 🏆 Tabla de posiciones — {liga_nombre}")
    sd=standings.copy().reset_index()
    sd.columns=["Equipo","Pos","PJ","G","E","P","GF","GC","DG","PTS"]
    sd=sd[["Pos","Equipo","PJ","G","E","P","GF","GC","DG","PTS"]]
    def color_pos(row):
        p=row["Pos"]; n=len(sd)
        if p<=4:   return ["background-color:#1a3a1a"]*len(row)
        if p<=6:   return ["background-color:#1a2a3a"]*len(row)
        if p>=n-2: return ["background-color:#3a1a1a"]*len(row)
        return [""]*len(row)
    st.dataframe(sd.style.apply(color_pos,axis=1), use_container_width=True, hide_index=True, height=620)
    st.markdown("---")
    with st.expander("📊 Estadísticas comparativas de la liga", expanded=False):
        display_liga_stats(df, standings, tiene, data_path)
    st.info("👈 Selecciona los equipos y presiona **Analizar partido**")
    st.stop()

if analizar:
    st.session_state["home_analyzed"]=home_sel
    st.session_state["away_analyzed"]=away_sel
    st.session_state["umbral_saved"] =UMBRAL
    st.session_state["vista_idx"] = 0

HOME_TEAM=st.session_state.get("home_analyzed",home_sel)
AWAY_TEAM=st.session_state.get("away_analyzed",away_sel)
UMBRAL_S =st.session_state.get("umbral_saved", UMBRAL)

# Contexto
home_pts=int(standings.loc[HOME_TEAM,"PTS"]); away_pts=int(standings.loc[AWAY_TEAM,"PTS"])
home_pos=int(standings.loc[HOME_TEAM,"Pos"]); away_pos=int(standings.loc[AWAY_TEAM,"Pos"])
diff_pts=home_pts-away_pts

if diff_pts>=UMBRAL_S:
    contexto="FAVORITO"; ctx_class="favorito"; ctx_emoji="⭐"
    ctx_txt=f"Local FAVORITO — {HOME_TEAM} {home_pts}pts vs {AWAY_TEAM} {away_pts}pts (diff +{diff_pts})"
elif diff_pts<=-UMBRAL_S:
    contexto="UNDERDOG"; ctx_class="underdog"; ctx_emoji="💪"
    ctx_txt=f"Local UNDERDOG — {HOME_TEAM} {home_pts}pts vs {AWAY_TEAM} {away_pts}pts (diff {diff_pts})"
else:
    contexto="REÑIDO"; ctx_class="renido"; ctx_emoji="⚔️"
    ctx_txt=f"Partido REÑIDO — {HOME_TEAM} {home_pts}pts vs {AWAY_TEAM} {away_pts}pts (diff {diff_pts:+d})"

contexto_v={"FAVORITO":"UNDERDOG","UNDERDOG":"FAVORITO","REÑIDO":"REÑIDO"}[contexto]

ch,cv_col,ca=st.columns([5,1,5])
with ch:   st.markdown(f"### 🏠 {HOME_TEAM}"); st.caption(f"#{home_pos} · {home_pts} pts")
with cv_col: st.markdown("### vs")
with ca:   st.markdown(f"### ✈️ {AWAY_TEAM}"); st.caption(f"#{away_pos} · {away_pts} pts")
st.markdown(f'<div class="ctx-badge {ctx_class}">{ctx_emoji} {ctx_txt}</div>', unsafe_allow_html=True)

# Liga stats colapsable encima de los tabs
with st.expander("📊 Estadísticas comparativas de la liga", expanded=False):
    display_liga_stats(df, standings, tiene, data_path)

st.markdown("---")

# Filtrar casos
df_c1=df[df["home"]==HOME_TEAM].copy()
df_c3=df[df["away"]==AWAY_TEAM].copy()

def filter_ctx(base_df, ctx, umbral, is_visitante=False):
    ids=[]
    for idx,row in base_df.iterrows():
        if is_visitante:
            l_=row.get("hist_pts_home",np.nan); v_=row.get("hist_pts_away",np.nan)
            if pd.isna(l_) or pd.isna(v_): continue
            diff_=int(v_)-int(l_)
        else:
            h_=row.get("hist_pts_home",np.nan); a_=row.get("hist_pts_away",np.nan)
            if pd.isna(h_) or pd.isna(a_): continue
            diff_=int(h_)-int(a_)
        if   ctx=="FAVORITO" and diff_>= umbral: ids.append(idx)
        elif ctx=="UNDERDOG" and diff_<=-umbral: ids.append(idx)
        elif ctx=="REÑIDO"   and -umbral<diff_<umbral: ids.append(idx)
    return df.loc[ids].copy() if ids else pd.DataFrame()

df_c2=filter_ctx(df_c1,contexto,  UMBRAL_S,is_visitante=False)
df_c4=filter_ctx(df_c3,contexto_v,UMBRAL_S,is_visitante=True)

ctx_label  ={"FAVORITO":f"⭐ Fav.(≥{UMBRAL_S}pts)","UNDERDOG":f"💪 Underdog(≥{UMBRAL_S}pts)","REÑIDO":f"⚔️ Reñido(<{UMBRAL_S}pts)"}
ctx_v_label={"FAVORITO":f"⭐ Fav.V(≥{UMBRAL_S}pts)","UNDERDOG":f"💪 UnderdogV(≥{UMBRAL_S}pts)","REÑIDO":f"⚔️ ReñidoV(<{UMBRAL_S}pts)"}

casos = [
    (f"🏠 {HOME_TEAM} LOCAL — general ({len(df_c1)}pj)", df_c1, HOME_TEAM, False),
    (f"⭐ {HOME_TEAM} LOCAL — {ctx_label[contexto]} ({len(df_c2)}pj)", df_c2, HOME_TEAM, False),
    (f"✈️ {AWAY_TEAM} VISITA — general ({len(df_c3)}pj)", df_c3, AWAY_TEAM, True),
    (f"🎯 {AWAY_TEAM} VISITA — {ctx_v_label[contexto_v]} ({len(df_c4)}pj)", df_c4, AWAY_TEAM, True),
]

if MODO_CELULAR:
    vista_idx = int(st.session_state.get("vista_idx", 0))
    vista_idx = max(0, min(3, vista_idx))
    titulo, df_case, team_case, es_visitante_case = casos[vista_idx]

    render_sticky_mobile_nav(vista_idx, casos)
    
    st.markdown(f"### {titulo}")
    st.caption("📱 Usa los números 1-4 para cambiar rápidamente de vista")
    display_caso(df_case, team_case, es_visitante_case, tiene)

else:
    tab1,tab2,tab3,tab4=st.tabs([
        f"🏠 {HOME_TEAM[:14]} LOCAL  (general, {len(df_c1)}pj)",
        f"🏠 {HOME_TEAM[:14]} LOCAL  {ctx_label[contexto]}  ({len(df_c2)}pj)",
        f"✈️ {AWAY_TEAM[:14]} VISITA (general, {len(df_c3)}pj)",
        f"✈️ {AWAY_TEAM[:14]} VISITA {ctx_v_label[contexto_v]} ({len(df_c4)}pj)",
    ])

    with tab1: display_caso(df_c1, HOME_TEAM, False, tiene)
    with tab2: display_caso(df_c2, HOME_TEAM, False, tiene)
    with tab3: display_caso(df_c3, AWAY_TEAM, True,  tiene)
    with tab4: display_caso(df_c4, AWAY_TEAM, True,  tiene)
