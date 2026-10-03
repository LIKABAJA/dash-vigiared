import dash
from dash import Dash, html, dcc, callback, Output, Input

app = Dash(
    __name__, 
    use_pages=True, 
    suppress_callback_exceptions=True
)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Barra Lateral (Sidebar)
    html.Div(id='sidebar', className='sidebar', children=[
        html.Div(className='sidebar-logo-container', children=[
            html.Img(src='/assets/logo.png', className='sidebar-logo-img')
        ]),

        # Enlaces de Navegación (Únicamente Inicio y Capacidad operativa)
        html.Nav([
            dcc.Link("🏠  Inicio", href="/", id='link-home', className='nav-link'),
            dcc.Link("📊  Capacidad operativa", href="/grafico-cascada", id='link-cascada', className='nav-link'),
        ])
    ]),

    # Contenido Principal
    html.Div(id='main-content', className='main-content', children=[
        # Cabecera superior con botón para ocultar/mostrar menú
        html.Div(className='top-header', children=[
            html.Button("☰ Menú", id='btn-toggle-sidebar', className='toggle-btn', n_clicks=0)
        ]),
        
        dash.page_container
    ])
])


# Callback para alternar (ocultar / mostrar) la barra lateral
@callback(
    [
        Output('sidebar', 'className'),
        Output('main-content', 'className')
    ],
    Input('btn-toggle-sidebar', 'n_clicks'),
    prevent_initial_call=False
)
def toggle_sidebar(n_clicks):
    if n_clicks and n_clicks % 2 != 0:
        return 'sidebar sidebar-collapsed', 'main-content main-content-expanded'
    
    return 'sidebar', 'main-content'


# Callback para resaltar únicamente las dos pestañas activas
@callback(
    [
        Output('link-home', 'className'),
        Output('link-cascada', 'className'),
    ],
    Input('url', 'pathname')
)
def update_active_links(pathname):
    current_path = pathname.rstrip('/') if pathname and pathname != '/' else '/'
    
    home_cls = 'nav-link nav-link-active' if current_path == '/' else 'nav-link'
    cascada_cls = 'nav-link nav-link-active' if current_path == '/grafico-cascada' else 'nav-link'
    
    return home_cls, cascada_cls


if __name__ == "__main__":
    app.run(
        debug=True,
        dev_tools_ui=False,
        host="127.0.0.1",
        port=8050
    )