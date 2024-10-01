import azure.functions as func
import logging
import requests
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="spotifyintegration")

#####################
# main spotify integration
#####################
def spotifyintegration(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the song name from the request
    song_name = req.params.get('song_name')
    logging.info('song_name:...' )
    if not song_name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            song_name = req_body.get('song_name')
    
    if not song_name:
        return func.HttpResponse(
            "Please pass a song name on the query string or in the request body",
            status_code=400
        )
    
    # Get Spotify token
    token = get_spotify_token()
    
    # Search for the song
    track = search_spotify_song(song_name, token)
    
    if track:
        preview_url = track.get('preview_url', None)
        if preview_url:
            return func.HttpResponse(f'Preview URL: {preview_url}', status_code=200)
        else:
            return func.HttpResponse(f'No preview available for "{song_name}".', status_code=404)
    else:
        return func.HttpResponse(f'Song "{song_name}" not found.', status_code=404)

#####################    
# Get a spotify token
#####################
def get_spotify_token():
    logging.info('Getting tokens...')
     
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    logging.info('Connecting...')

    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = requests.post(auth_url, headers=headers, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        logging.info(f"Request succeeded with status code {response.status_code}")
        # Parse the JSON response
        response_data = response.json()

        # Check if the response is a dictionary or list
        if isinstance(response_data, dict):
            # Iterate over dictionary items (key-value pairs)
            for key, value in response_data.items():
                logging.info(f"{key}: {value}")
        elif isinstance(response_data, list):
            # Iterate over list items
            for item in response_data:
                logging.info(item)
    else:
        logging.info(f"Request failed with status code {response.status_code}")
        logging.info(f"Request failed with reason {response.reason}")

    token_info = response.json()
    
    return token_info['access_token']

#####################
# search for the spotify song
#####################
def search_spotify_song(song_name, token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": song_name,
        "type": "track",
        "limit": 1  # Return only the top result
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code == 200:
        track_info = response.json()
        tracks = track_info['tracks']['items']
        if tracks:
            return tracks[0]  # Return the first matching track
    return None