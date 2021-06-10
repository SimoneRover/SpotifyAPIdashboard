# Imports
# ----------------------------------------------------------------------------------------------------------------------

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler as Ss

import plotly.graph_objects as go
import dash_html_components as html, dash_core_components as dcc, dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

from assets import layout_components
from app import app

app = app

# Data setup
# ----------------------------------------------------------------------------------------------------------------------

genres_data = pd.read_csv('datasets/data_by_genres.csv')
year_data = pd.read_csv('datasets/data_by_year.csv')

# Graphs
# ----------------------------------------------------------------------------------------------------------------------

# Audio features values over time
year_graph = go.Figure()
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['danceability'], mode='lines', name='Danceability'))
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['energy'], mode='lines', name='Energy'))
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['acousticness'], mode='lines', name='Acousticness'))
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['instrumentalness'], mode='lines', name='Instrumentalness'))
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['liveness'], mode='lines', name='Liveness'))
year_graph.add_trace(go.Scatter(x=year_data['year'], y=year_data['valence'], mode='lines', name='Valence'))
year_graph.update_yaxes(range=[0, 1.0])
year_graph.update_layout(
    title_text='Feature avg values over time',
    title_font_color='#ffffff',
    font_color='#ffffff',
    showlegend=True,
    paper_bgcolor='#343a40'
)

# Content table construction
content_table = html.Table(id='content-table', children=[
    html.Tr([
        html.Td([
            dcc.Graph(figure=year_graph)
        ])
    ])
], style={
    'width': '100%',
    'color': '#ffffff'
})

# Layout
# ----------------------------------------------------------------------------------------------------------------------

navbar = layout_components.homepage_navbar

layout = html.Div([
    html.Div(id='content-div'),
    html.Div([
        content_table
    ]),
    navbar
], style={'margin-left': '100px', 'margin-right': '100px'})

# App callbacks
# ----------------------------------------------------------------------------------------------------------------------


@app.callback(
    Output('content-div', 'children'),
    [Input('dropSearchBar', 'value')]
)
def load_page_content(selected_genre):

    # Audio features PCA plot
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    x = genres_data.loc[:, features].values
    x = Ss().fit_transform(x)

    pca2 = PCA(n_components=2)
    principalcomponents = pca2.fit_transform(x)
    principalcomponents_df = pd.DataFrame(data=principalcomponents, columns=['Audio features principal component 1',
                                                                             'Audio features principal component 2'])
    final_df = pd.concat([principalcomponents_df, genres_data['genres'], genres_data['popularity']], axis=1)

    final_df['genres'] = [str(x).capitalize() for x in final_df['genres']]

    pca_graph = go.Figure()
    pca_graph.update_layout(
        title_text='Feature avg values over genres',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40'
    )
    pca_graph.update_yaxes(
        range=[-6, 6]
    )
    pca_graph.update_xaxes(
        range=[-6, 6]
    )
    pca_graph.add_trace(go.Scatter(
        x=final_df['Audio features principal component 1'],
        y=final_df['Audio features principal component 2'],
        mode='markers',
        name='',
        text=final_df['genres']
    ))
    selected_genre_row = final_df[final_df['genres'] == selected_genre.capitalize()]
    pca_graph.add_trace(go.Scatter(
        x=selected_genre_row['Audio features principal component 1'],
        y=selected_genre_row['Audio features principal component 2'],
        mode='markers',
        marker=dict(color='red'),
        name='',
        text=str(selected_genre).capitalize()
    ))
    pca_graph.update_xaxes(
        title_text='Audio features principal component 1',
        title_font_color='#ffffff'
    )
    pca_graph.update_yaxes(
        title_text='Audio features principal component 2',
        title_font_color='#ffffff'
    )

    # Audio features polar plot
    selected_genre_row = genres_data[genres_data['genres'] == selected_genre]
    for col in selected_genre_row.columns:
        if col not in features:
            del selected_genre_row[col]
    temp_df = selected_genre_row.mean()
    temp_df = pd.DataFrame(temp_df, columns=['value'])
    categories2 = []
    for item in temp_df.index:
        categories2.append(item)
    categories2.append(categories2[0])
    polar_graph = go.Figure()
    polar_graph.add_trace(go.Scatterpolar(
        theta=categories2,
        r=temp_df['value'].append(temp_df.iloc[0]),
        fill='toself'
    ))
    polar_graph.update_layout(
        paper_bgcolor='#343a40',
        font_color='#ffffff',
        title_text='Genre avg audio features'
    )
    polar_graph.update_polars(
        radialaxis_range=[0, 1.0],
        radialaxis_showline=False,
        radialaxis_showticklabels=False
    )

    # Content table construction
    pca_table = html.Table(id='content-table', children=[
        html.Tr([
            html.Td([
                dcc.Graph(figure=pca_graph)
            ], style={
                'width': '65%'
            }),
            html.Td([
                dcc.Graph(figure=polar_graph)
            ], style={
                'width': '35%'
            })
        ])
    ], style={
        'width': '100%',
        'color': '#ffffff'
    })

    return pca_table
