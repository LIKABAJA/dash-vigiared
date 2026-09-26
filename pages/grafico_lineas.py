from pathlib import Path
import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/grafico-lineas', title='Evolución de Avisos')

BASE_DIR = Path(__file__).resolve().parent.parent
df_hist = pd.read_excel(BASE_DIR / 'data' / 'histórico_filtrado_proc.xlsx')

layout = html.Div([
    html.Div(className='chart-card', children=[
        # Título y Subtítulo
        html.H2("Evolución Histórica de Avisos por Año", style={'color': '#17324D', 'margin': '0 0 5px 0'}),
        html.P("Ajuste los filtros a continuación para analizar subconjuntos de datos específicos.", style={'color': '#607080', 'marginBottom': '20px'}),
        
        # FILA DE FILTROS (3 Columnas debajo del título)
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '20px', 'marginBottom': '25px'}, children=[
            
            # Filtro 1: Tipo de aviso
            html.Div([
                html.Label("Tipo de aviso:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='page-filter-tipo',
                    options=[{'label': 'Todos los tipos', 'value': 'ALL'}] + [
                        {'label': i, 'value': i} for i in ['Vegetación', 'Construcciones', 'Permiso Ingreso', 'Obras', 'Invasión/Explanacion']
                    ],
                    value='ALL',
                    clearable=False
                )
            ]),

            # Filtro 2: Estado de aviso
            html.Div([
                html.Label("Estado de aviso:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='page-filter-estado',
                    options=[
                        {'label': 'Todos los estados', 'value': 'ALL'},
                        {'label': 'Cerrado', 'value': 'Cerrado'},
                        {'label': 'Abierto', 'value': 'Abierto'}
                    ],
                    value='ALL',
                    clearable=False
                )
            ]),

            # Filtro 3: Tiempo de aviso
            html.Div([
                html.Label("Tiempo de aviso:", style={'fontWeight': 'bold', 'color': '#17324D', 'fontSize': '13px', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='page-filter-tiempo',
                    options=[
                        {'label': 'Todos los tiempos', 'value': 'ALL'},
                        {'label': 'A tiempo', 'value': 'A tiempo'},
                        {'label': 'Atrasado', 'value': 'Atrasado'}
                    ],
                    value='ALL',
                    clearable=False
                )
            ]),
        ]),

        # Contenedor de la Gráfica de Líneas
        dcc.Graph(id='graph-lineas')
    ])
])

@callback(
    Output('graph-lineas', 'figure'),
    [
        Input('page-filter-tipo', 'value'),
        Input('page-filter-estado', 'value'),
        Input('page-filter-tiempo', 'value')
    ]
)
def update_line_chart(tipo, estado, tiempo):
    df_filtered = df_hist.copy()
    
    # 1. Filtro Tipo
    if tipo and tipo != 'ALL':
        df_filtered = df_filtered[df_filtered['Tipo de aviso'] == tipo]
        
    # 2. Filtro Estado
    if estado and estado != 'ALL':
        df_filtered = df_filtered[df_filtered['Estado aviso'] == estado]
        
    # 3. Filtro Tiempo
    if tiempo and tiempo != 'ALL':
        df_filtered = df_filtered[df_filtered['Tiempo aviso'] == tiempo]
    
    # Selección de la categoría para agrupar las líneas según lo filtrado
    if tipo == 'ALL':
        group_col = 'Tipo de aviso'
    elif estado == 'ALL':
        group_col = 'Estado aviso'
    elif tiempo == 'ALL':
        group_col = 'Tiempo aviso'
    else:
        group_col = 'Tipo de aviso'
        
    if df_filtered.empty:
        fig = px.line(title="No se encontraron registros para la combinación de filtros seleccionada.")
        fig.update_layout(template='plotly_white', height=420)
        return fig

    df_grouped = df_filtered.groupby(['Año', group_col]).size().reset_index(name='Cantidad')
    
    fig = px.line(
        df_grouped, 
        x='Año', 
        y='Cantidad', 
        color=group_col,
        markers=True, 
        template='plotly_white',
        color_discrete_sequence=['#2A9D8F', '#E9A23B', '#17324D', '#D9534F', '#457B9D']
    )
    
    fig.update_layout(
        hovermode='x unified', 
        xaxis_title='Año', 
        yaxis_title='Número de Avisos', 
        height=420,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig