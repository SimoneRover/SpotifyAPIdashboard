import numpy as np
import requests as req
import base64


# returns the response for the access token (raw, not json)
def get_token_response(clientid, secretid):
    url = 'https://accounts.spotify.com/api/token'
    to_encode = '{0}:{1}'.format(clientid, secretid)
    to_bytes = to_encode.encode('ascii')
    base64bytes = base64.b64encode(to_bytes)
    base64message = base64bytes.decode('ascii')
    myheaders = {
        'Authorization': 'Basic {0}'.format(base64message)
    }
    mydata = {
        'grant_type': 'client_credentials'
    }
    resp = req.post(url, headers=myheaders, data=mydata)
    return resp


# returns the access token of the given response
def get_access_token(resp):
    resp_json = resp.json()
    accesstoken = resp_json['access_token']
    return accesstoken


# creates the headers for a simple API request
def get_headers(accesstoken):
    myheaders = {
        'Authorization': 'Bearer {0}'.format(accesstoken)
    }
    return myheaders


# returns the artist information
# search by artist name
def search_artists(name, accesstoken):
    baseurl = 'https://api.spotify.com/v1/search'
    query_name = str(name).replace(' ', '+')
    query = '?q={0}&type=artist'.format(query_name)
    my_headers = get_headers(accesstoken)
    url = baseurl + query
    resp = req.get(url, headers=my_headers)
    return resp.json()['artists']['items']


# returns the first-found artist information
# search by artist name
# NOTE: returns a json
def search_artist_first(name, accesstoken):
    baseurl = 'https://api.spotify.com/v1/search'
    query_name = str(name).replace(' ', '+')
    query = '?q={0}&type=artist'.format(query_name)
    my_headers = get_headers(accesstoken)
    url = baseurl + query
    resp = req.get(url, headers=my_headers)
    firstartistjson = resp.json()['artists']['items'][0]
    return firstartistjson


# param: artist object json format
# returns the artist ID
def get_artist_id(artist_json):
    artistid = artist_json['id']
    return artistid


# returns the artist followers count
def get_artist_followers_count(artist_json):
    followers_count = artist_json['followers']['total']
    return followers_count


def search_playlist(playlistname, accesstoken):
    baseurl = 'https://api.spotify.com/v1/search'
    query_name = str(playlistname).replace(' ', '+')
    query = '?q={0}&type=playlist'.format(query_name)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()['playlists']['items'][0]


# returns a list of tracks given a name
def search_tracks(name, accesstoken):
    baseurl = 'https://api.spotify.com/v1/search'
    query_name = str(name).replace(' ', '+')
    query = '?q={0}&type=track'.format(query_name)
    my_headers = get_headers(accesstoken)
    url = baseurl + query
    resp = req.get(url, headers=my_headers)
    return resp


# return the first matching track by name
def search_track_first(name, accesstoken):
    baseurl = 'https://api.spotify.com/v1/search'
    query_name = str(name).replace(' ', '+')
    query = '?q={0}&type=track'.format(query_name)
    my_headers = get_headers(accesstoken)
    url = baseurl + query
    resp = req.get(url, headers=my_headers)
    firsttrackjson = resp.json()['tracks']['items'][0]
    return firsttrackjson


# returns a list of the featured playlist in a given country
# NOTE: lang must be a string of two char respecting the ISO (eg. IT for Italy)
def get_featured_playlists(accesstoken, lang):
    baseurl = 'https://api.spotify.com/v1/browse/featured-playlists'
    query = '?limit=50&country={0}'.format(lang)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()

# returns a list of new featured album releases
# NOTE: lang must be a string of two char respecting the ISO (eg. IT for Italy)
def get_new_releases(lang, accesstoken):
    baseurl = 'https://api.spotify.com/v1/browse/new-releases'
    query ='?country={0}&limit=50'.format(lang)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp


# returns a list of the specified playlist's tracks
# NOTE: market must be a string of two char respecting the ISO (eg. IT for Italy)
def get_playlist_tracks(playlistid, market, accesstoken):
    baseurl = 'https://api.spotify.com/v1/playlists/{0}/tracks'.format(playlistid)
    query = '?limit=100&market={0}'.format(market)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


# returns the top tracks of an artist for a given market
# NOTE: market must be a string of two char respecting the ISO (eg. IT for Italy)
def get_artist_tops(artistid, market, accesstoken):
    baseurl = 'https://api.spotify.com/v1/artists/{0}/top-tracks'.format(artistid)
    query = '?market={0}'.format(market)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


def get_track_features(trackid, accesstoken):
    url = 'https://api.spotify.com/v1/audio-features/{0}'.format(trackid)
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


def get_tracks_features(commaseparatedtrackids, accesstoken):
    baseurl = 'https://api.spotify.com/v1/audio-features'
    query = '?ids={0}'.format(commaseparatedtrackids)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


def get_track_audio_analysis(trackid, accesstoken):
    url = 'https://api.spotify.com/v1/audio-analysis/{0}'.format(trackid)
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp


def get_artist_albums(artistid, lang, accesstoken):
    baseurl = 'https://api.spotify.com/v1/artists/{0}/albums'.format(artistid)
    query = '?include_groups=album&market={0}&limit=50'.format(lang)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers).json()
    return resp['items']


def get_album_tracks(albumid, lang, accesstoken):
    baseurl = 'https://api.spotify.com/v1/albums/{0}/tracks'.format(albumid)
    query = '?market={0}&limit=10'.format(lang)
    my_headers = get_headers(accesstoken)
    url = baseurl + query
    resp = req.get(url, headers=my_headers).json()
    return resp


def get_track(trackid, lang,  accesstoken):
    baseurl = 'https://api.spotify.com/v1/tracks/{0}'.format(trackid)
    query = '?market={0}'.format(lang)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


def get_album(albumid, lang, accesstoken):
    baseurl = 'https://api.spotify.com/v1/albums/{0}'.format(albumid)
    query = '?market={0}'.format(lang)
    url = baseurl + query
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()


# returns the index of the given element in the list, -1 if the element is not in the list
def indexOf(list_of_values, value):
    i = 0
    while i < len(list_of_values):
        if list_of_values[i] == value:
            return i
        i = i + 1
    return -1


def get_artist_related(artistid, accesstoken):
    url = 'https://api.spotify.com/v1/artists/{0}/related-artists'.format(artistid)
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()['artists']


def get_playlist_tracks_from_url(baseurl, lang, accesstoken):
    query = '?market={0}'.format(lang)
    url = baseurl + query
    resp = req.get(url, headers=get_headers(accesstoken))
    return resp.json()

def get_available_genres(accesstoken):
    url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
    my_headers = get_headers(accesstoken)
    resp = req.get(url, headers=my_headers)
    return resp.json()