import pandas as pd
import numpy as np

from apps.spotify_api import *

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler as Ss

import plotly.express as px
import plotly.graph_objects as go
import dash_html_components as html, dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from assets import layout_components
from app import app

app = app

# ----------------------------------------------------------------------------------------------------------------------
# API Setup

client_id = '5a40a4084bb2493988c7f01f3af5877c'
secret_id = '9493551bbfd24c7daedb374ddcf22003'
access_token = get_access_token(get_token_response(client_id, secret_id))

# ----------------------------------------------------------------------------------------------------------------------
# LAYOUT COMPONENTS

# Top Navigation Bar
navbar = layout_components.search_navbar

# Featured Playlists Table
featuredPlaylists = html.Div(
    children=[
        html.Div(id="tableDiv",
                 children=[]
                 )
    ]
)

# Featured Albums Table
featuredNewAlbums = html.Div(id="newAlbumsList",
                             children=[]
                             )

# ----------------------------------------------------------------------------------------------------------------------
# APP LAYOUT

layout = html.Div(children=[
    dbc.Row(children=[
        dbc.Col(width={"size": 5, "offset": 1},
                children=[
                    dbc.Row(children=[html.H2("Playlist in Tendenza", className="h1")]),
                    dbc.Row(children=[featuredPlaylists])
                ],
                className="table-responsive"
                ),
        dbc.Col(width={"size": 4, "offset": 2},
                children=[
                    dbc.Row(children=[html.H2("Album Nuovi in Tendenza", className="h1")]),
                    dbc.Row(children=[featuredNewAlbums])
                ],
                className="table-responsive",
                style={'margin-left': '150px'}
                )
    ]),
    html.Div(id='graphs_section', children=[]),
    navbar
    ],
    style={'margin-right': '50px', 'margin-left': '50px'}
)


# ----------------------------------------------------------------------------------------------
# APP CALLBACKS

@app.callback(
    Output(component_id='tableDiv', component_property='children'),
    [Input(component_id='dropSearchBar', component_property='value')]
)
def featured_table_content(country):
    fplaylists_df = pd.json_normalize(get_featured_playlists(access_token, str(country))['playlists']['items'])
    for column in fplaylists_df.columns:
        if (column != 'description') & (column != 'name') & (column != 'tracks.total'):
            del fplaylists_df[column]
    table_header = [
        html.Thead(html.Tr([html.Th("Nome"), html.Th("Descrizione"), html.Th("Tracce")]))
    ]
    rows = [(html.Tr([html.Td(name.capitalize()), html.Td(desc.capitalize()), html.Td(tracks_n)])) for name, desc, tracks_n in
            zip(fplaylists_df['name'], fplaylists_df['description'], fplaylists_df['tracks.total'])]
    table_body = [
        html.Tbody(rows)
    ]

    return [
        dbc.Table(table_header + table_body, bordered=True, dark=True, className="table table-hover")
    ]


@app.callback(
    Output(component_id='newAlbumsList', component_property='children'),
    [Input(component_id='dropSearchBar', component_property='value')]
)
def featured_new_albums_content(country):
    newAlb_df = pd.json_normalize(get_new_releases(country, access_token).json()['albums']['items'])

    for column in newAlb_df.columns:
        if (column != 'album_type') & (column != 'name') & (column != 'images') & (column != 'id'):
            del newAlb_df[column]

    newAlb_df = newAlb_df.drop(newAlb_df.index[[x for x in range(len(newAlb_df.index)) if x > 9]])

    lil_images = newAlb_df['images']
    for i, ele in lil_images.items():
        lil_images[i] = ele[2]['url']

    newAlb_df['images'] = lil_images

    table_header = [
        html.Thead(html.Tr([html.Th("Immagine Album"), html.Th("Nome"), html.Th("Tipo Album")]))
    ]
    rows = [(html.Tr([html.Td(html.Img(className="imgRelease", src=image)), html.Td(name.capitalize()), html.Td(type.capitalize())])) for
            image, name, type, id in
            zip(newAlb_df['images'], newAlb_df['name'], newAlb_df['album_type'], newAlb_df['id'])]
    table_body = [
        html.Tbody(rows)
    ]

    return [
        dbc.Table(table_header + table_body, bordered=True, dark=True, className="table table-hover")
    ]


