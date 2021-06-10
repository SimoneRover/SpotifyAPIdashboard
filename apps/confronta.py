import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import *

import pandas as pd
import json
import numpy as np

from apps.spotify_api import *
from pytrends.request import TrendReq as Tr
import pycountry

from app import app
from assets import layout_components

app = app

# ----------------------------------------------------------------------------------------------------------------------
# API Setup


client_id = '5a40a4084bb2493988c7f01f3af5877c'
secret_id = '9493551bbfd24c7daedb374ddcf22003'
access_token = get_access_token(get_token_response(client_id, secret_id))
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# App layout

navbar = layout_components.navbar



layout = html.Div([
    html.Table(style={'width': '100%', 'border': '4px solid #59615b', 'background-color':'#343a40'}, children=[
        html.Tr(children=[
            # First Artist
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                # Dropdown selection
                    html.H4("Cerca:", className='text-light font-weight-bold'),
                    dcc.Dropdown(id="artist1Drop", placeholder="Cerca un artista..."),
                    html.Div(id='artist1_info', style={'display':'block', 'margin-left':'auto',
                                                       'margin-right':'auto'},
                         className="text-light font-weight-bold")
            ]),
            # Second Artist
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                # Dropdown selection
                        html.H4("Cerca:", className='text-light font-weight-bold'),
                        dcc.Dropdown(id="artist2Drop", placeholder="Cerca un artista..."),
                        html.Div(id='artist2_info', style={'display': 'block', 'margin-left': 'auto',
                                                           'margin-right': 'auto'},
                                 className="text-light font-weight-bold")
            ])
        ]),
        # Graphs rows
        html.Tr(style={},
                children=[
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                dcc.Graph(id="artist_features")
            ]),
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                dcc.Graph(id="artist_pops")
            ]),
        ]),
        html.Tr(children=[
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                dcc.RadioItems(
                    labelStyle = {"display": "inline-block", "margin-left": "15px"},
                    options=[
                        {"label": "Danceability", "value": 1},
                        {"label": "Energy", "value": 2},
                        {"label": "Acousticness", "value": 3},
                        {"label": "Instrumentalness", "value": 4},
                        {"label": "Liveness", "value": 5},
                        {"label": "Valence", "value": 6}
                        ],
                        value=1,
                        id="radioInput",
                        style={'text-align': 'center', 'color':'#f7f7f7'},
                        className='dcc_compon'
                    ),
                    dcc.Graph(id="features_distribution")
                ]),
            html.Td(style={'width': '50%', 'border': '4px solid #59615b'}, children=[
                    dcc.Graph(id="artist_trends")
                ])
            ]),
    ]),
    navbar
], style={'margin-left': '100px', 'margin-right': '100px'})

# ----------------------------------------------------------------------------------------------------------------------
# App Functions


# Returns dynamic options for dropdowns
def update_search_dropmenu(txt):
    artists = search_artists(txt, access_token)
    df = pd.json_normalize(artists)
    df = df.sort_values(by='followers.total', ascending=False)
    for col in df.columns:
        if col != 'name':
            del df[col]
    df = df.reset_index()
    df = df.drop(df.index[[x for x in range(len(df.index)) if x > 4]])
    options = []
    for name in df['name']:
        options.append({'label': name, 'value': name})

    return options

def artist_info(name):
    artist = search_artists(name, access_token)


    # Empty response check
    if len(artist) < 1:
        artist = search_artists('Smash Mouth', access_token)
    artist = artist[0]
    artist_id = artist['id']
    artist_name = artist['name']

    # ------- ARTIST INFO SECTION -----------------------
    followers = get_artist_followers_count(artist)
    genres = artist['genres']
    artist_popularity = artist['popularity']
    image_link = artist['images'][1]['url']
    img_height = artist['images'][1]['height']
    img_width = artist['images'][1]['width']

    # Image formatting
    if img_width == img_height:
        img_width = 350
        img_height = 350
    else:
        img_ratio = float(img_height) / float(img_width)
        if img_ratio > 1:
            img_height = 350
            img_ratio = float(img_width) / float(img_height)
            img_width = int(350 * img_ratio)
        else:
            img_height = int(350 * img_ratio)
            img_width = 350

    # Genre list formatting
    display_genres = ''
    for genre in genres:
        if display_genres != '':
            display_genres = display_genres + ', ' + genre.capitalize()
        else:
            display_genres = display_genres + genre.capitalize()

    return [artist_id, artist_name, artist_popularity, followers, image_link, img_width, img_height, display_genres]




