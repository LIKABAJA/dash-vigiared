from pathlib import Path

import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# =========================================================
# REGISTRO DE LA PÁGINA
# =========================================================

dash.register_page(
    __name__,
    path="/grafico-cascada",
    name="Análisis de variación",
    title="Análisis de Variación de Avisos"
)


# =========================================================
# COLORES VIGÍARED
# =========================================================

AZUL = "#17324D"
AZUL_OSCURO = "#0B3B5A"
VERDE = "#2A9D8F"
AMBAR = "#E9A23B"
ROJO = "#D9534F"
GRIS = "#607080"
BORDE = "#E5E9ED"
FONDO = "#F4F6F8"
BLANCO = "#FFFFFF"


# =========================================================
# CARGA DE DATOS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

df_hist = pd.read_excel(
    BASE_DIR / "data" / "histórico_filtrado_proc.xlsx"
)


# =========================================================
# LIMPIEZA DE DATOS
# =========================================================

df_hist["Año"] = pd.to_numeric(
    df_hist["Año"],
    errors="coerce"
).astype("Int64")


df_hist["Tipo de aviso"] = (
    df_hist["Tipo de aviso"]
    .fillna("Sin clasificación")
    .astype(str)
    .str.strip()
)


df_hist["Estado aviso"] = (
    df_hist["Estado aviso"]
    .fillna("Sin estado")
    .astype(str)
    .str.strip()
)


df_hist["Equipo"] = (
    df_hist["Equipo"]
    .fillna("Sin equipo")
    .astype(str)
    .str.strip()
)


# =========================================================
# AÑOS DISPONIBLES
# =========================================================

anios = sorted(
    [
        int(anio)
        for anio in df_hist["Año"]
        .dropna()
        .unique()
    ]
)


# Solo años que tienen disponible el año inmediatamente anterior
anios_comparables = [
    anio
    for anio in anios
    if (anio - 1) in anios
]


if anios_comparables:
    anio_inicial = max(anios_comparables)
else:
    anio_inicial = None


# =========================================================
# FORMATO
# =========================================================

def formato_numero(valor):

    return f"{int(valor):,}".replace(",", ".")


def formato_variacion(valor):

    valor = int(valor)

    if valor > 0:
        return f"+{formato_numero(valor)}"

    return formato_numero(valor)


def formato_porcentaje(valor):

    if valor is None:
        return "N/A"

    signo = "+" if valor > 0 else ""

    return (
        f"{signo}{valor:.1f}%"
        .replace(".", ",")
    )


# =========================================================
# CALCULAR VARIACIÓN INTERANUAL
# =========================================================