@app.callback(
    Output('graphs_section', 'children'),
    [Input('dropSearchBar', 'value')]
)
def generate_graph_section(country):
    # Dataframe featured playlists
    f_playlists = get_featured_playlists(access_token, country)['playlists']['items']
    f_playlists_df = pd.json_normalize(f_playlists)
    for col in f_playlists_df:
        if (col != 'id') & (col != 'tracks.href') & (col != 'tracks.total') & (col != 'name'):
            del f_playlists_df[col]

    # Dataframe tracks in featured playlists
    tracks_df = pd.DataFrame()
    total_tracks_df = pd.DataFrame()
    for url, p_id, p_name in zip(f_playlists_df['tracks.href'], f_playlists_df['id'], f_playlists_df['name']):
        tracks = get_playlist_tracks_from_url(url, country, access_token)['items']
        tracks_df = pd.json_normalize(tracks)
        tracks_df['playlist.id'] = p_id
        tracks_df['playlist.name'] = p_name
        total_tracks_df = total_tracks_df.append(tracks_df)
    total_tracks_df.reset_index(inplace=True)
    for col in total_tracks_df:
        if (col != 'track.id') & (col != 'track.popularity') & (col != 'playlist.id') & (col != 'playlist.name'):
            del total_tracks_df[col]

    track_danceability = []
    track_energy = []
    track_acousticness = []
    track_instrumentalness = []
    track_liveness = []
    track_valence = []
    tracks_ids = []

    for track_id in total_tracks_df['track.id']:
        tracks_ids.append(track_id)

    # Request audio features for each track (requesting multiple track at a time)
    i = 0
    k = 0
    j = 0
    not_found_id = []
    req_string = ''
    for k in range(len(total_tracks_df)):
        if (j == 0) | (j % 100 != 0):
            if req_string == '':
                req_string = req_string + str(tracks_ids[k])
            else:
                req_string = req_string + ',' + str(tracks_ids[k])
            j = j + 1
        if (j != 0) & ((j % 100 == 0) | ((j % 100 != 0) & (k == len(total_tracks_df) - 1))):
            tracks_features = get_tracks_features(req_string, access_token)['audio_features']
            for track_features in tracks_features:
                if track_features is not None:
                    track_danceability.append(track_features['danceability'])
                    track_energy.append(track_features['energy'])
                    track_acousticness.append(track_features['acousticness'])
                    track_instrumentalness.append(track_features['instrumentalness'])
                    track_liveness.append(track_features['liveness'])
                    track_valence.append(track_features['valence'])
                else:
                    not_found_id.append(i)
                i = i + 1
            req_string = ''
            j = 0
    # Clear empty rows
    total_tracks_df.drop(inplace=True, index=not_found_id)

    total_tracks_df['danceability'] = track_danceability
    total_tracks_df['energy'] = track_energy
    total_tracks_df['acousticness'] = track_acousticness
    total_tracks_df['instrumentalness'] = track_instrumentalness
    total_tracks_df['liveness'] = track_liveness
    total_tracks_df['valence'] = track_valence

    # Features distribution thought tracks
    danceability_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['danceability'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    energy_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['energy'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    acousticness_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['acousticness'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    instrumentalness_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['instrumentalness'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    liveness_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['liveness'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    valence_distribution = total_tracks_df.groupby(
        pd.cut(total_tracks_df['valence'], np.arange(0, 1.0 + 0.05, 0.05))).count()
    danceability_distribution = danceability_distribution[['track.id']]
    energy_distribution = energy_distribution[['track.id']]
    acousticness_distribution = acousticness_distribution[['track.id']]
    instrumentalness_distribution = instrumentalness_distribution[['track.id']]
    liveness_distribution = liveness_distribution[['track.id']]
    valence_distribution = valence_distribution[['track.id']]

    # Distribution graphs
    danceability_distribution_graph = go.Figure()
    danceability_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in danceability_distribution.index.astype(str)],
        y=danceability_distribution['track.id'])
    )

    energy_distribution_graph = go.Figure()
    energy_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in energy_distribution.index.astype(str)],
        y=energy_distribution['track.id'])
    )

    acousticness_distribution_graph = go.Figure()
    acousticness_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in acousticness_distribution.index.astype(str)],
        y=acousticness_distribution['track.id'])
    )

    instrumentalness_distribution_graph = go.Figure()
    instrumentalness_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in instrumentalness_distribution.index.astype(str)],
        y=instrumentalness_distribution['track.id'])
    )

    liveness_distribution_graph = go.Figure()
    liveness_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in liveness_distribution.index.astype(str)],
        y=liveness_distribution['track.id'])
    )

    valence_distribution_graph = go.Figure()
    valence_distribution_graph.add_trace(go.Bar(
        x=[str(x).split(', ')[1].replace(']','') for x in valence_distribution.index.astype(str)],
        y=valence_distribution['track.id'])
    )

    # Distribution graphs layout update
    danceability_distribution_graph.update_layout(
        title_text='Danceability feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    energy_distribution_graph.update_layout(
        title_text='Energy feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    acousticness_distribution_graph.update_layout(
        title_text='Acousticness feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    instrumentalness_distribution_graph.update_layout(
        title_text='Instrumentalness feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    liveness_distribution_graph.update_layout(
        title_text='Liveness feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    valence_distribution_graph.update_layout(
        title_text='Valence feature distribution',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )

    # PCA graphs
    features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    x = total_tracks_df.loc[:, features].values

    x = Ss().fit_transform(x)

    pca2 = PCA(n_components=2)
    principalComponents2 = pca2.fit_transform(x)
    principalDf2 = pd.DataFrame(data=principalComponents2, columns=['Audio features principal component 1', 'Audio features principal component 2'])

    final_df2 = pd.concat([principalDf2, total_tracks_df['playlist.name'], total_tracks_df['track.popularity']], axis=1)
    final_df2 = final_df2[final_df2['track.popularity'] > 0]

    pc2_pid = px.scatter(final_df2, x=final_df2['Audio features principal component 1'], y=final_df2['Audio features principal component 2'],
                         color=final_df2['playlist.name'])

    pc2_pop = px.scatter(final_df2, x=final_df2['Audio features principal component 1'], y=final_df2['Audio features principal component 2'],
                         color=final_df2['track.popularity'])

    pc2_pid.update_layout(
        title_text='Audio features PCA with playlists',
        title_font_color='#ffffff',
        font_color='#ffffff',
        paper_bgcolor='#343a40',
        margin_r=300
    )
    pc2_pop.update_layout(
        title_text='Audio features PCA with popularity',
        title_font_color='#ffffff',
        font_color='#ffffff',
        paper_bgcolor='#343a40',
        margin_r=300
    )
    pc2_pid.update_yaxes(range=[-6, 6])
    pc2_pid.update_xaxes(range=[-6, 6])
    pc2_pop.update_yaxes(range=[-6, 6])
    pc2_pop.update_xaxes(range=[-6, 6])

    # Table construction
    graphs_table = html.Center([
        html.Table(children=[
            html.Tr([
                html.Td([
                    dcc.Graph(figure=danceability_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                }),
                html.Td([
                    dcc.Graph(figure=energy_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                })
            ]),
            html.Tr([
                html.Td([
                    dcc.Graph(figure=acousticness_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                }),
                html.Td([
                    dcc.Graph(figure=instrumentalness_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                })
            ]),
            html.Tr([
                html.Td([
                    dcc.Graph(figure=liveness_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                }),
                html.Td([
                    dcc.Graph(figure=valence_distribution_graph)
                ], style={
                    'width': '50%',
                    'border': '4px solid #59615b'
                })
            ]),
            html.Tr([
                html.Td(children=[
                    dcc.Graph(figure=pc2_pid)
                ], colSpan=2, style={'border': '4px solid #59615b'})
            ]),
            html.Tr([
                html.Td(children=[
                    dcc.Graph(figure=pc2_pop)
                ], colSpan=2, style={'border': '4px solid #59615b'})
            ])
        ], style={
            'width': '100%'
        })
    ])

    return graphs_table
