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
    
    # Barra Lateral
    html.Div(className='sidebar', children=[
        html.Div(className='sidebar-logo-container', children=[
            html.Img(src='/assets/logo.png', className='sidebar-logo-img')
        ]),
        
        # Enlaces de Navegación
        html.Nav([
            dcc.Link("🏠  Inicio", href="/", id='link-home', className='nav-link'),
            dcc.Link("📈  Evolución de avisos", href="/grafico-lineas", id='link-lineas', className='nav-link'),
            dcc.Link("📊  Capacidad operativa", href="/grafico-cascada", id='link-cascada', className='nav-link'),
            dcc.Link("🌀  Distribución polar", href="/grafico-polar", id='link-polar', className='nav-link'),
        ])
    ]),

    # Contenido Principal
    html.Div(className='main-content', children=[
        # Franja superior azul institucional (limpia, sin texto de usuario)
        html.Div(className='top-header', style={'height': '20px'}),
        
        dash.page_container
    ])
])

# Callback dinámico para resaltar la barra verde en la navegación
@callback(
    [
        Output('link-home', 'className'),
        Output('link-lineas', 'className'),
        Output('link-cascada', 'className'),
        Output('link-polar', 'className'),
    ],
    Input('url', 'pathname')
)
def update_active_links(pathname):
    home_cls = 'nav-link nav-link-active' if pathname in ['/', ''] else 'nav-link'
    lineas_cls = 'nav-link nav-link-active' if pathname == '/grafico-lineas' else 'nav-link'
    cascada_cls = 'nav-link nav-link-active' if pathname == '/grafico-cascada' else 'nav-link'
    polar_cls = 'nav-link nav-link-active' if pathname == '/grafico-polar' else 'nav-link'
    
    return home_cls, lineas_cls, cascada_cls, polar_cls


if __name__ == '__main__':
    app.run(debug=True, dev_tools_ui=False, host='192.168.1.11', port=8050)
    