def calcular_variacion(
    anio_actual,
    top_n=5
):

    anio_anterior = anio_actual - 1


    datos_anterior = df_hist[
        df_hist["Año"] == anio_anterior
    ].copy()


    datos_actual = df_hist[
        df_hist["Año"] == anio_actual
    ].copy()


    total_anterior = len(
        datos_anterior
    )

    total_actual = len(
        datos_actual
    )


    # =====================================================
    # RESUMEN POR TIPO DE AVISO
    # =====================================================

    anterior_tipo = (
        datos_anterior
        .groupby("Tipo de aviso")
        .size()
        .rename("Anterior")
    )


    actual_tipo = (
        datos_actual
        .groupby("Tipo de aviso")
        .size()
        .rename("Actual")
    )


    comparacion = pd.concat(
        [
            anterior_tipo,
            actual_tipo
        ],
        axis=1
    ).fillna(0)


    comparacion["Anterior"] = (
        comparacion["Anterior"]
        .astype(int)
    )


    comparacion["Actual"] = (
        comparacion["Actual"]
        .astype(int)
    )


    comparacion["Variacion"] = (
        comparacion["Actual"]
        - comparacion["Anterior"]
    )


    comparacion = (
        comparacion
        .reset_index()
    )


    comparacion["Impacto_abs"] = (
        comparacion["Variacion"]
        .abs()
    )


    comparacion = (
        comparacion
        .sort_values(
            "Impacto_abs",
            ascending=False
        )
    )


    # =====================================================
    # TOP DE CONTRIBUCIONES
    # =====================================================

    top = comparacion.head(
        top_n
    ).copy()


    resto = comparacion.iloc[
        top_n:
    ].copy()


    if not resto.empty:

        variacion_otros = int(
            resto["Variacion"]
            .sum()
        )

        if variacion_otros != 0:

            fila_otros = pd.DataFrame(
                {
                    "Tipo de aviso": [
                        "Otros tipos"
                    ],

                    "Anterior": [
                        int(
                            resto[
                                "Anterior"
                            ].sum()
                        )
                    ],

                    "Actual": [
                        int(
                            resto[
                                "Actual"
                            ].sum()
                        )
                    ],

                    "Variacion": [
                        variacion_otros
                    ],

                    "Impacto_abs": [
                        abs(
                            variacion_otros
                        )
                    ]
                }
            )

            top = pd.concat(
                [
                    top,
                    fila_otros
                ],
                ignore_index=True
            )


    # =====================================================
    # KPI
    # =====================================================

    variacion_total = (
        total_actual
        - total_anterior
    )


    if total_anterior > 0:

        pct_variacion = (
            variacion_total
            / total_anterior
            * 100
        )

    else:

        pct_variacion = None


    positivos = comparacion[
        comparacion["Variacion"] > 0
    ]


    negativos = comparacion[
        comparacion["Variacion"] < 0
    ]


    if not positivos.empty:

        principal_incremento = (
            positivos
            .sort_values(
                "Variacion",
                ascending=False
            )
            .iloc[0]
        )

    else:

        principal_incremento = None


    if not negativos.empty:

        principal_reduccion = (
            negativos
            .sort_values(
                "Variacion",
                ascending=True
            )
            .iloc[0]
        )

    else:

        principal_reduccion = None


    return {
        "anio_actual":
            anio_actual,

        "anio_anterior":
            anio_anterior,

        "total_actual":
            total_actual,

        "total_anterior":
            total_anterior,

        "variacion_total":
            variacion_total,

        "pct_variacion":
            pct_variacion,

        "comparacion":
            comparacion,

        "top":
            top,

        "principal_incremento":
            principal_incremento,

        "principal_reduccion":
            principal_reduccion
    }


# =========================================================
# GRÁFICA CASCADA
# =========================================================

def crear_cascada(
    resultado
):

    anio_actual = (
        resultado[
            "anio_actual"
        ]
    )

    anio_anterior = (
        resultado[
            "anio_anterior"
        ]
    )

    total_anterior = (
        resultado[
            "total_anterior"
        ]
    )

    total_actual = (
        resultado[
            "total_actual"
        ]
    )

    top = (
        resultado[
            "top"
        ]
        .copy()
    )


    categorias = [
        str(anio_anterior)
    ]

    medidas = [
        "absolute"
    ]

    valores = [
        total_anterior
    ]

    textos = [
        formato_numero(
            total_anterior
        )
    ]

    customdata = [
        [
            "Total inicial",
            total_anterior,
            total_anterior,
            0
        ]
    ]


    # =====================================================
    # CONTRIBUCIONES
    # =====================================================

    for _, fila in top.iterrows():

        tipo = fila[
            "Tipo de aviso"
        ]

        anterior = int(
            fila["Anterior"]
        )

        actual = int(
            fila["Actual"]
        )

        variacion = int(
            fila["Variacion"]
        )


        categorias.append(
            tipo
        )

        medidas.append(
            "relative"
        )

        valores.append(
            variacion
        )

        textos.append(
            formato_variacion(
                variacion
            )
        )

        customdata.append(
            [
                tipo,
                anterior,
                actual,
                variacion
            ]
        )


    # =====================================================
    # TOTAL FINAL
    # =====================================================

    categorias.append(
        str(anio_actual)
    )

    medidas.append(
        "total"
    )

    valores.append(
        total_actual
    )

    textos.append(
        formato_numero(
            total_actual
        )
    )

    customdata.append(
        [
            "Total final",
            total_actual,
            total_actual,
            resultado[
                "variacion_total"
            ]
        ]
    )


    fig = go.Figure(

        go.Waterfall(

            name="Avisos",

            orientation="v",

            measure=medidas,

            x=categorias,

            y=valores,

            text=textos,

            textposition="outside",

            customdata=customdata,

            connector={
                "line": {
                    "color": BORDE,
                    "width": 1
                }
            },

            increasing={
                "marker": {
                    "color": VERDE
                }
            },

            decreasing={
                "marker": {
                    "color": ROJO
                }
            },

            totals={
                "marker": {
                    "color": AZUL
                }
            },

            hovertemplate=(

                "<b>%{customdata[0]}</b>"
                "<br><br>"

                "Año anterior: "
                "%{customdata[1]:,.0f}"
                "<br>"

                "Año actual: "
                "%{customdata[2]:,.0f}"
                "<br>"

                "Variación: "
                "%{customdata[3]:+,.0f}"

                "<extra></extra>"
            )
        )
    )


    fig.update_layout(

        height=420,

        margin=dict(
            l=45,
            r=25,
            t=65,
            b=70
        ),

        title={

            "text": (
                "Contribución por tipo de aviso "
                f"· {anio_anterior} → {anio_actual}"
            ),

            "x": 0.02,

            "xanchor": "left",

            "font": {
                "size": 17,
                "color": AZUL
            }
        },

        xaxis=dict(

            title=None,

            tickfont=dict(
                size=11,
                color=GRIS
            )
        ),

        yaxis=dict(

            title="Cantidad de avisos",

            rangemode="tozero",

            gridcolor=BORDE,

            zeroline=False,

            tickfont=dict(
                size=11,
                color=GRIS
            )
        ),

        plot_bgcolor=BLANCO,

        paper_bgcolor=BLANCO,

        showlegend=False
    )


    return fig


