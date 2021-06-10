# ----------------------------------------------------------------------------------------------------------------------
# Imports


import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.graph_objs import *

import pandas as pd

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
# App layout

navbar = layout_components.artist_navbar

graph_layout = Layout(
    paper_bgcolor='#343a40'
)

layout = html.Div([
    # Content table
    html.Div(id='page_content', children=[
        html.Center(children=[
        ], id='artist_content')
    ]),
    # Nav bar
    navbar
])


# ----------------------------------------------------------------------------------------------------------------------
# App callbacks


@app.callback(
    [Output('artist_content', 'children'),
     Output('dropBar', 'placeholder')],
    [Input('dropBar', 'value')]
)
def update_page(artist_name):
    # Input check
    if (artist_name is None) | (artist_name == ''):
        artist_name = 'Smash Mouth'
    artist = search_artists(artist_name, access_token)

    # Empty response check
    if len(artist) < 1:
        artist = search_artists('Smash Mouth', access_token)
    artist = artist[0]
    artist_id = artist['id']
    artist_name = artist['name']

    # Get artist populars graph
    tops = get_artist_tops(artist_id, 'IT', access_token)['tracks']
    tops_df = pd.json_normalize(tops)
    for col in tops_df.columns:
        if (col != 'name') & (col != 'popularity'):
            del tops_df[col]
    short_titles = []
    for song_title in tops_df['name']:
        if len(song_title) > 19:
            short_titles.append(str(song_title)[0:20] + '...')
        else:
            short_titles.append(str(song_title))
    tops_df['short_name'] = short_titles
    tops_df = tops_df.drop_duplicates(subset='short_name', keep='first')
    tops_df = tops_df.sort_values(by='popularity', ascending=True)
    print(tops_df['short_name'].to_string())
    titolo = '{0} top tracks'.format(artist_name)
    populars = go.Figure()
    populars.add_trace(go.Bar(
        x=tops_df['popularity'],
        y=tops_df['short_name'],
        orientation='h'
    ))
    populars.update_xaxes(
        range=[0, 100]
    )
    populars.update_layout(
        title_text=titolo,
        title_font_color='#ffffff',
        font_color='#ffffff',
        paper_bgcolor='#343a40',
        colorway=['#4fa649']
    )
    populars_container = dcc.Graph(figure=populars)

    # Artist's song features graph
    req_string = ''
    for track in tops:
        if req_string != '':
            req_string = req_string + ',' + track['id']
        else:
            req_string = req_string + track['id']
    audio_features = get_tracks_features(req_string, access_token)['audio_features']

    # Analysis clear
    i = 0
    for song in audio_features:
        if (song is None) | (song == 'null'):
            del audio_features[i]
        i = i + 1
    audiofeatures_df = pd.json_normalize(audio_features)
    for col in audiofeatures_df.columns:
        if (col != 'danceability') & (col != 'energy') & (col != 'acousticness') & (col != 'instrumentalness') & (
                col != 'liveness') & (col != 'valence'):
            del audiofeatures_df[col]
    # FEATURES GRAPH
    fig2 = go.Figure()
    avg_audiofeatures_df = audiofeatures_df.mean()
    avg_audiofeatures_df = pd.DataFrame(avg_audiofeatures_df, columns=['value'])
    categories2 = []
    for item in avg_audiofeatures_df.index:
        categories2.append(item)
    categories2.append(categories2[0])
    fig2.add_trace(go.Scatterpolar(
        theta=categories2,
        r=avg_audiofeatures_df['value'].append(avg_audiofeatures_df.iloc[0]),
        fill='toself',
        name='Artist avg'
    ))
    fig2.update_layout(
        paper_bgcolor='#343a40',
        font_color='#ffffff'
    )
    fig2.update_polars(
        radialaxis_range=[0, 1.0],
        radialaxis_showline=False,
        radialaxis_showticklabels=False
    )
    audio_features_graph = dcc.Graph(figure=fig2)

    # Get artist infos
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
            display_genres = display_genres + ', ' + str(genre).capitalize()
        else:
            display_genres = display_genres + str(genre).capitalize()

    info_section = html.Center(children=[
        html.Img(src=str(image_link), width=img_width, height=img_height, style={'border': '3px solid white', 'border-radius': '20%'}),
        html.Br(),
        artist_name,
        html.Br(),
        'Popularity: {0}'.format(artist_popularity),
        html.Br(),
        'Followers: {0}'.format(followers),
        html.Br(),
        display_genres
    ])

    info_table = html.Table([
        html.Tr([
            # info section
            html.Td([
                html.Center([
                    info_section
                ])
            ]),
            # audio features graph
            html.Td([
                html.Center([
                    audio_features_graph
                ])
            ])
        ])
    ])

    centered_info_table = html.Center([
        info_table
    ])

    # Get artist popularity over time
    albums = get_artist_albums(artist_id, 'IT', access_token)

    dates = []
    album_pops = []
    album_names = []
    for album in albums:
        album_data = get_album(album['id'], 'IT', access_token)
        print(album_data)

        # Date formatting
        album_date = str(album_data['release_date'])
        if len(album_date) == 10:
            splitted = album_date.split('-')
            new_date = splitted[0] + '-' + splitted[1]
        elif len(album_date) == 4:
            new_date = album_date + '-01'
        else:
            new_date = album_date

        # Check if albums are released on the same date, select the most popular
        if indexOf(dates, new_date) != -1:
            if album_data['popularity'] > album_pops[indexOf(dates, new_date)]:
                album_pops[indexOf(dates, new_date)] = int(album_data['popularity'])
        else:
            dates.append(new_date)
            album_names.append(album_data['name'])
            album_pops.append(album_data['popularity'])

    dfd = {'Dates': dates, 'Popularity': album_pops, 'Name': album_names}
    df = pd.DataFrame(dfd)

    pop_graph = go.Figure(layout=graph_layout)
    if len(dates) >= 2:
        pop_graph.add_trace(go.Scatter(
            x=df['Dates'],
            y=df['Popularity'],
            hovertext=df['Name'],
            mode='lines',
            name='Albums popularity',
            line=dict(color='#138f32')
        ))
        pop_graph.update_layout(
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

    # Get Google Trends data
    if len(dates) >= 2:
        first_date = dates[0]
        last_date = dates[len(dates) - 1]
        if int(last_date.split('-')[0]) < 2004:
            last_date = '{0}-{1}'.format('2004', last_date.split('-')[1])
        timeframe_string = '{0}-01 {1}-01'.format(last_date, first_date)
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist_name], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        pop_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist_name],
            mode='lines',
            name='Google trends',
            line=dict(color='#45a0d9')
        ))
    else:
        timeframe_string = 'all'
        pytrend = Tr(hl='it-IT', tz=360)
        pytrend.build_payload(kw_list=[artist_name], cat=0, timeframe=timeframe_string, geo='', gprop='')
        artist_trend_df = pytrend.interest_over_time()
        pop_graph.add_trace(go.Scatter(
            x=artist_trend_df.index,
            y=artist_trend_df[artist_name],
            mode='lines',
            name='Google trends',
            line=dict(color='#45a0d9')
        ))
        pop_graph.update_layout(
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
    pop_graph_container = dcc.Graph(figure=pop_graph)

    # Get artist related
    artist_related = get_artist_related(artist_id, access_token)
    related_list = artist_related[0:3]
    related_list2 = artist_related[3:6]
    related_container = html.Center([
        html.Table(children=(
            html.Tr([
                html.Td(style={'width': '33%'}, children=[
                    html.Center([
                        html.Img(src=str(artist_r['images'][2]['url']), width=160, height=160, style={'border-radius': '50%', 'border': '3px solid white'}),
                        html.Br(),
                        artist_r['name'],
                        html.Br(),
                        'Followers: ' + str(get_artist_followers_count(artist_r))
                    ])
                ]) for artist_r in related_list
            ]),
            html.Tr([
                html.Td(style={'width': '33%'}, children=[
                    html.Center([
                        html.Img(src=str(artist_r['images'][2]['url']), width=160, height=160, style={'border-radius': '50%', 'border': '3px solid white'}),
                        html.Br(),
                        artist_r['name'],
                        html.Br(),
                        'Followers: ' + str(get_artist_followers_count(artist_r))
                    ])
                ]) for artist_r in related_list2
            ])
        ))
    ])

    # Get artist related top tracks avg features polar graph
    artist_related_list = artist_related[0:6]
    related_ids = []
    related_tops_ids = []
    for artist_r in artist_related_list:
        related_ids.append(artist_r['id'])

    for related_id in related_ids:
        top_tracks = get_artist_tops(related_id, 'IT', access_token)['tracks']
        for track in top_tracks:
            related_tops_ids.append(track['id'])
    i = 0
    req_string = ''
    while (i < 50) & (i < len(related_tops_ids)):
        if i == 0:
            req_string = req_string + related_tops_ids[i]
        else:
            req_string = req_string + ',' + related_tops_ids[i]
        i = i + 1
    related_audio_features = get_tracks_features(req_string, access_token)["audio_features"]
    i = 0
    for song in related_audio_features:
        if (song is None) | (song == 'null'):
            del related_audio_features[i]
        i = i + 1
    rel_features_df = pd.json_normalize(related_audio_features)
    for col in rel_features_df.columns:
        if (col != 'danceability') & (col != 'energy') & (col != 'acousticness') & (col != 'instrumentalness') & (
                col != 'liveness') & (col != 'valence'):
            del rel_features_df[col]

    avg_relaudiofeatures_df = rel_features_df.mean()
    avg_relaudiofeatures_df = pd.DataFrame(avg_relaudiofeatures_df, columns=['value'])

    categories3 = []
    for item in avg_relaudiofeatures_df.index:
        categories3.append(item)
    categories3.append(categories3[0])
    fig2.add_trace(go.Scatterpolar(
        theta=categories3,
        r=avg_relaudiofeatures_df['value'].append(avg_relaudiofeatures_df.iloc[0]),
        fill='toself',
        name='Related avg'
    ))

    # Global trend map
    pytrend.build_payload(kw_list=[artist_name])
    geo_result = pytrend.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)
    iso3 = []
    country_interest = []
    for iso2, interest in zip(geo_result['geoCode'], geo_result[artist_name]):
        if pycountry.countries.get(alpha_2=iso2) is not None:
            iso3_code = pycountry.countries.get(alpha_2=iso2).alpha_3
            iso3.append(iso3_code)
        else:
            iso3.append('')
        country_interest.append(interest)

    i = 0
    for iso3_code, interest in zip(iso3, country_interest):
        if iso3_code == '':
            del iso3[i]
            del country_interest[i]
        i = i + 1

    global_dict = {'Country': iso3, 'Interest': country_interest}
    global_interest_df = pd.DataFrame(global_dict)

    global_interest = go.Figure()
    global_interest.add_trace(go.Choropleth(
        locations=global_interest_df['Country'],
        z=global_interest_df['Interest'],
        colorscale='greens',
        colorbar_title='Interest'
    ))
    global_interest.update_layout(
        height=800,
        autosize=True,
        title_text='Artist global interest',
        paper_bgcolor='#343a40',
        font_color='#ffffff'
    )
    global_graph_container = dcc.Graph(figure=global_interest)

    # Returned table
    content_table = html.Table(children=[
        # Related artists row
        html.Tr(id='artist_row', children=[
            html.Td(id='artist_infos', children=[centered_info_table], style={'border':'4px solid #59615b'}),
            html.Td(id='related', children=[related_container], style={'border':'4px solid #59615b'})
        ]),
        # Graphs row
        html.Tr(children=[
            # Artist's popular songs graph
            html.Td(id='artist_overtime', children=[pop_graph_container], style={'border':'4px solid #59615b'}),
            # Artist's popularity over time graph
            html.Td(id='artists_populars', children=[populars_container], style={'border':'4px solid #59615b'})
        ]),
        # Artist's global interest
        html.Tr(children=[
            html.Td(id='global_graph', children=[global_graph_container], colSpan=2, style={'border':'4px solid #59615b'})
        ], style={'height': 800})
    ], style={
        'background-color': '#343a40',
        'color': '#ffffff'
    })

    return content_table, artist_name


# -----------------------------------------------------------------------------------------------------------------------


@app.callback(
    [Output(component_id='dropBar', component_property='options'),
     Output('dropBar', 'search_value')],
    Input(component_id='dropBar', component_property='search_value'),
    Input('dropBar', 'value')
)
def update_search_dropmenu(txt, value):
    if (txt is None) | (txt == ''):
        txt = "Smash Mouth"
        value = "Cerca un artista..."
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

    return options, value