# ----------------------------------------------------------------------------------------------------------------------
# App callbacks

# CALLBACK FOR UPDATING THE PAGE CONTENT
@app.callback(
    [Output('artist1_info', 'children'),
     Output('artist1Drop', 'placeholder'),
     Output('artist2_info', 'children'),
     Output('artist2Drop', 'placeholder')],
    Input('artist1Drop', 'value'),
    Input('artist2Drop', 'value'),
)
def artist_info_content(artist1_name, artist2_name):

    # Input check----------------------------
    if (artist1_name is None) | (artist1_name == ''):
        artist1_name = 'Smash Mouth'
    if (artist2_name is None) | (artist2_name == ''):
        artist2_name = 'Rick Astley'

    artist1_info = artist_info(artist1_name)  # [0artist_id, 1artist_name, 2artist_popularity, 3followers, 4image_link,
    artist2_info = artist_info(artist2_name)  # 5img_width, 6img_height, 7display_genres]

    info1_section = html.Center(children=[
        html.Img(style={'border': '4px solid #2450a3'}, src=str(artist1_info[4]), width=artist1_info[5], height=artist1_info[6]),
        html.Br(),
        artist1_name,
        html.Br(),
        'Popularity: {0}'.format(artist1_info[2]),
        html.Br(),
        'Followers: {0}'.format(artist1_info[3]),
        html.Br(),
        artist1_info[7]
    ])

    info2_section = html.Center(children=[
        html.Img(style={'border': '4px solid #b8392e'}, src=str(artist2_info[4]), width=artist2_info[5], height=artist2_info[6]),
        html.Br(),
        artist1_name,
        html.Br(),
        'Popularity: {0}'.format(artist2_info[2]),
        html.Br(),
        'Followers: {0}'.format(artist2_info[3]),
        html.Br(),
        artist2_info[7]
    ])
    return info1_section, artist1_name, info2_section, artist2_name