# =========================================================
# GRÁFICA DE LÍNEAS
# % CERRADOS / % ABIERTOS
# =========================================================

def crear_linea_estado(
    anio_seleccionado=None
):

    # =====================================================
    # PREPARACIÓN
    # =====================================================

    datos_estado = (
        df_hist
        .dropna(
            subset=["Año"]
        )
        .copy()
    )


    datos_estado["Estado_normalizado"] = (

        datos_estado[
            "Estado aviso"
        ]

        .astype(str)

        .str.strip()

        .str.lower()
    )


    datos_estado = datos_estado[
        datos_estado[
            "Estado_normalizado"
        ].isin(
            [
                "cerrado",
                "abierto"
            ]
        )
    ].copy()


    # =====================================================
    # CANTIDADES
    # =====================================================

    resumen = (
        datos_estado
        .groupby(
            [
                "Año",
                "Estado_normalizado"
            ]
        )
        .size()
        .reset_index(
            name="Cantidad"
        )
    )


    # =====================================================
    # TOTAL POR AÑO
    # =====================================================

    totales = (
        resumen
        .groupby("Año")[
            "Cantidad"
        ]
        .sum()
        .reset_index(
            name="Total"
        )
    )


    resumen = resumen.merge(
        totales,
        on="Año",
        how="left"
    )


    # =====================================================
    # PORCENTAJE
    # =====================================================

    resumen["Porcentaje"] = (
        resumen["Cantidad"]
        / resumen["Total"]
        * 100
    )


    resumen["Estado"] = (
        resumen[
            "Estado_normalizado"
        ]
        .map(
            {
                "cerrado":
                    "Cerrados",

                "abierto":
                    "Abiertos"
            }
        )
    )


    # =====================================================
    # GARANTIZAR AMBOS ESTADOS
    # =====================================================

    lista_anios = sorted(
        [
            int(a)
            for a in resumen["Año"]
            .dropna()
            .unique()
        ]
    )


    indice_completo = (
        pd.MultiIndex
        .from_product(
            [
                lista_anios,

                [
                    "Cerrados",
                    "Abiertos"
                ]
            ],

            names=[
                "Año",
                "Estado"
            ]
        )
    )


    resumen = (
        resumen
        .set_index(
            [
                "Año",
                "Estado"
            ]
        )
        .reindex(
            indice_completo
        )
        .reset_index()
    )


    resumen["Cantidad"] = (
        resumen["Cantidad"]
        .fillna(0)
    )


    resumen["Porcentaje"] = (
        resumen["Porcentaje"]
        .fillna(0)
    )


    # =====================================================
    # FIGURA BASE
    # =====================================================

    fig = px.line(

        resumen,

        x="Año",

        y="Porcentaje",

        color="Estado",

        markers=True,

        custom_data=[
            "Cantidad"
        ],

        color_discrete_map={
            "Cerrados":
                VERDE,

            "Abiertos":
                ROJO
        },

        template="plotly_white"
    )


    fig.update_traces(

        line=dict(
            width=3
        ),

        marker=dict(
            size=7
        ),

        hovertemplate=(

            "<b>%{fullData.name}</b>"
            "<br><br>"

            "Año: %{x}<br>"

            "Participación: "
            "%{y:.1f}%<br>"

            "Cantidad de avisos: "
            "%{customdata[0]:.0f}"

            "<extra></extra>"
        )
    )


    # =====================================================
    # RESALTAR PERIODO SELECCIONADO
    # =====================================================

    titulo = (
        "Evolución del estado de los avisos"
    )


    if anio_seleccionado is not None:

        anio_actual = int(
            anio_seleccionado
        )

        anio_anterior = (
            anio_actual - 1
        )


        # =================================================
        # FRANJA DE COMPARACIÓN
        # =================================================

        fig.add_vrect(

            x0=anio_anterior - 0.35,

            x1=anio_actual + 0.35,

            fillcolor=AMBAR,

            opacity=0.08,

            line_width=0,

            layer="below"
        )


        # =================================================
        # PUNTOS DESTACADOS
        # =================================================

        seleccion = resumen[
            resumen["Año"].isin(
                [
                    anio_anterior,
                    anio_actual
                ]
            )
        ].copy()


        cerrados_sel = seleccion[
            seleccion["Estado"]
            == "Cerrados"
        ]


        abiertos_sel = seleccion[
            seleccion["Estado"]
            == "Abiertos"
        ]


        fig.add_trace(

            go.Scatter(

                x=cerrados_sel[
                    "Año"
                ],

                y=cerrados_sel[
                    "Porcentaje"
                ],

                mode="markers",

                marker=dict(
                    size=13,
                    color=VERDE,
                    line=dict(
                        color=BLANCO,
                        width=3
                    )
                ),

                showlegend=False,

                hoverinfo="skip"
            )
        )


        fig.add_trace(

            go.Scatter(

                x=abiertos_sel[
                    "Año"
                ],

                y=abiertos_sel[
                    "Porcentaje"
                ],

                mode="markers",

                marker=dict(
                    size=13,
                    color=ROJO,
                    line=dict(
                        color=BLANCO,
                        width=3
                    )
                ),

                showlegend=False,

                hoverinfo="skip"
            )
        )


        # =================================================
        # ETIQUETA DE COMPARACIÓN
        # =================================================

        fig.add_annotation(

            x=(
                anio_anterior
                + anio_actual
            ) / 2,

            y=1.08,

            xref="x",

            yref="paper",

            text=(
                f"Comparación "
                f"{anio_anterior} → {anio_actual}"
            ),

            showarrow=False,

            font=dict(
                size=11,
                color=AZUL
            ),

            bgcolor="#F8FAFC",

            bordercolor=AMBAR,

            borderwidth=1,

            borderpad=5
        )


        titulo = (

            "Evolución del estado de los avisos "
            f"· {anio_anterior} → {anio_actual}"
        )


    # =====================================================
    # DISEÑO
    # =====================================================

    fig.update_layout(

        height=340,

        margin=dict(
            l=45,
            r=25,
            t=70,
            b=55
        ),

        title={
            "text": titulo,
            "x": 0.02,
            "xanchor": "left",
            "font": {
                "size": 17,
                "color": AZUL
            }
        },

        xaxis=dict(

            title="Año",

            dtick=1,

            showgrid=False,

            zeroline=False,

            tickfont=dict(
                size=11,
                color=GRIS
            )
        ),

        yaxis=dict(

            title="% de avisos",

            range=[
                0,
                100
            ],

            ticksuffix="%",

            gridcolor=BORDE,

            zeroline=False,

            tickfont=dict(
                size=11,
                color=GRIS
            )
        ),

        legend=dict(

            title=None,

            orientation="h",

            yanchor="top",

            y=-0.18,

            xanchor="center",

            x=0.5
        ),

        hovermode="x unified",

        plot_bgcolor=BLANCO,

        paper_bgcolor=BLANCO
    )


    return fig


