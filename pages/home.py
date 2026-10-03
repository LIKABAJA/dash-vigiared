import dash
from dash import html, dcc

dash.register_page(__name__, path='/', title='Inicio - VigíaRed Energía')

layout = html.Div([

    # ======================================================
    # PORTADA PRINCIPAL
    # ======================================================
    html.Div(
        className="home-hero",
        children=[

            # Etiqueta superior
            html.Div(
                "▣  Proyecto de Visualización de Datos",
                className="project-badge"
            ),

            # Título
            html.H1(
                [
                    html.Span("VigíaRed ", className="title-blue"),
                    html.Span("Energía S.A.S.", className="title-green")
                ],
                className="home-title"
            ),

            # Eslogan
            html.P(
                "Monitoreamos la red, anticipamos el riesgo.",
                className="home-slogan"
            ),

            # Línea de colores
            html.Div(className="brand-accent-line"),

            # Nuestra historia
            html.H2(
                "Nuestra historia",
                className="home-section-title"
            ),

            html.P(
                [
                    html.Strong("VigíaRed Energía S.A.S. "),
                    "nace como una propuesta orientada al monitoreo y análisis "
                    "de información relacionada con la infraestructura de transmisión eléctrica. "
                    "A través del uso de datos históricos de avisos y equipos, busca facilitar "
                    "la identificación de tendencias y apoyar la gestión operativa."
                ],
                className="home-description"
            ),

            # ==================================================
            # AUTORES
            # ==================================================
            html.Div(
                className="authors-card",
                children=[

                    html.Div(
                        "♟",
                        className="authors-icon"
                    ),

                    html.Div([
                        html.H3(
                            "Autores",
                            className="authors-title"
                        ),

                        html.P(
                            "Linda Barrera Jaramillo",
                            className="author-name"
                        ),

                        html.P(
                            "Danny Ortiz Quintero",
                            className="author-name"
                        ),

                        html.P(
                            "Diana Huertas",
                            className="author-name"
                        ),

                        html.Div(className="authors-divider"),

                        html.P(
                            "🎓 Universidad Central · Maestría en Analítica de Datos",
                            className="authors-university"
                        )
                    ])
                ]
            ),

            # ==================================================
            # BOTÓN
            # ==================================================
            dcc.Link(
                [
                    html.Span("Ingresar al Dashboard"),
                    html.Span("→", className="button-arrow")
                ],
                href="/dashboard",
                className="dashboard-button"
            )
        ]
    ),

    # ======================================================
    # PALETA INSTITUCIONAL
    # ======================================================
    html.Div(
        className="palette-card",
        children=[

            html.Div(
                className="palette-intro",
                children=[
                    html.Div("🎨", className="palette-icon"),

                    html.Div([
                        html.H3(
                            "Paleta de colores institucional",
                            className="palette-title"
                        ),

                        html.P(
                            "Estos colores representan la identidad visual de VigíaRed "
                            "Energía S.A.S. y se utilizan en todo el dashboard.",
                            className="palette-description"
                        )
                    ])
                ]
            ),

            html.Div(
                className="palette-colors",
                children=[

                    html.Div([
                        html.Div(className="color-circle color-blue"),
                        html.Div([
                            html.Strong("Azul institucional"),
                            html.Small("#17324D")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-green"),
                        html.Div([
                            html.Strong("Verde analítico"),
                            html.Small("#2A9D8F")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-amber"),
                        html.Div([
                            html.Strong("Ámbar atención"),
                            html.Small("#E9A23B")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-red"),
                        html.Div([
                            html.Strong("Rojo riesgo"),
                            html.Small("#D9534F")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-background"),
                        html.Div([
                            html.Strong("Fondo general"),
                            html.Small("#F4F6F8")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-white"),
                        html.Div([
                            html.Strong("Blanco tarjetas"),
                            html.Small("#FFFFFF")
                        ])
                    ], className="color-item"),

                    html.Div([
                        html.Div(className="color-circle color-gray"),
                        html.Div([
                            html.Strong("Texto secundario"),
                            html.Small("#607080")
                        ])
                    ], className="color-item")
                ]
            )
        ]
    )
])