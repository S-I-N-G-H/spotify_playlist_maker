

# Imports
import json
import requests
import urllib

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


scope = "playlist-modify-public user-library-read"
token = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def getArtists(spotify, name):
    names = []
    uris = []
    artists = spotify.search(q=name, limit=10, type='artist')
    for artist in artists['artists']['items']:
        names.append(artist['name'])
        uris.append(artist['uri'])
    return names, uris

def getTopTracks(spotify, uri):
    tracks = []
    trackUris = []
    results = spotify.artist_top_tracks(uri)
    # print(results)
    for track in results['tracks'][:10]:
        tracks.append(track['name'])
        trackUris.append(track['uri'])
    return tracks,trackUris

def makePlaylist(spotify, username, playlistName):
    alreadyMade = False
    playlists = spotify.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == playlistName:  
            alreadyMade = True
    if not alreadyMade:
        spotify.user_playlist_create(username, name=playlistName)

def getPlaylistID(spotify, username, playlistName):
    playlist_id = ''
    playlists = spotify.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == playlistName:  
            playlist_id = playlist['id']
    return playlist_id



# DASH
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

navbar = dbc.Navbar(
    children=[
        html.Span(
            # Use row and col to control vertical alignment of logo
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Spotify Playlist Maker", className="ml-2")),
                ],
                align="center",
                no_gutters=True,               
            ),         
        ),
        dbc.Nav([
                dbc.NavLink("Home", href="main"),
                dbc.NavLink("Artist Top 10", href="page-1"),
                dbc.NavLink("More", href="page-2"),
            ],
            pills=True,
            className="ml-auto"
        ) 
    ],
    color="lightgrey",
    dark=False,
    sticky="top",
    style={
        'border': '2px solid green',
        'outline': 'green',
        'border-radius': '10px',
        'color':'white',
    }
)


page_main_layout = html.Div([
    navbar,
    html.Div([
        html.H1(children='The easy way to put together Spotify playlists', style={'padding': '0px 10px' }),
        html.Br(),
        html.Div("  By Amardeep Singh"),
    ], style={
        'backgroundColor': 'green',
        'border-radius': '10px',
        'color': 'white',
        'padding': '30px'
    }),
    html.Div(id='page-main-content'),
])

page_1_layout = html.Div([
    navbar,
    html.Div([
        html.H1(children='Artist Top 10 Playlist', style={'padding': '0px 10px' }),
        
    ], style={
        'backgroundColor': 'green',
        'border-radius': '10px',
        'color': 'white',
        'padding': '30px'
    }),

    html.Div([
        html.Div([
            html.H2("Enter your Spotify username:"),
            dbc.Input(id="input-username", placeholder="username", type="text"),
            html.Br(),
            html.H2("Enter a new playlist or add to an existing:"),
            dbc.Input(id="input-playlist-name", placeholder="playlist", type="text"),
            html.Br(),
            html.H2("Search for an artist:"),
            dbc.Input(id="input-artist", placeholder="artist", type="text"),
            html.Br(),
            html.H3("Artist Picked"),
            html.Br(),
            html.Div(id="output-artist"),
            html.Br(),
            html.H3("Top 10 Tracks"),
            html.Br(),
            html.Div(id="output-tracks"),
            html.Br(),
            dbc.Button("Make Playlist", id = "button-playlist",color="white", block=True, size="lg", outline=True),
            html.Br(),
            html.Div(id="output-made"),
        ], style={
            'padding': '30px',
        }),


    ], style={
        'backgroundColor': 'grey',
        'border-radius': '10px',
        'color': 'white',
        'padding': '5px',
        'border': '2px solid green',
    }),




    html.Div("by Amardeep Singh", style={'float': 'right'}),
    html.Div(id='page-1-content')
])


page_2_layout = html.Div([
    navbar,
    html.Div([
        html.H1(children='More Coming Soon', style={'padding': '0px 10px' }),
        
    ], style={
        'backgroundColor': 'green',
        'border-radius': '10px',
        'color': 'white',
        'padding': '30px'
    }),
    html.Div("by Amardeep Singh", style={'float': 'right'}),
    html.Div(id='page-2-content')
])






#DASH CALLBACKS
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/main':
        return page_main_layout
    else:
        return page_main_layout


@app.callback(Output("output-artist", "children"), 
[Input("input-artist", "value")])
def output_text_artist(value):
    if value == None or value == "":
        return "no artist found"
    names, uris = getArtists(sp, value)
    if names == None:
        return "no artist found"
    return names[0]

@app.callback(Output("output-tracks", "children"), 
[Input("input-artist", "value")])
def output_text_tracks(value):
    if value == None or value == "":
        return "no tracks found"
    names, uris = getArtists(sp, value)
    if names == None:
        return "no tracks found"
    tracks,trackUris = getTopTracks(sp, uris[0])
    songs=[]
    for track in tracks:
        songs.append(track)
        songs.append(html.Br())
    return  songs


@app.callback(
    Output("output-made", "children"), 
    [Input("button-playlist", "n_clicks"),
    Input("input-username", "value"),
    Input("input-playlist-name", "value")],
    [State('input-artist', 'value')]
)
def on_button_click(n, username, playlistName, artist):
    if n is None:
        return "no playlist made"
    else:
        if artist == None or artist == "":
            return "no tracks found"
        names, uris = getArtists(sp, artist)
        if names == None:
            return "no tracks found"
        tracks,trackUris = getTopTracks(sp, uris[0])

        makePlaylist(token, username, playlistName)
        playlistID = getPlaylistID(token, username, playlistName)
        token.user_playlist_add_tracks(username, playlistID, trackUris)



        return f"Playlist made {n} times."




# run the dash on servers
if __name__ == '__main__':
    #app.run_server(debug=True)
    app.server.run(debug=True, port=8050, host='127.0.0.1')

#127.0.0.1 for local machine 
#0.0.0.0 for AWS machine 