# =========================================================
# LECTURA EJECUTIVA
# =========================================================

def crear_lectura(
    resultado
):

    anio_actual = (
        resultado[
            "anio_actual"
        ]
    )

    anio_anterior = (
        resultado[
            "anio_anterior"
        ]
    )

    variacion = (
        resultado[
            "variacion_total"
        ]
    )

    pct = (
        resultado[
            "pct_variacion"
        ]
    )

    incremento = (
        resultado[
            "principal_incremento"
        ]
    )

    reduccion = (
        resultado[
            "principal_reduccion"
        ]
    )


    if variacion > 0:

        frase = (
            f"Los avisos aumentaron en "
            f"{formato_numero(abs(variacion))} "
            f"registros"
        )


    elif variacion < 0:

        frase = (
            f"Los avisos disminuyeron en "
            f"{formato_numero(abs(variacion))} "
            f"registros"
        )


    else:

        frase = (
            "El volumen total de avisos "
            "se mantuvo sin variación"
        )


    if pct is not None:

        frase += (
            f" ({formato_porcentaje(pct)})"
        )


    frase += (
        f" entre {anio_anterior} "
        f"y {anio_actual}."
    )


    if incremento is not None:

        tipo = incremento[
            "Tipo de aviso"
        ]

        valor = int(
            incremento[
                "Variacion"
            ]
        )

        frase += (

            f" {tipo} presentó "
            f"el mayor incremento, "
            f"con {formato_numero(valor)} "
            f"avisos adicionales."
        )


    if reduccion is not None:

        tipo = reduccion[
            "Tipo de aviso"
        ]

        valor = abs(
            int(
                reduccion[
                    "Variacion"
                ]
            )
        )

        frase += (

            f" {tipo} registró "
            f"la mayor reducción, "
            f"con {formato_numero(valor)} "
            f"avisos menos."
        )


    return frase


