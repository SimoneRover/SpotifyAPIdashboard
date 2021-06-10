import dash_html_components as html, dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "padding": "1rem 1rem",
    "background-color": "#59615b",
}

country_list = [{"value": "AD", "label": "Andorra"},
                {"value": "AE", "label": "United Arab Emirates"},
                {"value": "AR", "label": "Argentina"},
                {"value": "AT", "label": "Austria"},
                {"value": "AU", "label": "Australia"},
                {"value": "BE", "label": "Belgium"},
                {"value": "BR", "label": "Brazil"},
                {"value": "CA", "label": "Canada"},
                {"value": "CH", "label": "Switzerland"},
                {"value": "CN", "label": "China"},
                {"value": "CZ", "label": "Czech Republic"},
                {"value": "DE", "label": "Germany"},
                {"value": "DK", "label": "Denmark"},
                {"value": "ES", "label": "Spain"},
                {"value": "FI", "label": "Finland"},
                {"value": "FR", "label": "France"},
                {"value": "GB", "label": "United Kingdom of Great Britain and Northern Ireland"},
                {"value": "GR", "label": "Greece"},
                {"value": "HR", "label": "Croatia"},
                {"value": "IE", "label": "Ireland"},
                {"value": "IL", "label": "Israel"},
                {"value": "IN", "label": "India"},
                {"value": "IS", "label": "Iceland"},
                {"value": "IT", "label": "Italy"},
                {"value": "JP", "label": "Japan"},
                {"value": "KR", "label": "Korea, Republic of"},
                {"value": "MX", "label": "Mexico"},
                {"value": "NL", "label": "Netherlands"},
                {"value": "NO", "label": "Norway"},
                {"value": "NZ", "label": "New Zealand"},
                {"value": "PL", "label": "Poland"},
                {"value": "PT", "label": "Portugal"},
                {"value": "RO", "label": "Romania"},
                {"value": "RS", "label": "Serbia"},
                {"value": "RU", "label": "Russian Federation"},
                {"value": "SE", "label": "Sweden"},
                {"value": "SG", "label": "Singapore"},
                {"value": "SI", "label": "Slovenia"},
                {"value": "SK", "label": "Slovakia"},
                {"value": "TR", "label": "Turkey"},
                {"value": "TW", "label": "Taiwan, Province of China"},
                {"value": "UA", "label": "Ukraine"},
                {"value": "US", "label": "United States of America"},
                {"value": "UY", "label": "Uruguay"},
                {"value": "ZA", "label": "South Africa"}]

navbar = html.Div(
    [
        dbc.Row(children=[
            dbc.Col(children=[html.Img(src='/assets/icona.png',
                                       style={
                                           "width": "50%"
                                       }
                                       )],
                    width=1
                    ),
            dbc.Col(html.H2("SPOTIFY DASHBOARD", className="h1",
                            style={
                                "text-align": "left"
                            }),
                    width="auto"
                    ),
        ]),

        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink("Generi", href="/", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Tendenze", href="/apps/tendenze", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Artisti", href="/apps/artist", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Confronta Artisti", href="/apps/confronta", active="exact",
                            className='text-light font-weight-bold'),
            ],
            vertical=False,
            pills=True

        ),
    ],
    style=SIDEBAR_STYLE,
)

artist_navbar = html.Div(
    [
        dbc.Row(children=[
            dbc.Col(children=[html.Img(src='/assets/icona.png',
                                       style={
                                           "width": "50%"
                                       }
                                       )],
                    width=1
                    ),
            dbc.Col(html.H2("SPOTIFY DASHBOARD", className="h1",
                            style={
                                "text-align": "left"
                            }),
                    width="auto"
                    ),
        ]),

        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink("Generi", href="/", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Tendenze", href="/apps/tendenze", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Artisti", href="/apps/artist", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Confronta Artisti", href="/apps/confronta", active="exact",
                            className='text-light font-weight-bold'),
                dbc.Col(width={"size": 0.5, "offset": 4},
                        children=[html.H4("Cerca:", className='text-light font-weight-bold')],
                        style={'margin-right': '5px'}
                        ),

                dbc.Col(width={"size": 4, "offset": 0},
                        children=[dcc.Dropdown(id="dropBar", placeholder="Cerca un artista...")]
                        ),
                # dbc.Col(dbc.Button("Cerca", id="btnIn", disabled=True, color="success", className="text-light font-weight-bold"))

            ],
            vertical=False,
            pills=True

        ),
    ],
    style=SIDEBAR_STYLE,
)

search_navbar = html.Div(
    [
        dbc.Row(children=[
            dbc.Col(children=[html.Img(src='/assets/icona.png',
                                       style={
                                           "width": "50%"
                                       }
                                       )],
                    width=1
                    ),
            dbc.Col(html.H2("SPOTIFY DASHBOARD", className="h1",
                            style={"text-align": "left"}
                            ),
                    width="auto"
                    ),
        ]),

        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink("Generi", href="/", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Tendenze", href="/apps/tendenze", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Artisti", href="/apps/artist", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Confronta Artisti", href="/apps/confronta", active="exact",
                            className='text-light font-weight-bold'),
                dbc.Col(width={"size": 0.5, "offset": 4},
                        children=[html.H4("Cerca:", className='text-light font-weight-bold')],
                        style={'margin-right': '5px'}
                        ),
                dbc.Col(width={"size": 4, "offset": 0},
                        children=[
                            dcc.Dropdown(id="dropSearchBar", placeholder="Seleziona un paese...", options=country_list,
                                         value="IT")],
                        ),
                # dbc.Col(dbc.Button("Search", id="btnIn", color="success", className="text-light font-weight-bold"))

            ],
            vertical=False,
            pills=True

        ),
    ],
    style=SIDEBAR_STYLE,
)


genres_data = pd.read_csv('datasets/data_by_genres.csv')

genre_list = []
for genre in genres_data['genres']:
    genre_list.append({'value': genre, 'label': str(genre).capitalize()})

homepage_navbar = html.Div(
    [
        dbc.Row(children=[
            dbc.Col(children=[html.Img(src='/assets/icona.png',
                                       style={
                                           "width": "50%"
                                       }
                                       )],
                    width=1
                    ),
            dbc.Col(html.H2("SPOTIFY DASHBOARD", className="h1",
                            style={"text-align": "left"}
                            ),
                    width="auto"
                    ),
        ]),

        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink("Generi", href="/", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Tendenze", href="/apps/tendenze", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Artisti", href="/apps/artist", active="exact", className='text-light font-weight-bold'),
                dbc.NavLink("Confronta Artisti", href="/apps/confronta", active="exact",
                            className='text-light font-weight-bold'),
                dbc.Col(width={"size": 0.5, "offset": 4},
                        children=[html.H4("Cerca:", className='text-light font-weight-bold')],
                        style={'margin-right': '5px'}
                        ),
                dbc.Col(width={"size": 4, "offset": 0},
                        children=[
                            dcc.Dropdown(id="dropSearchBar", placeholder="Seleziona un genere...", options=genre_list,
                                         value='pop')],
                        ),
                # dbc.Col(dbc.Button("Search", id="btnIn", color="success", className="text-light font-weight-bold"))

            ],
            vertical=False,
            pills=True

        ),
    ],
    style=SIDEBAR_STYLE,
)
