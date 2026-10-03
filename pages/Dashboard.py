from pathlib import Path
import dash
from dash import html, dcc, Input, Output, callback, ctx 
import plotly.express as px
import pandas as pd


dash.register_page(
    __name__,
    path="/dashboard",
    title="Dashboard"
)

BASE_DIR = Path(__file__).resolve().parent.parent

df_hist = pd.read_excel(
    BASE_DIR / "data" / "histórico_filtrado_proc.xlsx"
)
# ==============================
# MESES EN ESPAÑOL
# ==============================

meses_numero = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

meses_es = {
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre"
}

df_hist["Mes_numero"] = df_hist["nMes"].map(meses_numero)
df_hist["Mes_nombre"] = df_hist["nMes"].map(meses_es)
df_eq = pd.read_excel(
    BASE_DIR / "data" / "equipos_proc.xlsx"
)

# ==============================
# KPIs
# ==============================

total_avisos = len(df_hist)

total_equipos = len(df_eq)

cerrados = len(
    df_hist[df_hist["Estado aviso"] == "Cerrado"]
)

pct_cerrados = round(
    (cerrados / total_avisos) * 100,
    1
)

abiertos = len(
    df_hist[df_hist["Estado aviso"] == "Abierto"]
)

pct_abiertos = round(
    (abiertos / total_avisos) * 100,
    1
)

# ==============================
# GRÁFICA 1 - EVOLUCIÓN DE AVISOS
# ==============================

df_line = (
    df_hist.groupby(["Año", "Tipo de aviso"])
    .size()
    .reset_index(name="Cantidad")
)

df_top = df_line[
    df_line["Tipo de aviso"].isin(["Vegetación", "Construcciones"])
]

df_oth = (
    df_line[
        ~df_line["Tipo de aviso"].isin(["Vegetación", "Construcciones"])
    ]
    .groupby("Año")["Cantidad"]
    .sum()
    .reset_index()
)

df_oth["Tipo de aviso"] = "Otros"

df_line_final = pd.concat(
    [df_top, df_oth]
).sort_values("Año")


fig_line = px.line(
    df_line_final,
    x="Año",
    y="Cantidad",
    color="Tipo de aviso",
    markers=True,
    custom_data=["Tipo de aviso"],
    color_discrete_map={
        "Vegetación": "#2A9D8F",
        "Construcciones": "#E9A23B",
        "Otros": "#17324D"
    },
    template="plotly_white"
)

fig_line.update_layout(
    margin=dict(l=20, r=15, t=10, b=70),
    height=260,

    xaxis=dict(
        title=dict(
            text="Año",
            standoff=12
        )
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.30,
        xanchor="center",
        x=0.5
    )
)


# ==============================
# GRÁFICA 2 - DISTRIBUCIÓN POLAR
# ==============================

meses_es = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

df_hist["Mes_nombre"] = df_hist["Mes"].map(meses_es)


df_polar = (
    df_hist.groupby(
        ["Mes_numero", "Mes_nombre", "Tipo de aviso"]
    )
    .size()
    .reset_index(name="Cantidad")
)

df_polar_top = df_polar[
    df_polar["Tipo de aviso"].isin(["Vegetación", "Construcciones"])
]

df_polar_oth = (
    df_polar[
        ~df_polar["Tipo de aviso"].isin(["Vegetación", "Construcciones"])
    ]
    .groupby(["Mes_numero", "Mes_nombre"])["Cantidad"]
    .sum()
    .reset_index()
)

df_polar_oth["Tipo de aviso"] = "Otros"

df_polar_final = pd.concat(
    [df_polar_top, df_polar_oth]
).sort_values("Mes_numero")


fig_polar = px.line_polar(
    df_polar_final,
    r="Cantidad",
    theta="Mes_nombre",
    color="Tipo de aviso",
    line_close=True,

    category_orders={
        "Mes_nombre": [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]
    },

    color_discrete_map={
        "Vegetación": "#2A9D8F",
        "Construcciones": "#E9A23B",
        "Otros": "#17324D"
    },

    template="plotly_white"
)

fig_polar.update_layout(
    margin=dict(l=20, r=20, t=10, b=20),
    height=260,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.30,
        xanchor="center",
        x=0.5
    )
)