# =========================================================
# KPI TEXTOS
# =========================================================

def texto_incremento(
    fila
):

    if fila is None:
        return "Sin incremento"

    return (
        f"{fila['Tipo de aviso']} "
        f"(+{formato_numero(fila['Variacion'])})"
    )


def texto_reduccion(
    fila
):

    if fila is None:
        return "Sin reducción"

    return (
        f"{fila['Tipo de aviso']} "
        f"({formato_numero(fila['Variacion'])})"
    )


# =========================================================
# RESULTADO INICIAL
# =========================================================

if anio_inicial is not None:

    resultado_inicial = (
        calcular_variacion(
            anio_inicial
        )
    )


    fig_inicial = (
        crear_cascada(
            resultado_inicial
        )
    )


    fig_linea_inicial = (
        crear_linea_estado(
            anio_inicial
        )
    )


    lectura_inicial = (
        crear_lectura(
            resultado_inicial
        )
    )


    variacion_inicial = (
        resultado_inicial[
            "variacion_total"
        ]
    )


    pct_inicial = (
        resultado_inicial[
            "pct_variacion"
        ]
    )


    incremento_inicial = (
        resultado_inicial[
            "principal_incremento"
        ]
    )


    reduccion_inicial = (
        resultado_inicial[
            "principal_reduccion"
        ]
    )


else:

    fig_inicial = go.Figure()

    fig_linea_inicial = (
        go.Figure()
    )

    lectura_inicial = (
        "No existen años consecutivos "
        "suficientes para realizar "
        "el análisis."
    )

    variacion_inicial = 0

    pct_inicial = None

    incremento_inicial = None

    reduccion_inicial = None


# =========================================================
# LAYOUT
# =========================================================