@app.callback(
    [Output('artist_features', 'figure'),
     Output('features_distribution', 'figure')],
     Input('artist1Drop', 'value'),
     Input('artist2Drop', 'value'),
     Input('radioInput', 'value')
)
def features_graphs(artist1_name, artist2_name, value):
    # Input check----------------------------
    if (artist1_name is None) | (artist1_name == ''):
        artist1_name = 'Smash Mouth'
    if (artist2_name is None) | (artist2_name == ''):
        artist2_name = 'Rick Astley'

    artist1_info = artist_info(artist1_name)
    artist2_info = artist_info(artist2_name)

    # INITIALIZING GRAPH THAT WILL BE RETURNED
    features_graph = go.Figure()
    features_distribution = go.Figure()

    art1_albums = pd.json_normalize(get_artist_albums(artist1_info[0], 'IT', access_token))
    art2_albums = pd.json_normalize(get_artist_albums(artist2_info[0], 'IT', access_token))

    for col in art1_albums.columns:
        if (col != 'name') & (col != 'id') & (col != 'release_date'):
            del art1_albums[col]

    for col in art2_albums.columns:
        if (col != 'name') & (col != 'id') & (col != 'release_date'):
            del art2_albums[col]

    art1_albums.drop_duplicates(subset=['id'])
    art2_albums.drop_duplicates(subset=['id'])

    art1_tracks = pd.DataFrame()
    art2_tracks = pd.DataFrame()
    tracks = pd.DataFrame()
    artist1_df = art1_tracks

    for alb_id, name in zip(art1_albums['id'], art1_albums['name']):
        tracks = get_album_tracks(alb_id, 'IT', access_token)
        tracks_df = pd.json_normalize(tracks)
        if 'items' in tracks_df.columns:
            tracks_df = pd.json_normalize(tracks['items'])
            tracks_df['album.id'] = alb_id
            tracks_df['album.name'] = name
            art1_tracks = art1_tracks.append(tracks_df)

    art1_tracks.reset_index(inplace=True)


    for alb_id, name in zip(art2_albums['id'], art2_albums['name']):
        tracks = get_album_tracks(alb_id, 'IT', access_token)
        tracks_df = pd.json_normalize(tracks)
        if 'items' in tracks_df.columns:
            tracks_df = pd.json_normalize(tracks['items'])
            tracks_df['album.id'] = alb_id
            tracks_df['album.name'] = name
            art2_tracks = art2_tracks.append(tracks_df)

    art2_tracks.reset_index(inplace=True)

    for col in art1_tracks.columns:
        if (col != 'id') & (col != 'name') & (col != 'album.id') & (col != 'album.name') & (col != 'popularity'):
            del art1_tracks[col]

    for col in art2_tracks.columns:
        if (col != 'id') & (col != 'name') & (col != 'album.id') & (col != 'album.name') & (col != 'popularity'):
            del art2_tracks[col]


    art1_tracks.sort_values(by='id', inplace=True)
    art2_tracks.sort_values(by='id', inplace=True)
    art1_tracks.drop_duplicates(subset=['id'], keep='first', inplace=True)
    art2_tracks.drop_duplicates(subset=['id'], keep='first', inplace=True)
    art1_tracks.sort_index(inplace=True)
    art2_tracks.sort_index(inplace=True)
    art1_tracks.reset_index(inplace=True, drop=True)
    art2_tracks.reset_index(inplace=True, drop=True)

    # BUILDING ART1_TRACKS FEATURES----------------------------------------------
    track_danceability = []
    track_energy = []
    track_acousticness = []
    track_instrumentalness = []
    track_liveness = []
    track_valence = []
    tracks_ids = []

    for track_id in art1_tracks['id']:
        tracks_ids.append(track_id)

    i = 0
    k = 0
    j = 0
    not_found_id = []
    req_string = ''
    for k in range(len(art1_tracks)):
        if (j == 0) | (j % 100 != 0):
            if req_string == '':
                req_string = req_string + str(tracks_ids[k])
            else:
                req_string = req_string + ',' + str(tracks_ids[k])
            j = j + 1
        if (j != 0) & ((j % 100 == 0) | ((j % 100 != 0) & (k == len(art1_tracks) - 1))):
            tracks_features = get_tracks_features(req_string, access_token) # ['audio_features']
            print(tracks_features)
            tracks_features = tracks_features['audio_features']
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

    art1_tracks.drop(inplace=True, index=not_found_id)

    art1_tracks['danceability'] = track_danceability
    art1_tracks['energy'] = track_energy
    art1_tracks['acousticness'] = track_acousticness
    art1_tracks['instrumentalness'] = track_instrumentalness
    art1_tracks['liveness'] = track_liveness
    art1_tracks['valence'] = track_valence

    # BUILDING DF FOR TRACKS FEATURES FOR ARTIST1
    art1_tracks_f_graph = art1_tracks.drop(['id', 'name', 'album.id', 'album.name'], axis=1)
    art1_tracks_f_graph = art1_tracks_f_graph.mean()
    art1_tracks_f_graph = pd.DataFrame(art1_tracks_f_graph, columns=['value'])

    categories = []
    for item in art1_tracks_f_graph.index:
        categories.append(item)
    categories.append(categories[0])
    features_graph.add_trace(go.Scatterpolar(
        theta=categories,
        r=art1_tracks_f_graph['value'].append(art1_tracks_f_graph.iloc[0]),
        fill='toself',
        name='Related avg'
    ))

    # BUILDING DFS FOR TRACKS FEATURES DISTRIBUTION GRAPHS
    danceability_distribution = []
    energy_distribution = []
    acousticness_distribution = []
    instrumentalness_distribution = []
    liveness_distribution = []
    valence_distribution = []

    danceability_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['danceability'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    energy_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['energy'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    acousticness_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['acousticness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    instrumentalness_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['instrumentalness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    liveness_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['liveness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    valence_distribution = art1_tracks.groupby(
        pd.cut(art1_tracks['valence'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    art1_danceability_distribution = danceability_distribution[['id']]
    art1_energy_distribution = energy_distribution[['id']]
    art1_acousticness_distribution = acousticness_distribution[['id']]
    art1_instrumentalness_distribution = instrumentalness_distribution[['id']]
    art1_liveness_distribution = liveness_distribution[['id']]
    art1_valence_distribution = valence_distribution[['id']]

    # BUILDING ART2_TRACKS FEATURES----------------------------------------------
    track_danceability = []
    track_energy = []
    track_acousticness = []
    track_instrumentalness = []
    track_liveness = []
    track_valence = []
    tracks_ids = []

    for track_id in art2_tracks['id']:
        tracks_ids.append(track_id)

    i = 0
    k = 0
    j = 0
    not_found_id = []
    req_string = ''
    for k in range(len(art2_tracks)):
        if (j == 0) | (j % 100 != 0):
            if req_string == '':
                req_string = req_string + str(tracks_ids[k])
            else:
                req_string = req_string + ',' + str(tracks_ids[k])
            j = j + 1
        if (j != 0) & ((j % 100 == 0) | ((j % 100 != 0) & (k == len(art2_tracks) - 1))):
            tracks_features = get_tracks_features(req_string, access_token)  # ['audio_features']
            tracks_features = tracks_features['audio_features']
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

    art2_tracks.drop(inplace=True, index=not_found_id)

    art2_tracks_features = art2_tracks

    art2_tracks_features['danceability'] = track_danceability
    art2_tracks_features['energy'] = track_energy
    art2_tracks_features['acousticness'] = track_acousticness
    art2_tracks_features['instrumentalness'] = track_instrumentalness
    art2_tracks_features['liveness'] = track_liveness
    art2_tracks_features['valence'] = track_valence

    # BUILDING DF FOR TRACKS FEATURES FOR ARTIST2
    art2_tracks_f_graph = art2_tracks.drop(['id', 'name', 'album.id', 'album.name'], axis=1)
    art2_tracks_f_graph = art2_tracks_f_graph.mean()
    art2_tracks_f_graph = pd.DataFrame(art2_tracks_f_graph, columns=['value'])

    categories = []
    for item in art2_tracks_f_graph.index:
        categories.append(item)
    categories.append(categories[0])
    features_graph.add_trace(go.Scatterpolar(
        theta=categories,
        r=art2_tracks_f_graph['value'].append(art2_tracks_f_graph.iloc[0]),
        fill='toself',
        name='Related avg'
    ))

    features_graph.update_layout(
        title_text='Average Audio Features from all tracks',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
    )
    features_graph.update_polars(
        radialaxis_range=[0, 1.0],
        radialaxis_showline=False,
        radialaxis_showticklabels=False
    )

    # BUILDING DFS FOR TRACKS FEATURES DISTRIBUTION GRAPHS
    danceability_distribution = []
    energy_distribution = []
    acousticness_distribution = []
    instrumentalness_distribution = []
    liveness_distribution = []
    valence_distribution = []
    danceability_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['danceability'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    energy_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['energy'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    acousticness_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['acousticness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    instrumentalness_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['instrumentalness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    liveness_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['liveness'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    valence_distribution = art2_tracks.groupby(
        pd.cut(art2_tracks['valence'], np.arange(0, 1.0 + 0.1, 0.1))).count()

    art2_danceability_distribution = danceability_distribution[['id']]
    art2_energy_distribution = energy_distribution[['id']]
    art2_acousticness_distribution = acousticness_distribution[['id']]
    art2_instrumentalness_distribution = instrumentalness_distribution[['id']]
    art2_liveness_distribution = liveness_distribution[['id']]
    art2_valence_distribution = valence_distribution[['id']]

    # BUILDING FEATURES DISTRIBUTION GRAPHS
    if value == 1:
       features_distribution.add_trace(go.Bar(x=art1_danceability_distribution.index.astype(str),
                                          y=art1_danceability_distribution['id']))
       features_distribution.add_trace(go.Bar(x=art2_danceability_distribution.index.astype(str),
                                              y=art2_danceability_distribution['id']))
    elif value == 2:

       features_distribution.add_trace(go.Bar(x=art1_energy_distribution.index.astype(str),
                                              y=art1_energy_distribution['id']))
       features_distribution.add_trace(go.Bar(x=art2_energy_distribution.index.astype(str),
                                          y=art2_energy_distribution['id']))
    elif value == 3:
        features_distribution.add_trace(go.Bar(x=art1_acousticness_distribution.index.astype(str),
                                          y=art1_acousticness_distribution['id']))
        features_distribution.add_trace(go.Bar(x=art2_acousticness_distribution.index.astype(str),
                                          y=art2_acousticness_distribution['id']))
    elif value == 4:
        features_distribution.add_trace(go.Bar(x=art1_instrumentalness_distribution.index.astype(str),
                                          y=art1_instrumentalness_distribution['id']))
        features_distribution.add_trace(go.Bar(x=art2_instrumentalness_distribution.index.astype(str),
                                          y=art2_instrumentalness_distribution['id']))
    elif value == 5:
        features_distribution.add_trace(go.Bar(x=art1_liveness_distribution.index.astype(str),
                                          y=art1_liveness_distribution['id']))
        features_distribution.add_trace(go.Bar(x=art2_liveness_distribution.index.astype(str),
                                          y=art2_liveness_distribution['id']))
    elif value == 6:
        features_distribution.add_trace(go.Bar(x=art1_valence_distribution.index.astype(str),
                                          y=art1_valence_distribution['id']))
        features_distribution.add_trace(go.Bar(x=art2_valence_distribution.index.astype(str),
                                          y=art2_valence_distribution['id']))

    features_distribution.update_layout(
        title_text='Audio Features distribution of all tracks',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
    )

    return features_graph, features_distribution


@app.callback(
    [Output('artist_pops', 'figure'),
     Output('artist_trends','figure')],
     Input('artist1Drop', 'value'),
     Input('artist2Drop', 'value')
)
def general_graphs(artist1_name, artist2_name):
    # Input check----------------------------
    if (artist1_name is None) | (artist1_name == ''):
        artist1_name = 'Smash Mouth'
    if (artist2_name is None) | (artist2_name == ''):
        artist2_name = 'Rick Astley'

    artist1_info = artist_info(artist1_name)  # [0artist_id, 1artist_name, 2artist_popularity, 3followers, 4image_link,
    artist2_info = artist_info(artist2_name)

    # INITIALIZING GRAPH THAT WILL BE RETURNED
    pop_graph = go.Figure()
    trends_graph = go.Figure()


    art1_albums = pd.json_normalize(get_artist_albums(artist1_info[0], 'IT', access_token))
    art2_albums = pd.json_normalize(get_artist_albums(artist2_info[0], 'IT', access_token))



    for col in art1_albums.columns:
        if (col != 'name') & (col != 'id') & (col != 'release_date'):
            del art1_albums[col]

    for col in art2_albums.columns:
        if (col != 'name') & (col != 'id') & (col != 'release_date'):
            del art2_albums[col]

    art1_albums.drop_duplicates(subset=['id'])
    art2_albums.drop_duplicates(subset=['id'])

    pops = []
    for alb_id in art1_albums['id']:
        pop = pd.json_normalize(get_album(alb_id, 'IT', access_token))
        if pop.size == 2:
            pop = np.NaN
        else:
            pop = int(pop['popularity'])
        pops.append(pop)

    art1_albums['popularity'] = pops

    pops = []
    for alb_id in art2_albums['id']:
        pop = pd.json_normalize(get_album(alb_id, 'IT', access_token))
        if pop.size == 2:
            pop = np.NaN
        else:
            pop = int(pop['popularity'])
        pops.append(pop)
    art2_albums['popularity'] = pops

    # FORMATTING DATES IN ART1_ALBUMS
    dates = []
    for name, date in zip(art1_albums['name'], art1_albums['release_date']):
        # Date formatting
        date = str(date)
        if len(date) == 10:
            splitted = date.split('-')
            new_date = splitted[0] + '-' + splitted[1]
        elif len(date) == 4:
            new_date = date + '-01'
        else:
            new_date = date

        dates.append(new_date)

    art1_albums['release_date'] = dates


    art1_albums.dropna(subset=['popularity'], inplace=True)
    art2_albums.dropna(subset=['popularity'], inplace=True)

    art1_albums.drop_duplicates(subset=['id'])
    art2_albums.drop_duplicates(subset=['id'])

    # BUILDING GRAPH FOR ART1 TRENDS
    if len(dates) >= 2:
        first_date = dates[0]
        last_date = dates[len(dates) - 1]
        if int(last_date.split('-')[0]) < 2004:
            last_date = '{0}-{1}'.format('2004', last_date.split('-')[1])
        timeframe_string = '{0}-01 {1}-01'.format(last_date, first_date)
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist1_info[1]], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        trends_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist1_info[1]],
            mode='lines',
            name='Google trends',
            line=dict(color='#2450a3')
        ))
    else:
        timeframe_string = 'all'
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist1_info[1]], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        trends_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist1_info[1]],
            mode='lines',
            name='Google trends',
            line=dict(color='#2450a3')
        ))




    # BUILDING POPULARITY OVER TIME GRAPH
    art1_albums = pd.DataFrame(art1_albums)
    art1_albums_graph = art1_albums.sort_values(by='popularity', ascending=False)
    art1_albums_graph.drop_duplicates(subset=['release_date'], inplace=True, keep='first')
    art1_albums_graph.sort_index(inplace=True)
    art1_albums_graph.reset_index(inplace=True, drop=True)

    pop_graph.add_trace(go.Scatter(
        x=art1_albums_graph['release_date'],
        y=art1_albums_graph['popularity'],
        hovertext=art1_albums['name'],
        mode='markers+lines',
        name='{0} albums popularity'.format(artist1_info[1])
    ))

    # FORMATTING DATES IN ART2_ALBUMS
    dates = []
    album_pops = []
    for name, date in zip(art2_albums['name'], art2_albums['release_date'], ):
        # Date formatting
        date = str(date)
        if len(date) == 10:
            splitted = date.split('-')
            new_date = splitted[0] + '-' + splitted[1]
        elif len(date) == 4:
            new_date = date + '-01'
        else:
            new_date = date

        dates.append(new_date)

    art2_albums['release_date'] = dates

    # BUILDING GRAPH FOR ART2 TRENDS
    if len(dates) >= 2:
        first_date = dates[0]
        last_date = dates[len(dates) - 1]
        if int(last_date.split('-')[0]) < 2004:
            last_date = '{0}-{1}'.format('2004', last_date.split('-')[1])
        timeframe_string = '{0}-01 {1}-01'.format(last_date, first_date)
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist2_info[1]], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        trends_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist2_info[1]],
            mode='lines',
            name='Google trends',
            line=dict(color='#b8392e')
        ))
    else:
        timeframe_string = 'all'
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist2_info[1]], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        trends_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist2_info[1]],
            mode='lines',
            name='Google trends',
            line=dict(color='#b8392e')
        ))

    trends_graph.update_layout(
        showlegend=True,
        legend_title_font_color="#ffffff",
        legend_title_font_size=20,
        legend_font_color="#ffffff",
        legend_font_size=15,
        legend_bgcolor="#343a40",
        legend_itemwidth=35,
        paper_bgcolor='#343a40',
        font_color='#ffffff',
        title_text='Popularity over time',
        title_font_color='#ffffff'
    )

    art2_albums = pd.DataFrame(art2_albums)
    art2_albums_graph = art2_albums.sort_values(by='popularity', ascending=False)
    art2_albums_graph.drop_duplicates(subset=['release_date'], inplace=True, keep='first')
    art2_albums_graph.sort_index(inplace=True)

    pop_graph.add_trace(go.Scatter(
        x=art2_albums_graph['release_date'],
        y=art2_albums_graph['popularity'],
        hovertext=art2_albums['name'],
        mode='markers+lines',
        name='{0} albums popularity'.format(artist2_info[1])
    ))

    pop_graph.update_layout(
        title_text='Albums\' popularity over time',
        title_font_color='#ffffff',
        font_color='#ffffff',
        showlegend=False,
        paper_bgcolor='#343a40',
    )




    pop_graph_container = dcc.Graph(figure=pop_graph)

    return pop_graph, trends_graph
    # artist*_info CONTAINS INFO ABOUT THE ARTIST IN THE FOLLOWING FORMAT List: [0artist_id, 1artist_name,
    # 2artist_popularity, 3followers, 4image_link, 5img_width, 6img_height, 7display_genres]
    # art*_albums CONTAINS INFO ABOUT ARTISTS ALBUMS
    # art*_tracks CONTAINS INFO ABOUT TRACKS IN ALBUMS
    # art*_tracks_features CONTAINS ALO INFO ABOUT TRACK FEATURES

# CALLBACK FOR FIRST DROPDOWN UPDATE
@app.callback(
    Output('artist1Drop', 'options'),
    [Input('artist1Drop', 'search_value')],
)
def update_search_dropmenu1(txt):
    if (txt is None) | (txt == ''):
        txt = "Smash Mouth"
    options = update_search_dropmenu(txt)
    return options

# CALLBACK FOR SECOND DROPDOWN UPDATE
@app.callback(
    Output('artist2Drop', 'options'),
    [Input('artist2Drop', 'search_value')]
)
def update_search_dropmenu2(txt):
    if (txt is None) | (txt == ''):
        txt = "Rick Astley"
    options = update_search_dropmenu(txt)

    return options

