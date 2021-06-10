from pytrends.request import TrendReq as Tr
from apps.spotify_api import *
import plotly.graph_objects as go

client_id = '5a40a4084bb2493988c7f01f3af5877c'
secret_id = '9493551bbfd24c7daedb374ddcf22003'
access_token = get_access_token(get_token_response(client_id, secret_id))

input_string = 'Rick Astley'
artist = search_artists(input_string, access_token)[0]
artist_id = artist['id']
albums = get_artist_albums(artist_id, 'IT', access_token)
dates = []
album_pops = []
for album in albums:
    album_data = get_album(album['id'], 'IT', access_token)
    # Date formatting
    album_date = str(album_data['release_date'])
    if len(album_date) == 10:
        splitted = album_date.split('-')
        new_date = splitted[0] + '-' + splitted[1]
    elif len(album_date) == 4:
        new_date = album_date + '-01'
    else:
        new_date = album_date
    if indexOf(dates, new_date) != -1:
        if album_data['popularity'] > album_pops[indexOf(dates, new_date)]:
            album_pops[indexOf(dates, new_date)] = int(album_data['popularity'])
    else:
        dates.append(new_date)
        album_pops.append(album_data['popularity'])

first_date = dates[0]
last_date = dates[len(dates)-1]
if int(last_date.split('-')[0]) < 2004:
     last_date = '{0}-{1}'.format('2004', last_date.split('-')[1])
timeframe_string = '{0}-01 {1}-01'.format(last_date, first_date)
pytrend = Tr(hl='en-GB', tz=360)
pytrend.build_payload(kw_list=['Smash Mouth'], cat=0, timeframe=timeframe_string, geo='', gprop='')
artist_trend_df = pytrend.interest_over_time()

fig = go.Figure()
fig.add_trace(go.Scatter(
     x=artist_trend_df.index,
     y=artist_trend_df['Smash Mouth'],
     mode='lines'
))
fig.show()



