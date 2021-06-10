# ----------------------------------------------------------------------------------------------------------------------
# Imports

import dash_html_components as html, dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from apps import tendenze, artist, confronta, homepage
from assets import layout_components
from app import app

# ----------------------------------------------------------------------------------------------------------------------
# Layout components

navbar = layout_components.navbar

# ----------------------------------------------------------------------------------------------------------------------
# App layout


app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page_layout', children=[
        html.Div(id='page_content', children=[]),
        navbar
    ])
])


# ----------------------------------------------------------------------------------------------------------------------
# App callbacks


@app.callback(
    Output('page_layout', 'children'),
    [Input('url', 'pathname')]
)
def display_page(path):
    print(path)
    if path == '/apps/tendenze':
        return tendenze.layout
    elif path == '/apps/artist':
        return artist.layout
    elif path == '/apps/confronta':
        return confronta.layout
    elif path == '/':
        return homepage.layout
    else:
        error_layout = dbc.Jumbotron(
            [
                html.H1("404: Not Found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {path} was not recognized...")
            ]
        )
        return error_layout


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=False, port=3000)
