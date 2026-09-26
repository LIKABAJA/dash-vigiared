from pathlib import Path
import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# Registro único de la página para evitar choques de rutas
dash.register_page(__name__, path='/grafico-polar', title='Distribución Polar')

# Carga de datos
BASE_DIR = Path(__file__).resolve().parent.parent
df_hist = pd.read_excel(BASE_DIR / 'data' / 'histórico_filtrado_proc.xlsx')

# Opciones únicas para los selectores
años_disponibles = sorted([int(a) for a in df_hist['Año'].dropna().unique()])
tipos_disponibles = df_hist['Tipo de aviso'].dropna().unique().tolist()

layout = html.Div(className='chart-card', children=[
    html.H2("Análisis Estacional Polar", style={'color': '#17324D', 'margin': '0 0 5px 0'}),
    html.P("Consulte el comportamiento mensual filtrando por tipo de incidencia y año de operación.", style={'color': '#607080', 'marginBottom': '20px'}),
    
    # FILA DE FILTROS (2 Columnas: Año y Tipo de Aviso)
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '20px'}, children=[
        
        # Filtro 1: Año
        html.Div([
            html.Label("Seleccionar Año:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='polar-filter-año',
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
                id='dropdown-tipo-aviso',
                options=[{'label': 'Todos los tipos', 'value': 'ALL'}] + [
                    {'label': i, 'value': i} for i in tipos_disponibles
                ],
                value='ALL',
                clearable=False
            )
        ]),
    ]),
    
    # Gráfico Polar
    dcc.Graph(id='graph-polar')
])

@callback(
    Output('graph-polar', 'figure'),
    [
        Input('polar-filter-año', 'value'),
        Input('dropdown-tipo-aviso', 'value')
    ]
)
def update_polar_chart(año_sel, tipo_sel):
    df_filtered = df_hist.copy()
    
    # 1. Aplicar filtro de Año
    if año_sel and año_sel != 'ALL':
        df_filtered = df_filtered[df_filtered['Año'] == int(año_sel)]
        
    # 2. Aplicar filtro de Tipo de aviso
    if tipo_sel and tipo_sel != 'ALL':
        df_filtered = df_filtered[df_filtered['Tipo de aviso'] == tipo_sel]
        
    # Si los filtros dejan el dataset vacío
    if df_filtered.empty:
        fig = px.line_polar(title="No hay datos registrados para la combinación de año y tipo seleccionados.")
        fig.update_layout(template='plotly_white', height=480)
        return fig

    # Definir la lógica de visualización según si eligió 'ALL' o un tipo específico
    if tipo_sel == 'ALL':
        df_polar = df_filtered.groupby(['Mes', 'nMes', 'Tipo de aviso']).size().reset_index(name='Cantidad').sort_values('Mes')
        
        fig = px.line_polar(
            df_polar, 
            r='Cantidad', 
            theta='nMes', 
            color='Tipo de aviso',
            line_close=True,
            title=f"Distribución Mensual - {'Año ' + str(año_sel) if año_sel != 'ALL' else 'Histórico General'}",
            template='plotly_white',
            color_discrete_sequence=['#2A9D8F', '#E9A23B', '#17324D', '#D9534F', '#457B9D']
        )
    else:
        df_polar = df_filtered.groupby(['Mes', 'nMes']).size().reset_index(name='Cantidad').sort_values('Mes')
        
        fig = px.line_polar(
            df_polar, 
            r='Cantidad', 
            theta='nMes', 
            line_close=True,
            title=f"Distribución Mensual: {tipo_sel} ({'Año ' + str(año_sel) if año_sel != 'ALL' else 'Histórico General'})",
            template='plotly_white', 
            color_discrete_sequence=['#2A9D8F']
        )
        fig.update_traces(fill='toself')

    fig.update_layout(
        height=480,
        margin=dict(l=30, r=30, t=40, b=30)
    )
    return fig