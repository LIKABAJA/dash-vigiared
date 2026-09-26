from pathlib import Path
import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path='/grafico-cascada', title='Capacidad Operativa')

# Cargar datos
BASE_DIR = Path(__file__).resolve().parent.parent
df_hist = pd.read_excel(BASE_DIR / 'data' / 'histórico_filtrado_proc.xlsx')

# Obtener opciones únicas ordenadas para los filtros
años_disponibles = sorted([int(a) for a in df_hist['Año'].dropna().unique()])
tipos_disponibles = df_hist['Tipo de aviso'].dropna().unique().tolist()

layout = html.Div([
    html.Div(className='chart-card', children=[
        # Título y Descripción
        html.H2("Flujo de Capacidad Operativa (Cascada)", style={'color': '#17324D', 'margin': '0 0 5px 0'}),
        html.P("Auditoría de avisos registrados, resueltos, pendientes y niveles de cumplimiento.", style={'color': '#607080', 'marginBottom': '20px'}),
        
        # FILA DE FILTROS (2 Columnas)
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '25px'}, children=[
            
            # Filtro 1: Año
            html.Div([
                html.Label("Seleccionar Año:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='cascada-filter-año',
                    options=[{'label': 'Todos los años', 'value': 'ALL'}] + [
                        {'label': str(a), 'value': a} for a in años_disponibles
                    ],
                    value='ALL',
                    clearable=False
                )
            ]),

            # Filtro 2: Tipo de Aviso
            html.Div([
                html.Label("Seleccionar Tipo de Aviso:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='cascada-filter-tipo',
                    options=[{'label': 'Todos los tipos', 'value': 'ALL'}] + [
                        {'label': t, 'value': t} for t in tipos_disponibles
                    ],
                    value='ALL',
                    clearable=False
                )
            ]),
        ]),

        # Gráfico de Cascada
        dcc.Graph(id='graph-cascada')
    ])
])

@callback(
    Output('graph-cascada', 'figure'),
    [
        Input('cascada-filter-año', 'value'),
        Input('cascada-filter-tipo', 'value')
    ]
)
def update_waterfall_chart(año_sel, tipo_sel):
    df_filtered = df_hist.copy()
    
    # 1. Aplicar filtro de Año
    if año_sel and año_sel != 'ALL':
        df_filtered = df_filtered[df_filtered['Año'] == int(año_sel)]
        
    # 2. Aplicar filtro de Tipo de aviso
    if tipo_sel and tipo_sel != 'ALL':
        df_filtered = df_filtered[df_filtered['Tipo de aviso'] == tipo_sel]
        
    # Si la combinación no produce datos
    if df_filtered.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No hay registros para la combinación de filtros seleccionada.",
            template="plotly_white",
            height=450
        )
        return fig

    # Re-cálculo dinámico de métricas para la cascada
    total_avisos = len(df_filtered)
    cerrados = len(df_filtered[df_filtered['Estado aviso'] == 'Cerrado'])
    abiertos = len(df_filtered[df_filtered['Estado aviso'] == 'Abierto'])
    a_tiempo = len(df_filtered[df_filtered['Tiempo aviso'] == 'A tiempo'])
    atrasados = len(df_filtered[df_filtered['Tiempo aviso'] == 'Atrasado'])

    fig = go.Figure(go.Waterfall(
        name="Avisos", 
        orientation="v",
        measure=["relative", "relative", "total", "relative", "relative"],
        x=["Total Registrados", "Cerrados", "Pendientes", "Atendidos a Tiempo", "Atrasados"],
        textposition="outside",
        text=[f"{total_avisos}", f"-{cerrados}", f"{abiertos}", f"{a_tiempo}", f"{atrasados}"],
        y=[total_avisos, -cerrados, 0, a_tiempo, atrasados],
        connector={"line": {"color": "#607080"}},
        decreasing={"marker": {"color": "#2A9D8F"}}, # Verde analítico
        increasing={"marker": {"color": "#D9534F"}}, # Rojo de riesgo
        totals={"marker": {"color": "#17324D"}}      # Azul institucional
    ))

    fig.update_layout(
        template="plotly_white", 
        waterfallgap=0.3, 
        height=450,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig