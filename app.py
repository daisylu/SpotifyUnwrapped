# external libraries
import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, session, make_response, session, redirect
import requests
import spotipy
import spotipy.util as util

# internal modules
from spotify_unwrapped.lyrics import GeniusLyrics
from spotify_unwrapped.top_tracks import TopTracksInfo

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SPOTIFY_CLIENT_SECRET"]

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/lyrics", methods=["GET", "POST"])
# def generate_lyrics():
#     if request.method == "POST":
#         # user submitted from site
#         inputs = {k: v for k, v in request.form.items()}

#         # get lyrics
#         g = GeniusLyrics(token = os.environ["GENIUS_CLIENT_ACCESS_TOKEN"])
#         output = g.get_song_lyrics(**inputs)

#         print(output)

#     else:
#         output = "" 

#     return render_template("lyrics.html", output = output)

if os.environ["ENVIRONMENT"] == "dev":
    APP_HOST = "127.0.0.1:5000"
    SHOW_DIALOG = True
else:
    APP_HOST = "spotifyunwrapped.heroku.com"
    SHOW_DIALOG = False
    
API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = f"http://{APP_HOST}/api_callback"
SCOPE = 'user-top-read'
CLI_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLI_SEC = os.environ["SPOTIFY_CLIENT_SECRET"]

@app.route("/")
def verify():
    auth_url = f"{API_BASE}/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}"
    return redirect(auth_url)

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/api_callback")
def api_callback():
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"http://{APP_HOST}/api_callback",
        "client_id": CLI_ID,
        "client_secret": CLI_SEC
        })

    res_body = res.json()
    print(res.json())
    session["token"] = res_body.get("access_token")

    return redirect("index")


@app.route("/go", methods=["POST"])
def go():
    t = TopTracksInfo(session["token"], request.form)
    results_html = t.get_top_tracks_info()
    
    return render_template("results.html", data=request.form, output=results_html)

if __name__ == "__main__":
    app.run(debug=True)