layout = html.Div([

    # Encabezado del dashboard
    html.Div(
        className="card-banner dashboard-banner",
        children=[

            html.Img(
                src="/assets/logo.png",
                style={
                    "width": "95px",
                    "marginBottom": "2px"
                }
            ),

            html.H2(
                "Dashboard Operativo",
                style={
                    "color": "#17324D",
                    "marginTop":"2px",
                    "marginBottom":"2px",
                    "fontSize":"26px"
                }
            ),

            html.P(
                "Indicadores principales para el seguimiento de avisos y equipos.",
                className="banner-text"
            )
        ]
    ),
    html.Div(
    [
        html.P(
            "Este tablero consolida los principales indicadores de avisos y equipos, "
            "permitiendo analizar su evolución, distribución temporal y comportamiento "
            "operativo para apoyar la toma de decisiones.",
            style={
                "margin": "0",
                "fontSize": "13px",
                "color": "#607080",
                "lineHeight": "1.5"
            }
        )
    ],
    style={
        "margin": "8px 0 10px 0",
        "padding": "10px 14px",
        "backgroundColor": "#F8FAFC",
        "borderLeft": "4px solid #2A9D8F",
        "borderRadius": "6px"
    }
),

html.Div(
    [
        html.Span(
            "Filtro activo: Vista general",
            id="texto-filtro-activo",
            style={
                "fontSize": "13px",
                "fontWeight": "bold",
                "color": "#17324D"
            }
        ),

        html.Button(
            "Limpiar filtros",
            id="btn-limpiar-filtros",
            n_clicks=0,
            style={
                "marginLeft": "auto",
                "padding": "6px 12px",
                "border": "none",
                "borderRadius": "6px",
                "backgroundColor": "#17324D",
                "color": "white",
                "cursor": "pointer",
                "fontSize": "12px"
            }
        )
    ],
    style={
        "display": "flex",
        "alignItems": "center",
        "gap": "10px",
        "margin": "6px 0 10px 0"
    }
),
    # Grilla de KPIs
    html.Div(
        className="kpi-grid",
        children=[

            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        "📄",
                        className="kpi-icon"
                    ),

                    html.Div([
                        html.H3(
                            f"{total_avisos:,}".replace(",", "."),
                            id="kpi-total-avisos",
                            className="kpi-value-main"
                        ),

                        html.Span(
                            "Avisos históricos",
                            className="kpi-label"
                        )
                    ])
                ]
            ),

            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        "🗼",
                        className="kpi-icon"
                    ),

                    html.Div([
                        html.H3(
                            f"{total_equipos:,}".replace(",", "."),
                            id="kpi-total-equipos",
                            className="kpi-value-main"
                        ),

                        html.Span(
                            "Equipos georreferenciados",
                            className="kpi-label"
                        )
                    ])
                ]
            ),

            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        "✔️",
                        className="kpi-icon"
                    ),

                    html.Div([
                        html.H3(
                            f"{pct_cerrados}%".replace(".", ","),
                            id="kpi-cerrados",
                            className="kpi-value-green"
                        ),

                        html.Span(
                            "Avisos cerrados",
                            className="kpi-label"
                        )
                    ])
                ]
            ),

            html.Div(
                className="kpi-card",
                children=[
                    html.Div(
                        "🕒",
                        className="kpi-icon"
                    ),

                    html.Div([
                        html.H3(
                            f"{pct_abiertos}%".replace(".", ","),
                            id="kpi-abiertos",
                            className="kpi-value-red"
                        ),

                        html.Span(
                            "Avisos abiertos",
                            className="kpi-label"
                        )
                    ])
                ]
            )

                ]
    ),

    # ==============================
    # GRÁFICAS
    # ==============================

    html.Div(
        className="charts-grid-2col",
        children=[

            # Gráfica de líneas
            html.Div(
                className="chart-card",
                children=[

                    html.H4(
                        "Evolución de avisos por año",
                        className="chart-title"
                    ),

                    html.P(
                    "Desde 2017 Vegetación supera cada año a Construcciones y llega a su máximo en 2022",
                    style={
                        "color": "#607080",
                        "fontSize": "12px",
                        "marginTop": "-4px",
                        "marginBottom": "10px",
                            },
                    ),

                    dcc.Graph(
                        id="grafica-lineas-dashboard",
                        figure=fig_line,
                        config={
                            "displayModeBar": False
                        }
                    )

                ]
            ),

            # Gráfica polar
            html.Div(
                className="chart-card",
                children=[

                    html.H4(
                        "Distribución mensual de avisos",
                        className="chart-title"),
                    html.P(
                    "Mayo y junio concentran los avisos de Vegetación; el pico de septiembre en Construcciones proviene de un solo día de registro",
                    style={
                        "color": "#607080",
                        "fontSize": "12px",
                        "marginTop": "-4px",
                        "marginBottom": "10px",
                            },
                    ),

                    dcc.Graph(
                        id="grafica-polar-dashboard",
                        figure=fig_polar,
                        config={
                            "displayModeBar": False
                        }
                    )

                ]
            )

        ]
    )

])
# ==========================================================
# INTERACTIVIDAD DEL DASHBOARD
# Línea -> Año + Tipo
# Polar -> Año + Tipo + Mes
# ==========================================================

