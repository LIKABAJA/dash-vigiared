from pathlib import Path
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/', title='Inicio')

# Cargar Datos
BASE_DIR = Path(__file__).resolve().parent.parent
df_hist = pd.read_excel(BASE_DIR / 'data' / 'histórico_filtrado_proc.xlsx')
df_eq = pd.read_excel(BASE_DIR / 'data' / 'equipos_proc.xlsx')

# KPIs
total_avisos = len(df_hist)
total_equipos = len(df_eq)
cerrados = len(df_hist[df_hist['Estado aviso'] == 'Cerrado'])
pct_cerrados = round((cerrados / total_avisos) * 100, 1)
abiertos = len(df_hist[df_hist['Estado aviso'] == 'Abierto'])
pct_abiertos = round((abiertos / total_avisos) * 100, 1)

# Figura 1: Líneas
df_line = df_hist.groupby(['Año', 'Tipo de aviso']).size().reset_index(name='Cantidad')
df_top = df_line[df_line['Tipo de aviso'].isin(['Vegetación', 'Construcciones'])]
df_oth = df_line[~df_line['Tipo de aviso'].isin(['Vegetación', 'Construcciones'])].groupby('Año')['Cantidad'].sum().reset_index()
df_oth['Tipo de aviso'] = 'Otros'
df_line_final = pd.concat([df_top, df_oth]).sort_values('Año')

fig_line = px.line(
    df_line_final, x='Año', y='Cantidad', color='Tipo de aviso', markers=True,
    color_discrete_map={'Vegetación': '#2A9D8F', 'Construcciones': '#E9A23B', 'Otros': '#17324D'},
    template='plotly_white'
)
fig_line.update_layout(
    margin=dict(l=20, r=20, t=10, b=20),
    height=260,
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
)

# Figura 2: Polar
df_polar = df_hist.groupby(['Mes', 'nMes', 'Tipo de aviso']).size().reset_index(name='Cantidad')
df_polar_top = df_polar[df_polar['Tipo de aviso'].isin(['Vegetación', 'Construcciones'])]
df_polar_oth = df_polar[~df_polar['Tipo de aviso'].isin(['Vegetación', 'Construcciones'])].groupby(['Mes', 'nMes'])['Cantidad'].sum().reset_index()
df_polar_oth['Tipo de aviso'] = 'Otros'
df_polar_final = pd.concat([df_polar_top, df_polar_oth]).sort_values('Mes')

fig_polar = px.line_polar(
    df_polar_final, r='Cantidad', theta='nMes', color='Tipo de aviso', line_close=True,
    color_discrete_map={'Vegetación': '#2A9D8F', 'Construcciones': '#E9A23B', 'Otros': '#17324D'},
    template='plotly_white'
)
fig_polar.update_layout(
    margin=dict(l=30, r=30, t=10, b=20),
    height=260,
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
)

layout = html.Div([
    # Banner Bienvenida
    html.Div(className='card-banner', children=[
        html.H5("Bienvenido a", className='banner-welcome'),
        html.H1("VigíaRed Energía S.A.S.", className='banner-title'),
        html.P("Monitoreamos la red, anticipamos el riesgo.", className='banner-slogan'),
        html.P(
            "Plataforma de análisis para la gestión y operación de avisos asociados a infraestructura de transmisión eléctrica. "
            "Integramos información histórica y territorial para identificar patrones, evaluar el cumplimiento de los tiempos de atención y apoyar la toma de decisiones.",
            className='banner-text'
        )
    ]),

    # Grilla de KPIs
    html.Div(className='kpi-grid', children=[
        html.Div(className='kpi-card', children=[
            html.Div("📄", className='kpi-icon'),
            html.Div([
                html.H3(f"{total_avisos:,}".replace(',', '.'), className='kpi-value-main'),
                html.Span("Avisos históricos", className='kpi-label')
            ])
        ]),

        html.Div(className='kpi-card', children=[
            html.Div("🗼", className='kpi-icon'),
            html.Div([
                html.H3(f"{total_equipos:,}".replace(',', '.'), className='kpi-value-main'),
                html.Span("Equipos georreferenciados", className='kpi-label')
            ])
        ]),

        html.Div(className='kpi-card', children=[
            html.Div("✔️", className='kpi-icon'),
            html.Div([
                html.H3(f"{pct_cerrados}%".replace('.', ','), className='kpi-value-green'),
                html.Span("Avisos cerrados", className='kpi-label')
            ])
        ]),

        html.Div(className='kpi-card', children=[
            html.Div("🕒", className='kpi-icon'),
            html.Div([
                html.H3(f"{pct_abiertos}%".replace('.', ','), className='kpi-value-red'),
                html.Span("Avisos abiertos", className='kpi-label')
            ])
        ]),
    ]),

    # Gráficas
    html.Div(className='charts-grid-2col', children=[
        html.Div(className='chart-card', children=[
            html.H4("Evolución de avisos por año", className='chart-title'),
            dcc.Graph(figure=fig_line, config={'displayModeBar': False})
        ]),

        html.Div(className='chart-card', children=[
            html.H4("Distribución mensual de avisos (vista polar)", className='chart-title'),
            dcc.Graph(figure=fig_polar, config={'displayModeBar': False})
        ])
    ])
])