layout = html.Div([


    # =====================================================
    # BANNER
    # =====================================================

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

                "Análisis de Variación de Avisos",

                style={
                    "color": AZUL,
                    "marginTop": "2px",
                    "marginBottom": "2px",
                    "fontSize": "26px"
                }
            ),


            html.P(

                "Analiza qué factores explican "
                "el cambio en el volumen de avisos "
                "y cómo evoluciona su estado de gestión.",

                className="banner-text"
            )

        ]
    ),


    # =====================================================
    # TEXTO EXPLICATIVO
    # =====================================================

    html.Div(

        [

            html.P(

                "La cascada explica la variación "
                "entre dos años consecutivos, mientras "
                "la línea muestra la evolución histórica "
                "de la proporción de avisos cerrados "
                "y abiertos y resalta el periodo comparado.",

                style={
                    "margin": "0",
                    "fontSize": "13px",
                    "color": GRIS,
                    "lineHeight": "1.5"
                }
            )

        ],

        style={
            "margin": "8px 0 10px 0",
            "padding": "10px 14px",
            "backgroundColor": "#F8FAFC",
            "borderLeft":
                f"4px solid {VERDE}",
            "borderRadius": "6px"
        }
    ),


    # =====================================================
    # FILTRO
    # =====================================================

    html.Div(

        [

            html.Div(

                [

                    html.Label(

                        "Año a analizar",

                        style={
                            "fontWeight": "600",
                            "fontSize": "12px",
                            "color": AZUL,
                            "marginBottom": "4px"
                        }
                    ),


                    dcc.Dropdown(

                        id="filtro-anio-cascada",

                        options=[
                            {
                                "label":
                                    str(anio),

                                "value":
                                    anio
                            }
                            for anio
                            in anios_comparables
                        ],

                        value=anio_inicial,

                        clearable=False
                    )

                ],

                style={
                    "width": "260px"
                }
            ),


            html.Div(

                id="texto-comparacion",

                children=(
                    f"Comparación: "
                    f"{anio_inicial - 1} "
                    f"vs. {anio_inicial}"
                    if anio_inicial
                    else ""
                ),

                style={
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": GRIS,
                    "paddingBottom": "9px"
                }
            )

        ],

        style={
            "display": "flex",
            "alignItems": "end",
            "gap": "16px",
            "marginBottom": "10px"
        }
    ),


    # =====================================================
    # KPI
    # =====================================================

    html.Div(

        className="kpi-grid",

        children=[


            html.Div(

                className="kpi-card",

                children=[

                    html.Div(
                        "↕️",
                        className="kpi-icon"
                    ),

                    html.Div([

                        html.H3(

                            formato_variacion(
                                variacion_inicial
                            ),

                            id="kpi-variacion-total",

                            className=(
                                "kpi-value-green"
                                if variacion_inicial >= 0
                                else "kpi-value-red"
                            )
                        ),

                        html.Span(
                            "Variación de avisos",
                            className="kpi-label"
                        )
                    ])
                ]
            ),


            html.Div(

                className="kpi-card",

                children=[

                    html.Div(
                        "📊",
                        className="kpi-icon"
                    ),

                    html.Div([

                        html.H3(

                            formato_porcentaje(
                                pct_inicial
                            ),

                            id="kpi-variacion-pct",

                            className="kpi-value-main"
                        ),

                        html.Span(
                            "Variación porcentual",
                            className="kpi-label"
                        )
                    ])
                ]
            ),


            html.Div(

                className="kpi-card",

                children=[

                    html.Div(
                        "⬆️",
                        className="kpi-icon"
                    ),

                    html.Div([

                        html.H3(

                            texto_incremento(
                                incremento_inicial
                            ),

                            id="kpi-mayor-incremento",

                            className="kpi-value-green",

                            style={
                                "fontSize": "18px"
                            }
                        ),

                        html.Span(
                            "Mayor contribución positiva",
                            className="kpi-label"
                        )
                    ])
                ]
            ),


            html.Div(

                className="kpi-card",

                children=[

                    html.Div(
                        "⬇️",
                        className="kpi-icon"
                    ),

                    html.Div([

                        html.H3(

                            texto_reduccion(
                                reduccion_inicial
                            ),

                            id="kpi-mayor-reduccion",

                            className="kpi-value-red",

                            style={
                                "fontSize": "18px"
                            }
                        ),

                        html.Span(
                            "Mayor contribución negativa",
                            className="kpi-label"
                        )
                    ])
                ]
            )

        ]
    ),


    # =====================================================
    # CASCADA
    # =====================================================

    html.Div(

        className="chart-card",

        style={
            "marginTop": "12px"
        },

        children=[

            html.H4(

                "¿Qué explica la variación?",

                className="chart-title"
            ),


            dcc.Graph(

                id="grafica-cascada",

                figure=fig_inicial,

                config={
                    "displayModeBar": False
                }
            )

        ]
    ),


    # =====================================================
    # LECTURA EJECUTIVA
    # =====================================================

    html.Div(

        [

            html.Div(

                "Lectura ejecutiva",

                style={
                    "fontSize": "13px",
                    "fontWeight": "700",
                    "color": AZUL,
                    "marginBottom": "5px"
                }
            ),


            html.P(

                lectura_inicial,

                id="lectura-cascada",

                style={
                    "margin": "0",
                    "fontSize": "13px",
                    "color": GRIS,
                    "lineHeight": "1.6"
                }
            )

        ],

        style={
            "margin": "10px 0 12px 0",
            "padding": "12px 14px",
            "backgroundColor": "#F8FAFC",
            "borderLeft":
                f"4px solid {AMBAR}",
            "borderRadius": "6px"
        }
    ),


    # =====================================================
    # LÍNEA CERRADOS / ABIERTOS
    # =====================================================

    html.Div(

        className="chart-card",

        children=[

            html.H4(

                "¿Cómo evoluciona el estado de los avisos?",

                className="chart-title"
            ),


            dcc.Graph(

                id="grafica-estado-lineas",

                figure=fig_linea_inicial,

                config={
                    "displayModeBar": False
                }
            )

        ]
    )

])


