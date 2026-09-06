"""
probabilidad_lineas.py
-----------------------
Se integra con tu Analisis_Futbol_2.py existente. No reemplaza nada, solo agrega
un cálculo nuevo sobre los DataFrames que vos ya generás (df_c1, df_c2, df_c3, df_c4)
y sobre el `cuotas_df` que devuelve tu `parse_betano_text()`.

QUÉ HACE:
1) Para cada línea parseada de Betano (goles, remates, tiros_al_arco, corners —
   se ignoran tarjetas, btts, 1x2 y faltas porque no los pediste) calcula el %
   histórico de veces que esa línea se hubiera cumplido, combinando:
     - scope "total": el historial del LOCAL jugando de local + el historial
       del VISITANTE jugando de visita, agrupados en una sola bolsa (pool).
     - scope "home": solo el historial propio del equipo LOCAL.
     - scope "away": solo el historial propio del equipo VISITANTE.
2) Ordena TODO de mayor a menor probabilidad histórica (sin filtrar por ningún
   umbral tipo 80%, como pediste).
3) Si cargás 2 o más partidos, arma una combinada tomando la línea de mayor
   probabilidad de CADA partido y te da la cuota combinada (producto de cuotas)
   y la probabilidad combinada (producto de probabilidades, asumiendo
   independencia entre partidos).

Requiere que tus DataFrames tengan las columnas normalizadas que ya usa tu app:
    home_goals, away_goals,
    home_total_shots, away_total_shots,
    home_shots_on_target, away_shots_on_target,
    home_corner_kicks, away_corner_kicks

Y que `cuotas_df` tenga las columnas que ya devuelve tu parser:
    match, home, away, market, scope, side, line, odds
"""

import pandas as pd
import numpy as np

# Mercados que nos interesan (se ignora tarjetas, btts, 1x2, faltas, etc.)
MERCADOS_VALIDOS = {"goles", "remates", "tiros_al_arco", "corners"}

_COL_HOME = {
    "goles": "home_goals",
    "remates": "home_total_shots",
    "tiros_al_arco": "home_shots_on_target",
    "corners": "home_corner_kicks",
}
_COL_AWAY = {
    "goles": "away_goals",
    "remates": "away_total_shots",
    "tiros_al_arco": "away_shots_on_target",
    "corners": "away_corner_kicks",
}


def _serie(df, market, scope, lado):
    """
    lado: 'home' si el df es historial del equipo jugando de LOCAL,
          'away' si el df es historial del equipo jugando de VISITA
                 (ya con las columnas swapeadas, como hace tu swap_visitante()).
    """
    if df is None or df.empty:
        return pd.Series(dtype=float)

    h = pd.to_numeric(df.get(_COL_HOME[market]), errors="coerce")
    a = pd.to_numeric(df.get(_COL_AWAY[market]), errors="coerce")

    if scope == "total":
        return (h + a).dropna()
    if scope == "home":
        return h.dropna() if lado == "home" else pd.Series(dtype=float)
    if scope == "away":
        return a.dropna() if lado == "away" else pd.Series(dtype=float)
    return pd.Series(dtype=float)


def evaluar_cuotas(df_home_local, df_away_visita, cuotas_df, match_label=None):
    """
    df_home_local  : historial del equipo LOCAL jugando de local (ej. tu df_c1 o df_c2)
    df_away_visita : historial del equipo VISITANTE jugando de visita, YA SWAPEADO
                      (mismo formato que le pasás a build_match_df cuando es_visitante=True)
    cuotas_df      : filas de una sola tabla de Betano (match, home, away, market,
                      scope, side, line, odds)
    match_label    : nombre a mostrar para este partido (si no, usa row['match'])

    Devuelve un DataFrame con TODAS las líneas evaluadas, ordenado de mayor a
    menor probabilidad histórica.
    """
    filas = []
    for _, row in cuotas_df.iterrows():
        market, scope, side = row["market"], row["scope"], row["side"]
        line, odds = row["line"], row["odds"]

        if market not in MERCADOS_VALIDOS:
            continue
        if line == "" or pd.isna(line):
            continue
        if side not in ("over", "under"):
            continue

        line = float(line)

        if scope == "total":
            pool = pd.concat([
                _serie(df_home_local, market, "total", "home"),
                _serie(df_away_visita, market, "total", "away"),
            ])
        elif scope == "home":
            pool = _serie(df_home_local, market, "home", "home")
        elif scope == "away":
            pool = _serie(df_away_visita, market, "away", "away")
        else:
            continue

        n = len(pool)
        if n == 0:
            continue

        hits = int((pool > line).sum()) if side == "over" else int((pool < line).sum())
        prob_hist = hits / n

        try:
            odds_f = float(odds)
            prob_impl = 1 / odds_f
        except (TypeError, ValueError, ZeroDivisionError):
            odds_f, prob_impl = np.nan, np.nan

        filas.append({
            "partido": match_label or row.get("match", ""),
            "mercado": market,
            "scope": scope,
            "side": side,
            "linea": line,
            "cuota": odds_f,
            "cumplidos": hits,
            "fallidos": n - hits,
            "n_partidos": n,
            "prob_historica_%": round(prob_hist * 100, 1),
            "prob_implicita_%": round(prob_impl * 100, 1) if not np.isnan(prob_impl) else None,
            "valor_%": round((prob_hist - prob_impl) * 100, 1) if not np.isnan(prob_impl) else None,
        })

    out = pd.DataFrame(filas)
    if out.empty:
        return out
    return out.sort_values("prob_historica_%", ascending=False).reset_index(drop=True)


def mejor_linea_por_partido(df_ranking):
    """De un ranking con líneas de uno o varios partidos apilados, devuelve
    SOLO la línea de mayor probabilidad histórica de cada partido."""
    if df_ranking is None or df_ranking.empty:
        return pd.DataFrame()
    idx = df_ranking.groupby("partido")["prob_historica_%"].idxmax()
    return (
        df_ranking.loc[idx]
        .sort_values("prob_historica_%", ascending=False)
        .reset_index(drop=True)
    )


def armar_combinada(df_mejores):
    """
    df_mejores: una fila por partido (ej. la salida de mejor_linea_por_partido,
    o cualquier selección manual de una línea por partido).

    Devuelve la cuota combinada (producto de cuotas) y la probabilidad
    combinada (producto de probabilidades históricas, asumiendo independencia
    entre partidos — es una aproximación, no una certeza matemática).
    """
    if df_mejores is None or df_mejores.empty:
        return None

    cuota_total = float(df_mejores["cuota"].prod())
    prob_total = float((df_mejores["prob_historica_%"] / 100).prod() * 100)

    detalle = df_mejores[
        ["partido", "mercado", "scope", "side", "linea", "cuota", "prob_historica_%"]
    ].to_dict("records")

    return {
        "detalle": detalle,
        "cuota_combinada": round(cuota_total, 2),
        "probabilidad_combinada_%": round(prob_total, 1),
        "valor_estimado_%": round(prob_total - (100 / cuota_total), 1) if cuota_total else None,
    }