@callback(
    Output("kpi-total-avisos", "children"),
    Output("kpi-total-equipos", "children"),
    Output("kpi-cerrados", "children"),
    Output("kpi-abiertos", "children"),
    Output("grafica-polar-dashboard", "figure"),
    Output("texto-filtro-activo", "children"),

    Input("grafica-lineas-dashboard", "clickData"),
    Input("grafica-polar-dashboard", "clickData"),
    Input("btn-limpiar-filtros", "n_clicks")
)
def actualizar_dashboard(click_linea, click_polar, n_clicks):

    # =========================================
    # LIMPIAR FILTROS
    # =========================================

    if ctx.triggered_id == "btn-limpiar-filtros":

        return (
            f"{total_avisos:,}".replace(",", "."),
            f"{total_equipos:,}".replace(",", "."),
            f"{pct_cerrados}%".replace(".", ","),
            f"{pct_abiertos}%".replace(".", ","),
            fig_polar,
            "Filtro activo: Vista general"
        )

    # =========================================
    # VISTA GENERAL
    # =========================================

    if click_linea is None:

        return (
            f"{total_avisos:,}".replace(",", "."),
            f"{total_equipos:,}".replace(",", "."),
            f"{pct_cerrados}%".replace(".", ","),
            f"{pct_abiertos}%".replace(".", ","),
            fig_polar,
            "Filtro activo: Vista general"
        )

    # =========================================
    # AÑO + TIPO DESDE GRÁFICA DE LÍNEAS
    # =========================================

    anio = click_linea["points"][0]["x"]

    tipo = click_linea["points"][0]["customdata"][0]

    datos = df_hist[
        df_hist["Año"] == anio
    ].copy()

    if tipo == "Otros":

        datos = datos[
            ~datos["Tipo de aviso"].isin(
                ["Vegetación", "Construcciones"]
            )
        ]

    else:

        datos = datos[
            datos["Tipo de aviso"] == tipo
        ]

    # Texto inicial del filtro
    texto_filtro = f"Filtro activo: {anio} · {tipo}"

    # =========================================
    # CREAR POLAR PARA AÑO + TIPO
    # =========================================

    polar_filtrada = (
        datos.groupby(["Mes", "Mes_nombre"])
        .size()
        .reset_index(name="Cantidad")
        .sort_values("Mes")
    )

    fig_polar_filtrada = px.line_polar(
        polar_filtrada,
        r="Cantidad",
        theta="Mes_nombre",
        line_close=True,
        markers=True,
        template="plotly_white"
    )

    fig_polar_filtrada.update_traces(
        line_color="#2A9D8F",
        fill="toself"
    )

    fig_polar_filtrada.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20
        ),
        height=260,

        title={
            "text": f"{tipo} · {anio}",
            "x": 0.5,
            "xanchor": "center",
                "y": 0.98,
                 "yanchor": "top",
                "pad": {
                "b": 10
            },
            "font": {
                "size": 14,
                "color": "#17324D"
            }
        },

        polar=dict(
            radialaxis=dict(
                visible=True,
                rangemode="tozero"
            ),
            angularaxis=dict(
                direction="clockwise"
            )
        ),

        showlegend=False
    )

    # =========================================
    # SI EL CLIC FUE EN LA POLAR:
    # AÑO + TIPO + MES
    # =========================================

    if (
        ctx.triggered_id == "grafica-polar-dashboard"
        and click_polar is not None
    ):

        mes = click_polar["points"][0]["theta"]

        datos = datos[
            datos["Mes_nombre"].astype(str) == str(mes)
        ]

        texto_filtro = (
            f"Filtro activo: {anio} · {tipo} · {mes}"
        )

        fig_polar_filtrada.update_layout(
            title={
                "text": f"{tipo} · {anio} · {mes}",
                "x": 0.5,
                "xanchor": "center",
                "y":0.98,
                "yanchor":"top",
                "font": {
                    "size": 14,
                    "color": "#17324D"
                }
            }
        )

    # =========================================
    # RECALCULAR KPI
    # =========================================

    total = len(datos)

    equipos = datos["Equipo"].nunique()

    cerrados_filtro = len(
        datos[
            datos["Estado aviso"] == "Cerrado"
        ]
    )

    abiertos_filtro = len(
        datos[
            datos["Estado aviso"] == "Abierto"
        ]
    )

    if total > 0:

        pct_cerrados_filtro = round(
            cerrados_filtro / total * 100,
            1
        )

        pct_abiertos_filtro = round(
            abiertos_filtro / total * 100,
            1
        )

    else:

        pct_cerrados_filtro = 0
        pct_abiertos_filtro = 0

    # =========================================
    # RETORNO
    # =========================================

    return (
        f"{total:,}".replace(",", "."),
        f"{equipos:,}".replace(",", "."),
        f"{pct_cerrados_filtro}%".replace(".", ","),
        f"{pct_abiertos_filtro}%".replace(".", ","),
        fig_polar_filtrada,
        texto_filtro
    )