# =========================================================
# CALLBACK GENERAL
# =========================================================

@callback(

    Output(
        "grafica-cascada",
        "figure"
    ),

    Output(
        "kpi-variacion-total",
        "children"
    ),

    Output(
        "kpi-variacion-total",
        "className"
    ),

    Output(
        "kpi-variacion-pct",
        "children"
    ),

    Output(
        "kpi-mayor-incremento",
        "children"
    ),

    Output(
        "kpi-mayor-reduccion",
        "children"
    ),

    Output(
        "lectura-cascada",
        "children"
    ),

    Output(
        "texto-comparacion",
        "children"
    ),

    Output(
        "grafica-estado-lineas",
        "figure"
    ),

    Input(
        "filtro-anio-cascada",
        "value"
    )
)

def actualizar_cascada(
    anio
):

    if anio is None:

        fig_vacia = go.Figure()

        return (

            fig_vacia,

            "0",

            "kpi-value-main",

            "N/A",

            "Sin datos",

            "Sin datos",

            (
                "No existen datos suficientes "
                "para realizar la comparación."
            ),

            "",

            fig_vacia
        )


    # =====================================================
    # AÑO
    # =====================================================

    anio = int(
        anio
    )


    # =====================================================
    # CASCADA
    # =====================================================

    resultado = (
        calcular_variacion(
            anio
        )
    )


    fig_cascada = (
        crear_cascada(
            resultado
        )
    )


    # =====================================================
    # LÍNEA SINCRONIZADA
    # =====================================================

    fig_estado = (
        crear_linea_estado(
            anio
        )
    )


    # =====================================================
    # KPI
    # =====================================================

    variacion = (
        resultado[
            "variacion_total"
        ]
    )


    pct = (
        resultado[
            "pct_variacion"
        ]
    )


    incremento = (
        resultado[
            "principal_incremento"
        ]
    )


    reduccion = (
        resultado[
            "principal_reduccion"
        ]
    )


    lectura = (
        crear_lectura(
            resultado
        )
    )


    # =====================================================
    # COLOR KPI VARIACIÓN
    # =====================================================

    if variacion > 0:

        clase_variacion = (
            "kpi-value-green"
        )

    elif variacion < 0:

        clase_variacion = (
            "kpi-value-red"
        )

    else:

        clase_variacion = (
            "kpi-value-main"
        )


    # =====================================================
    # TEXTO COMPARACIÓN
    # =====================================================

    texto_comparacion = (

        f"Comparación: "
        f"{anio - 1} "
        f"vs. {anio}"
    )


    # =====================================================
    # RETURN
    # =====================================================

    return (

        fig_cascada,

        formato_variacion(
            variacion
        ),

        clase_variacion,

        formato_porcentaje(
            pct
        ),

        texto_incremento(
            incremento
        ),

        texto_reduccion(
            reduccion
        ),

        lectura,

        texto_comparacion,

        fig_estado
    )